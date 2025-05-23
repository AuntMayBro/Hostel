# Hostel Management System

# 📘 User Authentication & Account Management API

This module, built with **Django Rest Framework (DRF)** and **JWT**, handles all aspects of user authentication and account management. This includes user registration, login, email verification, password reset, and user profile management.

Base URL for all endpoints: `/api/accounts/`

---

## 🚀 Endpoints Overview

Here's a breakdown of the available API endpoints:

### 🔹 1. Register User

**POST** `/register/`

Registers a new user and automatically sends a verification code to their email address.

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "password2": "yourpassword"
}
```

**Response**:

```json
{
  "msg": "Registration successful. Please check your email for the verification code to activate your account."
}
```

### 🔹 2. Verify Email

**POST** `/verify-email/`

Activates a user account using the 6-digit verification code sent during registration.

**Request Body**:

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response**:

```json
{
  "msg": "Email verified successfully"
}
```

### 🔹 3. Login User

**POST** `/login/`

Authenticates a user and provides JWT access and refresh tokens for subsequent API requests.

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response**:

```json
{
  "token": {
    "refresh": "your_refresh_token",
    "access": "your_access_token"
  },
  "msg": "Login Successful"
}
```

### 🔹 4. Logout User

**POST** `/logout/`

Blacklists a refresh token to effectively log out a user.
**Authentication Required**: ✅ Access Token

**Request Body**:

```json
{
  "refresh": "your_refresh_token"
}
```

**Response**:

```json
{
  "msg": "Logout successful"
}
```

### 🔹 5. Get User Profile

**GET** `/profile/`

Retrieves the profile details of the authenticated user.
**Authentication Required**: ✅ Access Token

**Response**:

```json
{
  "id": 1,
  "email": "user@example.com"
  // ... other user profile details
}
```

### 🔹 6. Change Password

**POST** `/change-password/`

Allows a logged-in user to change their password.
**Authentication Required**: ✅ Access Token

**Request Body**:

```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword",
  "confirm_new_password": "newpassword"
}
```

**Response**:

```json
{
  "msg": "Password Changed Successfully"
}
```

### 🔹 7. Send Password Reset Email

**POST** `/send-reset-password-email/`

Initiates the password reset process by sending an email with a secure reset link to the user.

**Request Body**:

```json
{
  "email": "user@example.com"
}
```

**Response**:

```json
{
  "msg": "Email to Change Password Sent"
}
```

### 🔹 8. Reset Password

**POST** `/reset-password/<uid>/<token>/`

Allows a user to reset their password using the unique ID (`uid`) and token provided in the password reset email link.

**Request Body**:

```json
{
  "new_password": "newpass",
  "confirm_new_password": "newpass"
}
```

**Response**:

```json
{
  "msg": "Password Reset Successfully"
}
```