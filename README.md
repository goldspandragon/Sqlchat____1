# SqlChat

Bienvenido a SQLchat, un servicio no oficial soportado por flask, SQLite y grooq, archivo asociado a manual de pseudo instrucciones para el progreso en el mismo

-
Primero(Importante generar llave api groq): Ir a la pagina de groq y generar tu Api Key (Es secreta)
-

* En Windows:


1.-Entrar a la powershell
----------------------------------------------------------------
	Crear flask
	1.1.- pip install flask
----------------------------------------------------------------
2.-Acceder al directorio de la carpeta del proyecto
----------------------------------------------------------------
	En la powerShell es con Cd: y la dirrecion de la carpeta
----------------------------------------------------------------
3.-Activar el entorno virtual
----------------------------------------------------------------
	En caso de que no este creado Venv:
	3.1.-python -m venv venv
	3.2.-Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
-----------------------------------------------------------------
4.-Ejecutar el proyecto
----------------------------------------------------------------
	En la powershell una vez con todo instalado y el entorno activado:
	Python app.py
-----------------------------------------------------------------


Características:
	
En la carpeta Databases: están los archivos db que se cargan a la pagina(dentro de la misma se puede agregar y eliminar)
Carpeta Static: se encuentra los estilos css
Templates: todos los .HTML para modificar 
app: archivo Python, almacena lógica detrás de la IA
data: archivo db que almacena datos de la pagina y de sesión o variables a travez de sqllite 
user: arvhico db que guarda usuarios

1.- Inicio

Para empezar en el funcionamiento necesitas iniciar Sesión con tus credenciales.
Tu sesión sesión estará asociada a datos que se reflejaran en la pagina y como se referirá la Ia hacia ti.

2.- Fase de exploración

En la pagina existen 3 apartados clave:
*Subir Archivo:
	Para este lado te permite cargar un archivo .db para empezar la conversación 

*Comenzar Conversación:
	Para este punto esta el Chat en profundidad y el chat analítico para tus consultas db

*Historial:
	En este apartado puedes ver todo lo que haz conversado con la Ia tanto como analítica como la de consultas, podras observarlas por errores, exitosas y por categoría(Las consultas se guardan en contenedores según su categoría siendo el archivo en si)

3.- Funcionamiento

*Chat Analítico:
	Chat analítico puedes pedirlo consultas informales por texto y la Ia te enviara la consulta lista por chat junto con un análisis que es en relación al resto de datos y de la misma base es importante que para que devuelva una consulta exitosa es consultar bien por nombres y columnas, es decir, si la columna se llama "Clientes" es necesario no desviarse de su nombre original para tener éxito.

*Chat en Profundidad:
	El nombre no representa nada a nivel técnico pero el chat en profundidad te dejara hablar con la Ia de grooq de manera libre pero solo en relación a la base de datos que este seleccionada, de todas formas puedes hablarle de lo que quieras pero el objetivo es que hables de la base actual cargada en cuestión, esta puede darte opiniones y resúmenes clave para darte un encuentro mas cercano a la base de datos, para que asi, al momento de hacer consultas no fallen.
