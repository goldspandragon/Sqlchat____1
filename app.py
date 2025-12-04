import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
import re
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# Función now() para timestamps en Jinja
app.jinja_env.globals.update(now=lambda: datetime.now())


# ============================================================
# 🔹 CONFIG MULTI-BASES
# ============================================================

DATABASE_FOLDER = "databases"
os.makedirs(DATABASE_FOLDER, exist_ok=True)


def listar_bases():
    """Devuelve la lista de archivos .db en la carpeta databases."""
    return [b for b in os.listdir(DATABASE_FOLDER) if b.endswith(".db")]


def get_selected_db_path():
    """Devuelve la ruta absoluta de la base seleccionada en sesión."""
    db = session.get("selected_db")
    if not db:
        return None
    return os.path.join(DATABASE_FOLDER, db)


def get_data_db():
    """Devuelve conexión sqlite a la base seleccionada, o None si no hay."""
    ruta = get_selected_db_path()
    if ruta and os.path.exists(ruta):
        conn = sqlite3.connect(ruta)
        conn.row_factory = sqlite3.Row
        return conn
    return None


# ============================================================
# 🔹 BASE DE USUARIOS + CHAT PROFUNDO
# ============================================================

USER_DB = "users.db"
GROQ_API_KEY = ""   # ⚠️ reemplaza aquí con tu API Key de Groq #----------------------------
GROQ_MODEL = "llama-3.1-8b-instant"


def init_user_db():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()

    # Tabla usuarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # Tabla historial profundo
    c.execute("""
        CREATE TABLE IF NOT EXISTS deep_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            database TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabla para consultas SQL rápidas
    c.execute("""
        CREATE TABLE IF NOT EXISTS sql_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            database TEXT NOT NULL,
            pregunta TEXT NOT NULL,
            sql TEXT NOT NULL,
            resultado TEXT,
            analisis TEXT,
            exito BOOLEAN NOT NULL,
            categoria TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


init_user_db()


def get_user_db():
    conn = sqlite3.connect(USER_DB)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# 🔹 OBTENER ESQUEMA
# ============================================================

def obtener_esquema():
    conn = get_data_db()
    if not conn:
        return "No hay base seleccionada.", []

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [t[0] for t in cursor.fetchall()]
    esquema = ""

    if not tablas:
        conn.close()
        return "La base no contiene tablas.", []

    for tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla});")
        columnas = [c[1] for c in cursor.fetchall()]
        esquema += f"Tabla: {tabla}\nColumnas: {', '.join(columnas)}\n\n"

    conn.close()
    return esquema, tablas


def generar_mapeo_sinonimos():
    """Genera un diccionario de sinónimos comunes para campos de BD."""
    return {
        "cliente": ["customers", "usuarios", "accounts", "clientes", "personas"],
        "nombre": ["name", "nombre", "nombre_completo", "full_name", "apellido", "titulo"],
        "edad": ["age", "edad", "fecha_nacimiento", "birth_date", "años"],
        "teléfono": ["phone", "telefono", "movil", "celular", "telephone", "tel"],
        "correo": ["email", "correo", "email_address", "mail", "e_mail"],
        "dirección": ["address", "direccion", "ubicacion", "location", "domicilio"],
        "id": ["id", "codigo", "pk", "identificador", "numero", "account_id", "user_id", "customer_id"],
        "fecha": ["date", "fecha", "created_at", "updated_at", "timestamp", "fecha_creacion"],
        "monto": ["amount", "monto", "total", "valor", "price", "precio", "suma"],
        "descripción": ["description", "descripcion", "detalle", "comentarios", "observaciones"],
        "estado": ["status", "estado", "condicion", "situacion"],
        "activo": ["active", "activo", "habilitado", "enabled", "is_active"],
        "producto": ["product", "producto", "item", "articulo", "commodity"],
        "categoría": ["category", "categoria", "tipo", "type", "clasificacion"],
        "ciudad": ["city", "ciudad", "municipio", "localidad"],
        "país": ["country", "pais", "nacion"],
        "empresa": ["company", "empresa", "organizacion", "negocio"],
        "departamento": ["department", "departamento", "seccion", "area"],
        "salario": ["salary", "salario", "sueldo", "pago", "wage"],
        "cantidad": ["quantity", "cantidad", "numero_items", "count", "numero"],
    }


# ============================================================
# 🔹 LOGIN / REGISTER
# ============================================================

def validar_contraseña(contraseña):
    """
    Valida que la contraseña cumpla con los requisitos de seguridad:
    - Mínimo 8 caracteres
    - Al menos un número
    - Al menos un carácter especial (!@#$%^&*)
    - Al menos una mayúscula
    Devuelve: (es_válida, mensaje_error)
    """
    if len(contraseña) < 8:
        return False, "La contraseña debe tener mínimo 8 caracteres."
    
    if not re.search(r'\d', contraseña):
        return False, "La contraseña debe contener al menos un número (0-9)."
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', contraseña):
        return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&* etc)."
    
    if not re.search(r'[A-Z]', contraseña):
        return False, "La contraseña debe contener al menos una mayúscula."
    
    return True, ""


def hash_password(contraseña):
    """Genera un hash SHA-256 de la contraseña."""
    return hashlib.sha256(contraseña.encode()).hexdigest()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        # Validaciones
        if not username:
            flash("❌ El usuario no puede estar vacío.", "login")
            return render_template("login.html")
        
        if len(username) < 3:
            flash("❌ El usuario debe tener mínimo 3 caracteres.", "login")
            return render_template("login.html")

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            flash("❌ Las contraseñas no coinciden.", "login")
            return render_template("login.html")

        # Validar seguridad de la contraseña
        es_válida, mensaje = validar_contraseña(password)
        if not es_válida:
            flash(f"❌ {mensaje}", "login")
            return render_template("login.html")

        conn = get_user_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user:
            flash("❌ El usuario ya existe.", "login")
        else:
            # Guardar contraseña hasheada
            password_hash = hash_password(password)
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            flash("✅ Registro exitoso. Ahora puedes iniciar sesión.", "login")
            conn.close()
            return redirect(url_for("login"))

        conn.close()

    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_user_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if user:
            # Comparar contraseña hasheada
            password_hash = hash_password(password)
            if user["password"] == password_hash:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash("✅ Sesión iniciada correctamente.", "login")
                return redirect(url_for("index"))
        
        flash("❌ Usuario o contraseña incorrectos.", "login")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("🔒 Sesión cerrada.")
    return redirect(url_for("login"))


# ============================================================
# 🔹 SUBIR SQL Y LISTADO / SELECCIÓN / ELIMINACIÓN DE BASES
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():
    user = session.get("username")
    historial = session.get("historial", [])

    if not user:
        return render_template("index.html", user=None, historial=None)

    # Subida de archivo .sql
    if request.method == "POST":
        archivo = request.files.get("file")

        if archivo and archivo.filename.endswith(".sql"):
            nombre = archivo.filename.replace(".sql", "")
            ruta_sql = os.path.join(DATABASE_FOLDER, nombre + ".sql")
            ruta_db = os.path.join(DATABASE_FOLDER, nombre + ".db")

            archivo.save(ruta_sql)

            try:
                conn = sqlite3.connect(ruta_db)
                cur = conn.cursor()
                cur.executescript(open(ruta_sql, "r", encoding="utf-8").read())
                conn.commit()
                conn.close()

                session["selected_db"] = nombre + ".db"
                flash(f"📂 Base '{nombre}' cargada correctamente.")

            except Exception as e:
                flash(f"❌ Error procesando SQL: {e}")

        return redirect(url_for("index"))

    return render_template(
        "index.html",
        user=user,
        historial=historial,
        lista_bases=listar_bases(),
        selected_db=session.get("selected_db")
    )


# 👉 NUEVA RUTA: seleccionar base
@app.route("/seleccionar_base", methods=["POST"])
def seleccionar_base():
    db = request.form.get("database")
    if not db:
        flash("❌ No se recibió ninguna base para seleccionar.")
        return redirect(url_for("index"))

    session["selected_db"] = db
    flash(f"📌 Base activa: {db}")
    return redirect(url_for("index"))


# 👉 NUEVA RUTA: eliminar base (.db y su .sql si existe)
@app.route("/eliminar_base", methods=["POST"])
def eliminar_base():
    db = request.form.get("database")
    if not db:
        flash("❌ No se recibió ninguna base para eliminar.")
        return redirect(url_for("index"))

    ruta_db = os.path.join(DATABASE_FOLDER, db)
    ruta_sql = os.path.join(DATABASE_FOLDER, db.replace(".db", ".sql"))

    try:
        if os.path.exists(ruta_db):
            os.remove(ruta_db)
        if os.path.exists(ruta_sql):
            os.remove(ruta_sql)

        # Si la base eliminada estaba seleccionada, la limpiamos de sesión
        if session.get("selected_db") == db:
            session["selected_db"] = None

        flash(f"🗑️ Base '{db}' eliminada correctamente.")
    except Exception as e:
        flash(f"❌ Error al eliminar base: {e}")

    return redirect(url_for("index"))

# ============================================================
# 🔹 Historial
# ============================================================

@app.route("/historial")
def historial_page():
    if "username" not in session:
        return redirect(url_for("login"))

    usuario = session.get("username")
    bases = listar_bases()
    
    # Obtener historial de consultas agrupado por base de datos
    conn = get_user_db()
    consultas_por_base = {}
    
    # Obtener todas las consultas del usuario de la tabla deep_history
    historial_db = conn.execute(
        """SELECT database, role, message, timestamp FROM deep_history 
           WHERE user = ? ORDER BY database, timestamp DESC""",
        (usuario,)
    ).fetchall()
    
    # Agrupar consultas por base de datos
    for item in historial_db:
        db = item["database"]
        if db not in consultas_por_base:
            consultas_por_base[db] = []
        consultas_por_base[db].append({
            "role": item["role"],
            "message": item["message"],
            "timestamp": item["timestamp"]
        })
    
    # Obtener historial sesión (consultas SQL rápidas) - AHORA DE LA BASE DE DATOS
    historial_sesion = []
    sql_queries = conn.execute(
        """SELECT database, pregunta, sql, resultado, analisis, exito, categoria, timestamp 
           FROM sql_queries 
           WHERE user = ? 
           ORDER BY timestamp DESC""",
        (usuario,)
    ).fetchall()
    
    for item in sql_queries:
        # Convertir resultado de JSON string a lista
        try:
            resultado = json.loads(item["resultado"]) if item["resultado"] else []
        except:
            resultado = []
        
        historial_sesion.append({
            "pregunta": item["pregunta"],
            "sql": item["sql"],
            "resultado": resultado,
            "analisis": item["analisis"],
            "exito": item["exito"],
            "categoria": item["categoria"],
            "database": item["database"]
        })
    
    conn.close()

    return render_template(
        "historial.html", 
        historial_sesion=historial_sesion, 
        consultas_por_base=consultas_por_base,
        bases=bases
    )


# ============================================================
# 🔹 CONSULTAS SQL + ANÁLISIS IA
# ============================================================

@app.route("/preguntar", methods=["POST"])
def preguntar():
    user = session.get("username")
    
    if session.get("selected_db") is None:
        raise ValueError("No hay base seleccionada. Selecciona una antes de consultar.")

    if not user:
        flash("Debes iniciar sesión.")
        return render_template("index.html", user=None)

    pregunta = request.form.get("pregunta")
    historial = session.get("historial", [])

    try:
        esquema_texto, tablas = obtener_esquema()
        if not tablas:
            raise ValueError("No hay tablas en la base seleccionada.")

        # === Paso 1: Generación de SQL ===
        mapeo_sinonimos = generar_mapeo_sinonimos()
        
        # Formatear el mapeo de sinónimos para el prompt
        sinonimos_formateado = "\n".join([
            f"  - \"{clave}\": {', '.join(valores)}"
            for clave, valores in mapeo_sinonimos.items()
        ])
        
        system_msg_sql = f"""Eres un generador experto en SQL para SQLite especializado en interpretar sinónimos naturales.
Tu tarea es convertir preguntas en lenguaje natural a SQL válido y exacto.

BASE DE DATOS ACTUAL:
{esquema_texto}

DICCIONARIO DE SINÓNIMOS (usa como referencia para mapear términos):
{sinonimos_formateado}

REGLAS CRÍTICAS - LEE CUIDADOSAMENTE:
1. Devuelve SOLO código SQL válido. NO expliques nada más. Sin comentarios.
2. NO uses alias (AS) NUNCA BAJO NINGUNA CIRCUNSTANCIA a menos que sea absolutamente necesario para JOIN de la misma tabla.
3. Los nombres de COLUMNAS y TABLAS deben coincidir EXACTAMENTE con el esquema proporcionado.
4. Interpreta sinónimos: si el usuario dice "edad" y en el esquema hay "fecha_nacimiento", usa "fecha_nacimiento".
5. Si no puedes encontrar una columna exacta para un sinónimo, busca palabras parciales (LIKE) en el contexto.
6. NO inventes columnas ni tablas. Si no existen, devuelve error claro pero en SQL.
7. Prioriza exactitud sobre inteligencia: es mejor "no encontrado" que una columna errónea.
8. En ambigüedad, elige la opción más general o la primera coincidencia.

EJEMPLOS DE LO QUE HACER:
✓ Pregunta: "¿Cuántos clientes tenemos?" + Esquema con tabla "customers"
  Respuesta: SELECT COUNT(*) FROM customers;

✓ Pregunta: "Mostrar nombre de clientes" + Esquema: tabla "usuarios" con "nombre_completo"
  Respuesta: SELECT nombre_completo FROM usuarios;

✓ Pregunta: "Listar teléfonos" + Esquema: tabla "contactos" con "telefono"
  Respuesta: SELECT telefono FROM contactos;

EJEMPLOS DE LO QUE EVITAR:
✗ SELECT COUNT(*) AS total FROM customers;  (sin AS)
✗ SELECT fecha AS f FROM eventos;  (sin AS)
✗ SELECT invalid_column FROM usuarios;  (columna no existe)
✗ SELECT * FROM tabla_inexistente;  (tabla no existe)

IMPORTANTE: La precisión es más importante que la inteligencia. Si dudes, devuelve solo lo que SABES que existe."""


        payload_sql = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_msg_sql},
                {"role": "user", "content": pregunta},
            ],
        }

        response_sql = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json=payload_sql
        ).json()

        # Validación mínima por seguridad
        if (
            not response_sql
            or "choices" not in response_sql
            or len(response_sql["choices"]) == 0
            or "message" not in response_sql["choices"][0]
            or "content" not in response_sql["choices"][0]["message"]
        ):
            raise ValueError(f"Groq no devolvió una respuesta válida (SQL). Respuesta: {response_sql}")

        raw_sql = response_sql["choices"][0]["message"]["content"]

        # limpiar cualquier cosa que no sea SQL
        sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()

        # si la IA escribió texto antes de SQL → eliminarlo
        multiples = sql_query.split(";")
        if len(multiples) > 1:
            # filtra solo líneas que contengan palabras SQL
            candidates = [
                line.strip()
                for line in multiples
                if any(x in line.upper() for x in ["SELECT", "UPDATE", "INSERT", "DELETE", "WITH", "CREATE"] )
            ]
            if len(candidates) > 0:
                sql_query = candidates[0] + ";"

        # === Ejecutar SQL ===
        conn = get_data_db()
        if not conn:
            raise ValueError("No hay base de datos activa. Selecciona o carga una base.")

        cur = conn.cursor()
        cur.execute(sql_query)
        resultados = [list(row) for row in cur.fetchall()]
        columnas = [c[0] for c in cur.description] if cur.description else []
        conn.close()

        # === Paso 2: Análisis IA DESPUÉS del SQL ===
        system_msg_analisis = """
        Eres un científico de datos senior especializado en análisis multidimensional con foco en bases relacionales.
        Tu trabajo es analizar los resultados SQL con un nivel profesional alto.

        REQUISITOS DEL ANÁLISIS:
        1. Haz interpretaciones profundas sobre patrones, correlaciones, tendencias y comportamientos de los datos.
        2. Compara valores entre columnas o entre filas relevantes cuando corresponda.
        3. Menciona insights que puedan ser útiles para decisiones estratégicas.
        4. Si la tabla contiene métricas numéricas, resalta máximos, mínimos, promedios o outliers.
        5. SIEMPRE relaciona tu análisis con el contexto del documento SQL seleccionado.
        6. No repitas el SQL ejecutado ni inventes datos fuera de los resultados entregados.
        7. Mantén el análisis profesional, claro, directo y sin relleno.

        Formato final:
        – Explica entre 4 y 7 líneas.
        – No uses lenguaje genérico.
        """


        payload_analysis = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_msg_analisis},
                {"role": "user",
                 "content": f"La pregunta fue: {pregunta}\nResultados: {resultados}"}
            ],
        }

        response_analysis = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json=payload_analysis
        ).json()

        if (
            not response_analysis
            or "choices" not in response_analysis
            or len(response_analysis["choices"]) == 0
            or "message" not in response_analysis["choices"][0]
            or "content" not in response_analysis["choices"][0]["message"]
        ):
            analisis = "⚠️ No se pudo generar análisis debido a un error en la respuesta de la IA."
        else:
            analisis = response_analysis["choices"][0]["message"]["content"].strip()

        # Guardar historial (lo que se ve en el chat)
        # Determinar categoría basada en el tipo de consulta
        sql_lower = sql_query.lower()
        if 'insert' in sql_lower:
            categoria = 'Inserción de Datos'
        elif 'update' in sql_lower:
            categoria = 'Actualización de Datos'
        elif 'delete' in sql_lower:
            categoria = 'Eliminación de Datos'
        elif 'count' in sql_lower or 'avg' in sql_lower or 'sum' in sql_lower or 'max' in sql_lower or 'min' in sql_lower:
            categoria = 'Agregaciones'
        elif 'join' in sql_lower:
            categoria = 'Consultas con JOIN'
        elif 'group by' in sql_lower:
            categoria = 'Agrupamientos'
        elif 'order by' in sql_lower:
            categoria = 'Ordenamientos'
        else:
            categoria = 'Consultas Generales'
        
        db_actual = session.get("selected_db")
        
        registro_consulta = {
            "pregunta": pregunta,
            "sql": sql_query,
            "resultado": resultados[:5],
            "analisis": analisis,
            "exito": True,
            "categoria": categoria,
            "database": db_actual
        }
        
        historial.append(registro_consulta)
        session["historial"] = historial
        
        # Guardar en base de datos
        if db_actual:
            user_db = get_user_db()
            user_db.execute(
                """INSERT INTO sql_queries 
                   (user, database, pregunta, sql, resultado, analisis, exito, categoria)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user, db_actual, pregunta, sql_query, json.dumps(resultados[:5]), analisis, True, categoria)
            )
            user_db.commit()
            user_db.close()
        flash("✅ Consulta ejecutada correctamente.")

        return redirect(url_for("index"))

    except Exception as e:
        db_actual = session.get("selected_db")
        
        registro_error = {
            "pregunta": pregunta,
            "sql": "(error)",
            "resultado": str(e),
            "analisis": "No disponible por error.",
            "exito": False,
            "categoria": "Error",
            "database": db_actual
        }
        
        historial.insert(0, registro_error)
        session["historial"] = historial

        # Guardar error en base de datos
        if db_actual:
            user_db = get_user_db()
            user_db.execute(
                """INSERT INTO sql_queries 
                   (user, database, pregunta, sql, resultado, analisis, exito, categoria)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user, db_actual, pregunta, "(error)", str(e), "No disponible por error.", False, "Error")
            )
            user_db.commit()
            user_db.close()

        flash(f"❌ Error: {e}")
        return redirect(url_for("index"))


# ============================================================
# 🔹 CHAT PROFUNDO (placeholder)
# ============================================================

@app.route("/chat_profundo")
def chat_profundo():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_user_db()
    mensajes = conn.execute(
        "SELECT role, message, timestamp FROM deep_history WHERE user = ? AND database = ? ORDER BY id ASC",
        (session["username"], session.get("selected_db", "ninguna"))
    ).fetchall()
    conn.close()

    return render_template("chat_profundo.html", mensajes=mensajes)

@app.route("/chat_profundo_enviar", methods=["POST"])
def chat_profundo_enviar():
    if "username" not in session:
        return redirect(url_for("login"))

    texto_usuario = request.form.get("mensaje", "").strip()
    if not texto_usuario:
        flash("Debes escribir un mensaje.", "chatp")
        return redirect(url_for("chat_profundo"))

    usuario = session["username"]
    base = session.get("selected_db", "ninguna")

    # ⬇Guardar mensaje del usuario
    conn = get_user_db()
    conn.execute("""
        INSERT INTO deep_history (user, database, role, message)
        VALUES (?, ?, ?, ?)
    """, (usuario, base, "user", texto_usuario))
    conn.commit()
    conn.close()

    # ⬇️ Obtener esquema de la BD actual
    esquema_texto, tablas = obtener_esquema()
    
    # ⬇️ Preparar historial para mandar a la IA
    conn = get_user_db()
    historial = conn.execute(
        "SELECT role, message FROM deep_history WHERE user = ? AND database = ? ORDER BY id ASC",
        (usuario, base)
    ).fetchall()
    conn.close()

    mensajes_formateados = [{"role": m["role"], "content": m["message"]} for m in historial]

    # ⬇️ Crear sistema prompt con contexto de la BD
    system_prompt = f"""Eres un asistente experto en bases de datos SQL. Tienes acceso a la siguiente base de datos actualmente cargada: '{base}'

Esquema de la base de datos:
{esquema_texto}

INSTRUCCIONES IMPORTANTES:
1. Responde siempre en contexto de la base de datos actual: {base}
2. Usa EXACTAMENTE los nombres de columnas y tablas de la base.
3. NO uses alias (AS) en consultas a menos que sea absolutamente necesario.
4. Si el usuario pregunta algo relacionado con la BD, proporciona consultas SQL exactas.
5. Si pregunta algo que NO está en la BD, comunícalo claramente.
6. Mantén un tono profesional y preciso.
7. En cada respuesta, contextualiza tu análisis con los datos reales de '{base}'
8. IMPORTANTE: Cuando menciones múltiples campos clave o puntos importantes, enuméralos así:
   
   1.- Primer punto importante
   2.- Segundo punto importante
   3.- Tercer punto importante
   
9. Usa tabulación y enumeración clara para destacar información importante."""

    # ⬇️ Llamado a la IA GROQ
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt}
        ] + mensajes_formateados
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json=payload
        ).json()

        respuesta_ia = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        respuesta_ia = f"Error al contactar la IA: {e}"

    # ⬇️ Guardar respuesta de la IA
    conn = get_user_db()
    conn.execute("""
        INSERT INTO deep_history (user, database, role, message)
        VALUES (?, ?, ?, ?)
    """, (usuario, base, "assistant", respuesta_ia))
    conn.commit()
    conn.close()

    return redirect(url_for("chat_profundo"))


# ============================================================
# 🔹 Limpiar Historial
# ============================================================

@app.route("/limpiar_chat", methods=["POST"])
def limpiar_chat():
    """Elimina todo el historial de chat profundo del usuario"""
    if "username" not in session:
        return {"success": False, "error": "No autenticado"}, 401
    
    usuario = session.get("username")
    try:
        conn = get_user_db()
        conn.execute("DELETE FROM deep_history WHERE user = ?", (usuario,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.route("/limpiar_consultas", methods=["POST"])
def limpiar_consultas():
    """Elimina todas las consultas SQL registradas del usuario"""
    if "username" not in session:
        return {"success": False, "error": "No autenticado"}, 401
    
    usuario = session.get("username")
    try:
        conn = get_user_db()
        conn.execute("DELETE FROM sql_queries WHERE user = ?", (usuario,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)