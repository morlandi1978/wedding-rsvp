# 💍 Wedding RSVP — Guida al Deploy

Sistema completo per la gestione delle conferme di partecipazione al matrimonio.

## Struttura del progetto

```
wedding-rsvp/
├── database/
│   └── schema.sql          # Schema MySQL da importare
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── config.py       # Impostazioni dal .env
│   │   ├── database.py     # Modelli SQLAlchemy
│   │   ├── auth.py         # JWT + bcrypt
│   │   └── routers/
│   │       ├── rsvp.py     # Endpoint pubblici (invitati)
│   │       ├── admin.py    # Endpoint protetti (admin)
│   │       └── auth.py     # Login admin
│   ├── requirements.txt
│   ├── .env.example
│   └── start.sh
├── frontend/
│   ├── rsvp/
│   │   └── index.html      # Pagina RSVP per gli invitati
│   └── admin/
│       ├── login.html      # Login admin
│       └── dashboard.html  # Dashboard admin
└── nginx.conf.example      # Configurazione Nginx

```

---

## 1. Database

```sql
-- Importa lo schema
mysql -u root -p < database/schema.sql
```

Crea un utente dedicato:
```sql
CREATE USER 'wedding_user'@'localhost' IDENTIFIED BY 'password_sicura';
GRANT ALL PRIVILEGES ON wedding_rsvp.* TO 'wedding_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 2. Backend (Python / FastAPI)

```bash
cd backend

# Crea virtualenv
python3 -m venv venv
source venv/activate  # Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt

# Configura l'ambiente
cp .env.example .env
nano .env   # Compila DB_HOST, DB_USER, DB_PASSWORD, SECRET_KEY, ecc.
```

### Primo avvio: crea l'utente admin

```bash
# Avvia il server
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Da un altro terminale, chiama l'endpoint di setup UNA VOLTA:
curl -X POST http://localhost:8000/api/auth/setup
# Output atteso: {"message": "Admin 'admin' creato con successo"}

# Poi CAMBIA la password nel .env e riavvia!
```

### Avvio normale

```bash
./start.sh
# oppure:
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Systemd service (produzione)

```ini
# /etc/systemd/system/wedding-rsvp.service
[Unit]
Description=Wedding RSVP API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/wedding-rsvp/backend
ExecStart=/var/www/wedding-rsvp/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable wedding-rsvp
sudo systemctl start wedding-rsvp
```

---

## 3. Frontend

Copia i file sul server:
```bash
cp -r frontend/ /var/www/wedding-rsvp/frontend/
```

Modifica `API_BASE` in ogni HTML se necessario (di default `/api` — funziona con Nginx).

---

## 4. Nginx

```bash
cp nginx.conf.example /etc/nginx/sites-available/wedding-rsvp
# Modifica server_name e percorsi
sudo ln -s /etc/nginx/sites-available/wedding-rsvp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL con certbot
sudo certbot --nginx -d tuodominio.it
```

---

## 5. Utilizzo

### Aggiungere invitati
Dalla dashboard admin (`/admin/dashboard.html`) clicca **+ Aggiungi**, inserisci nome ed email.

Il sistema genera automaticamente un token univoco.

### Creare il link WhatsApp
Ogni invitato ha un link del tipo:
```
https://tuodominio.it/rsvp/?token=tok_abc123...
```
Cliccando "Link" nella dashboard lo copi negli appunti.

### Inviare su WhatsApp
Esempio di messaggio:
```
Ciao [Nome]! 💍
Siamo felici di invitarti al nostro matrimonio.
Per confermare la tua presenza clicca qui:
https://tuodominio.it/rsvp/?token=TOK_PERSONALE
```

---

## API Reference

Documentazione interattiva disponibile su: `/api/docs`

### Endpoint pubblici
| Metodo | URL | Descrizione |
|--------|-----|-------------|
| GET | `/api/rsvp/{token}` | Info invitato |
| POST | `/api/rsvp/{token}` | Invia risposta RSVP |

### Endpoint admin (JWT richiesto)
| Metodo | URL | Descrizione |
|--------|-----|-------------|
| GET | `/api/admin/guests` | Lista invitati |
| POST | `/api/admin/guests` | Aggiungi invitato |
| DELETE | `/api/admin/guests/{id}` | Elimina invitato |
| GET | `/api/admin/stats` | Statistiche |
| GET | `/api/admin/export/csv` | Esporta CSV |

---

## Note di sicurezza

- Cambia `SECRET_KEY` nel `.env` con una stringa casuale lunga (es. `openssl rand -hex 32`)
- Cambia la password admin subito dopo il setup
- Considera di limitare l'accesso a `/admin/` per IP in Nginx
- Usa sempre HTTPS in produzione
