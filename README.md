
# 🏨 Hostel Management System – Backend API

This project provides a RESTful API for managing a hostel system, built with **Django Rest Framework** and **JWT Authentication**. It includes:

✅ User Registration, Authentication, Password Management  
👨‍🎓 Director Registration and Management  
🔒 Role-based Permissions (Pluggable for Hostel Managers, Students, Admins)

---

## 📦 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🌐 Base URLs

| Module              | Base URL         |
|---------------------|------------------|
| User Auth           | `/api/user/`     |
| Director Management | `/api/director/` |

---

## 📘 User Authentication API

### 🔹 Register User  
**POST** `/api/user/register/`  
Sends verification email.

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

---

### 🔹 Verify Email  
**POST** `/api/user/verify-email/`

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

---

### 🔹 Login  
**POST** `/api/user/login/`

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

---

### 🔹 Logout  
**POST** `/api/user/logout/`  
🔒 Requires authentication

```json
{
  "refresh": "your_refresh_token"
}
```

---

### 🔹 Get Profile  
**GET** `/api/user/profile/`  
🔒 Requires authentication

---

### 🔹 Change Password  
**POST** `/api/user/change-password/`  
🔒 Requires authentication

```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword"
}
```

---

### 🔹 Send Password Reset Email  
**POST** `/api/user/send-reset-password-email/`

```json
{
  "email": "user@example.com"
}
```

---

### 🔹 Reset Password  
**POST** `/api/user/reset-password/<uid>/<token>/`

```json
{
  "new_password": "newpass"
}
```

---

## 🧑‍💼 Director API

### 🔹 Register Director  
**POST** `/api/director/register/`  
Registers a director along with associated institute and user.

```json
{
  "email": "director@example.com",
  "password": "strongpassword",
  "first_name": "John",
  "last_name": "Doe",
  "designation": "Director",
  "contact_number": "+91XXXXXXXXXX",
  "alternate_contact_number": "+91YYYYYYYYYY",
  "address": "123 Main St",
  "city": "Indore",
  "state": "Madhya Pradesh",
  "pincode": "452001",
  "profile_picture": null,
  "institute": {
    "name": "IET DAVV",
    "address": "Khandwa Road",
    "city": "Indore",
    "state": "Madhya Pradesh",
    "pincode": "452017",
    "contact_email": "admin@ietdavv.edu.in",
    "contact_number": "+91ZZZZZZZZZZ",
    "website": "https://ietdavv.edu.in"
  }
}
```

---

### 🔹 Get Director Profile  
**GET** `/api/director/<id>/`  
🔒 Requires authentication
Returns details of a specific director (usually self).

---

### 🔹 Update Director Profile  
**PUT/PATCH** `/api/director/<id>/`  
🔒 Requires authentication

Used to update director's personal or institute info.

```json
{
  "name": "Dr. A. B. Updated",
  "phone": "+91XXXXXXXXXX"
}
```

---

