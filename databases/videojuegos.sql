-- =====================================
--   SUPER DATABASE DE VIDEOJUEGOS
-- =====================================

-- 🔥 LIMPIEZAS
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS platforms;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS game_platform;
DROP TABLE IF EXISTS game_genre;
DROP TABLE IF EXISTS dlcs;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS user_achievements;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS rarities;
DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS game_stats;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS event_participation;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS servers;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS matchmaking;
DROP TABLE IF EXISTS quests;
DROP TABLE IF EXISTS user_quests;
DROP TABLE IF EXISTS leaderboard;

-- 👤 USUARIOS
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    country TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 🎮 JUEGOS
CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    release_year INTEGER,
    developer TEXT,
    rating REAL
);

-- 🖥 PLATAFORMAS
CREATE TABLE platforms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- 🔌 RELACIÓN JUEGO-PLATAFORMA
CREATE TABLE game_platform (
    game_id INTEGER,
    platform_id INTEGER,
    PRIMARY KEY(game_id, platform_id),
    FOREIGN KEY(game_id) REFERENCES games(id),
    FOREIGN KEY(platform_id) REFERENCES platforms(id)
);

-- 🎵 GÉNEROS
CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE game_genre (
    game_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY(game_id, genre_id),
    FOREIGN KEY(game_id) REFERENCES games(id),
    FOREIGN KEY(genre_id) REFERENCES genres(id)
);

-- 🧩 DLCs
CREATE TABLE dlcs (
    id INTEGER PRIMARY KEY,
    game_id INTEGER,
    name TEXT,
    price REAL,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ⭐ LOGROS
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY,
    game_id INTEGER,
    name TEXT,
    description TEXT,
    points INTEGER,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

CREATE TABLE user_achievements (
    user_id INTEGER,
    achievement_id INTEGER,
    unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, achievement_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(achievement_id) REFERENCES achievements(id)
);

-- 🛒 COMPRAS & MICROTRANSACCIONES
CREATE TABLE purchases (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    game_id INTEGER,
    dlc_id INTEGER,
    amount REAL,
    purchased_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(game_id) REFERENCES games(id),
    FOREIGN KEY(dlc_id) REFERENCES dlcs(id)
);

-- 🧱 RAREZAS
CREATE TABLE rarities (
    id INTEGER PRIMARY KEY,
    name TEXT,
    drop_rate REAL
);

-- 🎁 ITEMS
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT,
    rarity_id INTEGER,
    value INTEGER,
    FOREIGN KEY(rarity_id) REFERENCES rarities(id)
);

-- 🎒 INVENTARIO DEL JUGADOR
CREATE TABLE inventory (
    user_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY(user_id, item_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);

-- 👥 SISTEMA DE AMIGOS
CREATE TABLE friends (
    user_id INTEGER,
    friend_id INTEGER,
    status TEXT,
    PRIMARY KEY(user_id, friend_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(friend_id) REFERENCES users(id)
);

-- 💬 MENSAJERÍA
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER,
    receiver_id INTEGER,
    message TEXT,
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
);

-- ⭐ REVIEWS DE JUEGOS
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    game_id INTEGER,
    rating INTEGER,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- 📊 ESTADÍSTICAS DEL JUEGO
CREATE TABLE game_stats (
    user_id INTEGER,
    game_id INTEGER,
    hours_played REAL,
    level INTEGER,
    progress REAL,
    PRIMARY KEY(user_id, game_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- 🎉 EVENTOS
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    start_date TEXT,
    end_date TEXT
);

CREATE TABLE event_participation (
    event_id INTEGER,
    user_id INTEGER,
    score INTEGER,
    PRIMARY KEY(event_id, user_id),
    FOREIGN KEY(event_id) REFERENCES events(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 🔔 NOTIFICACIONES
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    content TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 🌍 SERVIDORES MULTIJUGADOR
CREATE TABLE servers (
    id INTEGER PRIMARY KEY,
    region TEXT,
    max_players INTEGER
);

-- 🕹 PARTIDAS
CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    server_id INTEGER,
    winner_id INTEGER,
    duration INTEGER,
    played_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(server_id) REFERENCES servers(id),
    FOREIGN KEY(winner_id) REFERENCES users(id)
);

-- ⚖ SISTEMA DE MATCHMAKING
CREATE TABLE matchmaking (
    user_id INTEGER,
    rank INTEGER,
    mmr INTEGER,
    PRIMARY KEY(user_id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 🗺 QUESTS / MISIONES
CREATE TABLE quests (
    id INTEGER PRIMARY KEY,
    game_id INTEGER,
    name TEXT,
    reward_item INTEGER,
    FOREIGN KEY(game_id) REFERENCES games(id),
    FOREIGN KEY(reward_item) REFERENCES items(id)
);

CREATE TABLE user_quests (
    user_id INTEGER,
    quest_id INTEGER,
    is_completed INTEGER,
    PRIMARY KEY(user_id, quest_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(quest_id) REFERENCES quests(id)
);

-- 🏆 LEADERBOARD
CREATE TABLE leaderboard (
    user_id INTEGER,
    game_id INTEGER,
    score INTEGER,
    PRIMARY KEY(user_id, game_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ===================================
--   INSERTS DE PRUEBA
-- ===================================

INSERT INTO users (username, email, password, country) VALUES
 ("gamer1", "gamer1@mail.com", "1234", "Chile"),
 ("dragonSlayer", "slayer@mail.com", "1234", "México"),
 ("shadowFox", "fox@mail.com", "abcd", "Argentina");

INSERT INTO platforms (name) VALUES
 ("PC"), ("PlayStation"), ("Xbox"), ("Nintendo Switch");

INSERT INTO genres (name) VALUES
 ("RPG"), ("Acción"), ("Estrategia"), ("Aventura"), ("Shooter");

INSERT INTO games (title, description, release_year, developer, rating) VALUES
 ("Legends of Eldoria", "RPG épico de mundo abierto", 2023, "BlueStar Studios", 4.8),
 ("CyberStrike", "Shooter futurista multijugador", 2024, "NovaWorks", 4.5),
 ("Kingdom Battle", "Estrategia en tiempo real", 2022, "WarForge", 4.2);

INSERT INTO game_platform VALUES
 (1,1), (1,2), (1,4),
 (2,1), (2,3),
 (3,1), (3,2), (3,3);

INSERT INTO dlcs (game_id, name, price) VALUES
 (1, "Eldoria Frozen Lands", 14.99),
 (2, "CyberStrike Neon Pack", 9.99);

INSERT INTO achievements (game_id, name, description, points) VALUES
 (1, "Primer Dragón", "Derrota tu primer dragón", 50),
 (1, "Rey del Bosque", "Derrota al guardián del bosque", 80),
 (2, "25 Eliminaciones", "Consigue 25 kills en una partida", 30);

INSERT INTO rarities (name, drop_rate) VALUES
 ("Común", 70),
 ("Raro", 20),
 ("Épico", 8),
 ("Legendario", 2);

INSERT INTO items (name, rarity_id, value) VALUES
 ("Espada Oxidada", 1, 10),
 ("Arco Élfico", 2, 100),
 ("Báculo del Sabio", 3, 350),
 ("Espada del Infinito", 4, 2000);

INSERT INTO inventory VALUES
 (1,1,3), (1,2,1), (2,4,1);

INSERT INTO reviews (user_id, game_id, rating, comment) VALUES
 (1,1,5,"Increíble experiencia."),
 (2,2,4,"Muy buen shooter");

INSERT INTO servers (region, max_players) VALUES
 ("US-East", 100),
 ("LATAM-South", 80);

INSERT INTO matches (server_id, winner_id, duration) VALUES
 (2,1,32), (1,2,25);

INSERT INTO quests (game_id, name, reward_item) VALUES
 (1, "Salvar al Aldeano", 2),
 (2, "Hackear la Torre Central", 3);

INSERT INTO user_quests VALUES
 (1,1,0), (1,2,1);

INSERT INTO leaderboard VALUES
 (1,1,15000), (2,1,18000), (3,2,9000);