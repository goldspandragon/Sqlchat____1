-- ===============================
--   BASE HOSPITALARIA COMPLETA
-- ===============================

DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS specialties;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS exams;
DROP TABLE IF EXISTS hospitalizations;

CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    fullname TEXT NOT NULL,
    rut TEXT UNIQUE,
    birthdate TEXT,
    phone TEXT,
    email TEXT
);

CREATE TABLE specialties (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE doctors (
    id INTEGER PRIMARY KEY,
    fullname TEXT,
    specialty_id INTEGER,
    email TEXT,
    phone TEXT,
    FOREIGN KEY(specialty_id) REFERENCES specialties(id)
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    reason TEXT,
    status TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id)
);

CREATE TABLE medicines (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY,
    appointment_id INTEGER,
    medicine_id INTEGER,
    dosage TEXT,
    duration TEXT,
    FOREIGN KEY(appointment_id) REFERENCES appointments(id),
    FOREIGN KEY(medicine_id) REFERENCES medicines(id)
);

CREATE TABLE exams (
    id INTEGER PRIMARY KEY,
    appointment_id INTEGER,
    exam_type TEXT,
    result TEXT,
    FOREIGN KEY(appointment_id) REFERENCES appointments(id)
);

CREATE TABLE medical_records (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE hospitalizations (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    room TEXT,
    start_date TEXT,
    end_date TEXT,
    reason TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

-- ==== INSERTS DE PRUEBA ====

INSERT INTO specialties (name) VALUES
 ("Cardiología"), ("Neurología"), ("Pediatría"), ("Dermatología");

INSERT INTO patients (fullname, rut, birthdate, phone, email) VALUES
 ("Ana Fuentes", "19.450.221-3", "1998-02-11", "987654321", "ana@example.com"),
 ("Luis González", "17.783.121-2", "1985-06-22", "912345678", "luis@example.com");

INSERT INTO doctors (fullname, specialty_id, email, phone) VALUES
 ("Dr. Pedro Araya", 1, "paraya@hospital.cl", "987000111"),
 ("Dra. Paula Soto", 3, "psoto@hospital.cl", "981234567");

INSERT INTO appointments (patient_id, doctor_id, date, reason, status) VALUES
 (1, 1, "2024-09-10 10:00", "Dolor en el pecho", "Completado"),
 (2, 2, "2024-09-11 15:30", "Fiebre alta", "Pendiente");

INSERT INTO medicines (name, description) VALUES
 ("Ibuprofeno", "Antiinflamatorio"),
 ("Paracetamol", "Analgésico");

INSERT INTO prescriptions (appointment_id, medicine_id, dosage, duration) VALUES
 (1, 1, "400 mg", "5 días"),
 (2, 2, "500 mg", "3 días");

INSERT INTO exams (appointment_id, exam_type, result) VALUES
 (1, "Electrocardiograma", "Normal"),
 (2, "Hemograma", "Leucocitos altos");

INSERT INTO medical_records (patient_id, description) VALUES
 (1, "Paciente con historial de asma"),
 (2, "Reacción alérgica a penicilina");

INSERT INTO hospitalizations (patient_id, room, start_date, end_date, reason) VALUES
 (1, "101A", "2024-09-01", "2024-09-03", "Observación"),
 (2, "203B", "2024-09-05", "2024-09-08", "Tratamiento fiebre");
