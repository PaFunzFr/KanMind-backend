# Kanban Board Backend Project

![KanMind Logo](assets/icons/logo_icon.svg)

Dies ist das Backend für eine Django REST API Anwendung.
Das Projekt basiert auf Django und Django REST Framework und nutzt eine klassische App‑Struktur (z.B. app_auth, app_board, app_task).
Mit dieser API kannst du Benutzerauthentifizierung, Boards und Aufgaben verwalten.

---

## Projectstruktur

backend/
├── app_auth/
├── app_board/
├── app_task/
├── core/
├── env/                  # lokale virtuelle Umgebung (ignored)
├── manage.py
├── requirements.txt
└── .gitignore

---

## ⚙️ Voraussetzungen

- **Python 3.8+**
- **pip**
- Optional: **virtualenv**

---

## 🚀 Installation

1. **Repository klonen**
git clone https://github.com/<dein-benutzername>/<repo-name>.git
cd <repo-name>


2. **Virtuelle Umgebung erstellen**
python -m venv env
source env/bin/activate # Windows: env\Scripts\activate

3. **Abhängigkeiten installieren**
pip install -r requirements.txt

4. **Migrationen durchführen**
python manage.py migrate

5. **Superuser für Admin erstellen**
python manage.py createsuperuser

6. **Server starten**
python manage.py runserver


> **Hinweis:**  
> Standardmäßig läuft der Server unter [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
> Passe `core/settings.py` für Datenbanken, `DEBUG`, und `ALLOWED_HOSTS` an.

---

## 📦 Abhängigkeiten (`requirements.txt`)

- `Django`
- `djangorestframework`

---

## 🔒 Sicherheit

- Achte darauf, dass `.env` Dateien **nicht** im Repo landen (siehe `.gitignore`)
- Keine Datenbankdateien (`*.sqlite3`) ins Repo pushen.
- Für geheime Schlüssel und Passwörter ausschließlich `.env` verwenden.

---

## 📝 Lizenz

MIT License – siehe [LICENSE](LICENSE)
