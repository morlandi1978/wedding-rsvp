-- Wedding RSVP Database Schema
-- MySQL / MariaDB

CREATE DATABASE IF NOT EXISTS wedding_rsvp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wedding_rsvp;

-- Tabella invitati
CREATE TABLE IF NOT EXISTS guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    token VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella risposte RSVP
CREATE TABLE IF NOT EXISTS rsvp_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT NOT NULL,
    attending BOOLEAN NOT NULL,
    companions INT DEFAULT 0,
    menu_choice VARCHAR(50),         -- 'standard', 'vegetarian', 'vegan', 'gluten_free'
    message TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE CASCADE
);

-- Tabella admin (un solo utente admin)
CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indici
CREATE INDEX idx_guests_token ON guests(token);
CREATE INDEX idx_rsvp_guest_id ON rsvp_responses(guest_id);

-- Inserimento admin di default (password: changeme123 — da cambiare subito!)
-- Hash generato con bcrypt, rounds=12
-- Per rigenerarlo: python3 -c "import bcrypt; print(bcrypt.hashpw(b'changeme123', bcrypt.gensalt(12)).decode())"
INSERT INTO admin_users (username, password_hash)
VALUES ('admin', '$2b$12$placeholder_change_this_hash_run_setup_py');

-- Esempi di invitati (da rimuovere in produzione)
-- INSERT INTO guests (name, email, token) VALUES
-- ('Mario Rossi', 'mario@example.com', 'tok_abc123def456'),
-- ('Laura Bianchi', 'laura@example.com', 'tok_xyz789ghi012');
