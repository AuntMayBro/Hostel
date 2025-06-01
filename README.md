
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
Registers a user and returns JWT tokens.

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### 🔸 Response:
```json
{
  "message": "User registered successfully. Please verify your email.",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
}
```

---

### 🔹 Verify Email  
**POST** `/api/user/verify-email/`  
Verifies email and returns JWT tokens.

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

#### 🔸 Response:
```json
{
  "message": "Email verified successfully.",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
}
```

---

### 🔹 Login  
**POST** `/api/user/login/`  
Logs in a user and returns JWT tokens.

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### 🔸 Response:
```json
{
  "message": "Login successful.",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
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
Returns new JWT tokens after successful password change.

```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword"
}
```

#### 🔸 Response:
```json
{
  "message": "Password changed successfully.",
  "tokens": {
    "access": "new_access_token",
    "refresh": "new_refresh_token"
  }
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
Returns new JWT tokens after reset.

```json
{
  "new_password": "newpass"
}
```

#### 🔸 Response:
```json
{
  "message": "Password reset successful.",
  "tokens": {
    "access": "new_access_token",
    "refresh": "new_refresh_token"
  }
}
```

---

## 🧑‍💼 Director API

### 🔹 Register Director  
**POST** `/api/director/register/`  
Registers a director and institute, and returns JWT tokens.

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

#### 🔸 Response:
```json
{
  "message": "Director registered successfully.",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
}
```

---

### 🔹 Get Director Profile  
**GET** `/api/director/<id>/`  
🔒 Requires authentication  
Returns details of the specific director.

---

### 🔹 Update Director Profile  
**PUT/PATCH** `/api/director/<id>/`  
🔒 Requires authentication

```json
{
  "name": "Dr. A. B. Updated",
  "phone": "+91XXXXXXXXXX"
}
```

---
