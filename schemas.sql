-- 1. Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres VARCHAR(50),
    apellidos VARCHAR(50),
    email VARCHAR(100),
    contrasena VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de tareas
CREATE TABLE tareas (
    id_tarea INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(100),
    descripcion VARCHAR(255),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_limite DATE,
    estado VARCHAR(20) DEFAULT 'pendiente',
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- 3. Tabla de tipos de problemas (Se crea ANTES porque la siguiente tabla depende de ella)
CREATE TABLE tipos_problemas (
    tipo_problema VARCHAR(50) PRIMARY KEY,
    descripcion TEXT
);

-- 4. Tabla de historial de escaneos y análisis
CREATE TABLE historial_escaneos (
    id_escaneo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tarea INT,
    tipo_problema VARCHAR(50) NOT NULL,
    expresion_original TEXT NOT NULL,
    fecha_escaneo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resultado_json TEXT,
    FOREIGN KEY (id_tarea) REFERENCES tareas(id_tarea),
    FOREIGN KEY (tipo_problema) REFERENCES tipos_problemas(tipo_problema)
);