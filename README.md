# 🏨 Hostel Management API

A powerful and modular Django REST API backend for managing hostels, users, institutes, courses, branches, and hostel-specific operations. The system ensures secure authentication using JWT, supports role-based functionality (Students, Directors, Hostel Managers), and is built with extensibility and clarity in mind.

---

## 🚀 Features

- 🔐 JWT-based user authentication (Student, Director, Manager)
- 🏫 Institute, Course & Branch management by Directors
- 🛏️ Hostel & Room creation with assignment logic
- 📄 Student hostel application workflows
- 📦 Modular and scalable project structure

---

## ⚙️ Prerequisites

- Python 3.8+
- pip (Python package manager)
- PostgreSQL (recommended) or SQLite (for development)

---

## 🛠️ Setup Instructions

```bash
git clone <repository_url>
cd <project_directory>

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt  # Make sure requirements.txt includes all necessary packages
```

### 🔧 Database Configuration

Edit `backend/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 🔨 Migrate & Run

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional
python manage.py runserver
```

API Base URL: `http://127.0.0.1:8000/api/`

---

## 🔑 Authentication

Uses **JWT**:

- Access token → passed via `Authorization: Bearer <token>`
- Refresh token → used to renew access

---

## 📡 API Modules & Endpoints

### 👤 User Module (`/api/user/`)

- `POST /register/` → Register (student/director/manager)
- `POST /verify-email/` → Verify registration OTP
- `POST /login/student/` → Login as Student
- `POST /login/admin/` → Login as Director/Manager
- `POST /logout/` → Logout
- `GET /session/` → Get session info
- `POST /token/refresh/` → Refresh JWT
- `GET|PUT|PATCH /profile/` → View or update profile
- `PUT /change-password/` → Change password
- `POST /send-reset-password-email/` → Send password reset link
- `POST /reset-password/<uid>/<token>/` → Reset password

### 🧑‍🏫 Director Module (`/api/director/`)

- `POST /register/` → Register director & institute
- `GET|PUT|PATCH|DELETE /<int:pk>/` → Director detail
- `GET /institute/` → List all institutes
- `GET /institute/<int:pk>/` → Get institute detail
- `GET|POST /courses/` → List/Create courses
- `GET|PUT|PATCH|DELETE /courses/<int:pk>/` → Manage course
- `GET|POST /branches/` → List/Create branches
- `GET|PUT|PATCH|DELETE /branches/<int:pk>/` → Manage branch
- `GET|POST /create-hostel/` → List/Create hostels
- `GET|PUT|PATCH|DELETE /hostel/<int:pk>/` → Manage hostel

### 🏢 Hostel Module (`/api/hostel/`)

- `GET|POST /create-room/` → List/Create rooms (optional `hostel_id` filter)
- `GET|PUT|PATCH|DELETE /room/<int:pk>/` → Manage room
- `GET|POST /create-manager/` → List/Create hostel managers
- `GET|PUT|PATCH|DELETE /manager/<int:pk>/` → Manage hostel manager
- `GET|POST /applications/` → Student hostel applications
- `GET|PUT|PATCH|DELETE /applications/<int:pk>/` → Manage applications

---

## 🔐 Environment Variables

Use a `.env` file to store:

```env
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost/db
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Hostel Management <noreply@hostel.com>
```

---

## 🗂️ Project Structure

```text
.
├── manage.py
├── backend/                  # Main Django project directory
│   ├── settings.py           # Project settings
│   ├── urls.py               # Root URL configuration
├── account/                  # Authentication & user
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── director/                 # Institute management
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── hostel/                   # Hostel operations
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── requirements.txt          # Python dependencies
```

---

## 🤝 Contributing

Pull requests and issue reports are welcome. Feel free to fork this project and enhance it with new features.

---

## 📃 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

For any queries or support, feel free to reach out via email at: [admin@hostelmanagement.com](mailto\:admin@hostelmanagement.com)

