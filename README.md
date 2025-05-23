# Hostel-management-system

# 📘 User Authentication & Account Management API

This module handles user registration, login, email verification, password reset, and user profile management using Django Rest Framework (DRF) and JWT.

Base URL: `/api/accounts/`

---

## 🚀 Endpoints Overview

### 🔹 1. Register User

**POST** `/register/`  
Registers a new user and sends a verification code via email.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "password2": "yourpassword"
}
Response:

json
Copy
Edit
{
  "msg": "Registration successful. Please check your email for the verification code to activate your account."
}
🔹 2. Verify Email
POST /verify-email/
Activates a user account using the 6-digit verification code.

Request Body:

json
Copy
Edit
{
  "email": "user@example.com",
  "code": "123456"
}
Response:

json
Copy
Edit
{
  "msg": "Email verified successfully"
}
🔹 3. Login User
POST /login/
Authenticates a user and returns JWT access and refresh tokens.

Request Body:

json
Copy
Edit
{
  "email": "user@example.com",
  "password": "yourpassword"
}
Response:

json
Copy
Edit
{
  "token": {
    "refresh": "your_refresh_token",
    "access": "your_access_token"
  },
  "msg": "Login Successful"
}
🔹 4. Logout User
POST /logout/
Blacklists a refresh token to log out a user.
Auth Required: ✅ Access Token

Request Body:

json
Copy
Edit
{
  "refresh": "your_refresh_token"
}
Response:

json
Copy
Edit
{
  "msg": "Logout successful"
}
🔹 5. Get User Profile
GET /profile/
Returns the authenticated user’s profile details.
Auth Required: ✅ Access Token

Response:

json
Copy
Edit
{
  "id": 1,
  "email": "user@example.com",
  ...
}
🔹 6. Change Password
POST /change-password/
Changes the password for the logged-in user.
Auth Required: ✅ Access Token

Request Body:

json
Copy
Edit
{
  "old_password": "oldpassword",
  "new_password": "newpassword",
  "confirm_new_password": "newpassword"
}
Response:

json
Copy
Edit
{
  "msg": "Password Changed Successfully"
}
🔹 7. Send Password Reset Email
POST /send-reset-password-email/
Sends an email with a reset password link.

Request Body:

json
Copy
Edit
{
  "email": "user@example.com"
}
Response:

json
Copy
Edit
{
  "msg": "Email to Change Password Sent"
}
🔹 8. Reset Password
POST /reset-password/<uid>/<token>/
Allows a user to reset their password using a secure link.

Request Body:

json
Copy
Edit
{
  "new_password": "newpass",
  "confirm_new_password": "newpass"
}
Response:

json
Copy
Edit
{
  "msg": "Password Reset Successfully"
}
