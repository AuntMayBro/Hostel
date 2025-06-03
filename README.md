# 🏨 Hostel Management System – Backend API

This document outlines the architecture and functionalities of the Hostel Management System's backend Application Programming Interface (API). The system is engineered utilizing Django and Django REST Framework, with JSON Web Tokens (JWT) implemented for secure authentication. It provides a comprehensive suite of services for the administration of institutes, directors, hostel managers, students, hostel facilities, room inventories, and application processes within a multi-institute environment.

## ✅ Core System Capabilities

* **User Account Administration (Account Application):**
    * Facilitation of user registration, incorporating mandatory email verification protocols.
    * Secure email and password-based authentication mechanisms (login/logout).
    * User profile management functionalities.
    * Secure password modification and recovery procedures.
* **Directorate and Institutional Management (Director Application):**
    * Systematic registration of Directors, which includes the concurrent creation of an associated institutional entity.
    * Comprehensive management (Create, Read, Update, Delete - CRUD) of Institutes, Courses, and Academic Branches.
    * Empowerment of Directors with CRUD operations for hostel facilities pertinent to their respective institutes.
* **Hostel Operations Management (Hostel Application):**
    * Detailed management of hostel room inventory (CRUD).
    * Assignment and administration of Hostel Managers, executed by authorized Directors (CRUD).
    * A structured system for student hostel applications, enabling students to apply and allowing Directors or Hostel Managers to review and process these submissions.
    * *Prospective Enhancements:* Development of modules for room allocation and financial payment processing, for which serializers are currently extant.
* **Authentication and Authorization Framework:**
    * Implementation of JWT-based authentication, providing secure access and refresh tokens.
    * A granular, role-based access control (RBAC) model, encompassing Superusers, Directors, Hostel Managers, and Students. Authorization is rigorously enforced based on user roles and their hierarchical or relational associations (e.g., a Director's operational scope is confined to entities within their designated institute).

---

## ⚙️ System Prerequisites and Configuration Protocol

### Essential Software and Libraries
* Python (version 3.8 or higher is recommended).
* Pip (Python package installation utility).
* Git (version control system for repository cloning).
* A virtual environment management tool (e.g., `venv`, `virtualenv`) is strongly advised for dependency isolation.

### Installation Procedure

1.  **Repository Acquisition:**
    Clone the project repository from its designated source.
    ```bash
    git clone <your-repository-url>
    cd hostel-management-system 
    ```

2.  **Virtual Environment Initialization:**
    Establish and activate a Python virtual environment.
    ```bash
    python -m venv venv
    # For Windows environments:
    venv\Scripts\activate
    # For macOS/Linux environments:
    source venv/bin/activate
    ```

3.  **Dependency Installation:**
    Ensure the presence of a `requirements.txt` file enumerating all requisite packages. Install these dependencies using pip.
    ```bash
    pip install -r requirements.txt
    ```
    Key dependencies typically encompass:
    * `django`
    * `djangorestframework`
    * `djangorestframework-simplejwt`
    * `psycopg2-binary` (for PostgreSQL integration) or alternative database drivers as appropriate.
    * Additional dependencies specific to the project, such as email backend libraries, should also be included.

4.  **Database Configuration:**
    Modify the `DATABASES` configuration within the `your_project_name/settings.py` file to reflect the specifications of the chosen database system (e.g., PostgreSQL, MySQL, SQLite).

5.  **Database Schema Migration:**
    Apply all pending database migrations to synchronize the schema.
    ```bash
    python manage.py migrate
    ```

6.  **Superuser Account Creation (Optional but Recommended):**
    Create an administrative superuser account for privileged access to the system.
    ```bash
    python manage.py createsuperuser
    ```
    Adhere to the ensuing prompts to finalize account creation.

7.  **Development Server Execution:**
    Initiate the Django development server.
    ```bash
    python manage.py runserver
    ```
    The API endpoints will typically become accessible at `http://127.0.0.1:8000/`.

---

## 📂 Standardized Directory Architecture

The project adheres to a conventional Django project structure, as illustrated below:


hostel-management-system/
├── account/                  # Manages user authentication and profiles
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py       
│   ├── views_account.py
│   └── urls.py
├── director/                 # Manages directors, institutes, courses, branches
│   ├── migrations/
│   ├── models.py
│   ├── serializers_director.py
│   ├── views_director.py
│   └── urls.py
├── hostel/                   # Manages hostels, rooms, managers, applications
│   ├── migrations/
│   ├── models.py
│   ├── serializers_hostel.py
│   ├── views_hostel.py
│   └── urls.py
├── backend/        
│   ├── settings.py           
│   ├── urls.py               # Root URL routing configuration
│   ├── wsgi.py             
│   └── asgi.py               
├── manage.py                 
└── requirements.txt          # Project dependencies listing


---

## 🔑 Authentication Protocol

* **JSON Web Tokens (JWT):** The API employs JWT for securing its endpoints. Upon successful authentication (login or registration), the system issues `access` and `refresh` tokens.
* **Token Transmission:** For requests to protected endpoints, the `access` token must be included within the `Authorization` header, prefixed by `Bearer`.
    ```
    Authorization: Bearer <your_access_token>
    ```
* **Token Refresh Mechanism:** Should an access token expire, the corresponding `refresh` token is utilized to procure a new token pair. This is typically handled via a dedicated endpoint (e.g., `/api/token/refresh/` if employing `djangorestframework-simplejwt` default configurations) or integrated within the login response.
* **Authorization Policies:** Access to specific API endpoints and operations is governed by the authenticated user's assigned role (Superuser, Director, HostelManager, Student) and their contextual relationships within the system (e.g., a Director's operational authority is restricted to their affiliated institute).

---

## 🌐 API Base Uniform Resource Locators (URLs)

The following table delineates the base URLs for the primary modules of the API:

| Module                       | Base URL           |
|------------------------------|--------------------|
| Account (User Authentication)| `/api/account/`    |
| Director Management          | `/api/director/`   |
| Hostel Management            | `/api/hostel/`     |

---

## 📘 API Endpoint Documentation

### Account API (`/api/account/`)

This module is responsible for user registration, authentication, profile management, and password administration.

---

#### 1. User Registration
* **Endpoint:** `POST /api/account/register/`
* **Description:** Facilitates the registration of new users (e.g., Student, Manager). Upon successful registration, a verification email containing an activation code is dispatched.
* **Authentication Requirement:** `AllowAny` (No authentication required).
* **Request Payload:**
    ```json
    {
      "email": "newuser@example.com",
      "password": "yourSecurePassword123",
      "role": "student", // Permissible values: "student", "manager". Director registration is handled separately.
    }
    ```
* **Successful Response (HTTP 201 Created):**
    ```json
    {
      "msg": "Registration successful. Please check your email for the verification code to activate your account."
    }
    ```
* **Error Response (HTTP 400 Bad Request):** Returned if input validation fails (e.g., pre-existing email, password mismatch).

---

#### 2. Email Verification
* **Endpoint:** `POST /api/account/verify-email/`
* **Description:** Validates the user's email address using the verification code received post-registration, thereby activating the account.
* **Authentication Requirement:** `AllowAny`.
* **Request Payload:**
    ```json
    {
      "email": "newuser@example.com",
      "code": "123456"
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      },
      "user_id": 123,
      "email": "newuser@example.com",
      "role": "student",
      "msg": "Email verified successfully. Account activated."
    }
    ```
* **Error Response (HTTP 400 Bad Request):** Indicates an invalid or expired code, or a non-existent email address.

---

#### 3. User Login
* **Endpoint:** `POST /api/account/login/`
* **Description:** Authenticates an existing user against provided credentials and issues JWT tokens upon success.
* **Authentication Requirement:** `AllowAny`.
* **Request Payload:**
    ```json
    {
      "email": "user@example.com",
      "password": "yourpassword"
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      },
      "user_id": 123,
      "email": "user@example.com",
      "role": "student", 
      "msg": "Login Successful"
    }
    ```
* **Error Responses:**
    * `HTTP 401 Unauthorized`: Invalid credentials provided.
    * `HTTP 403 Forbidden`: Account has not been activated via email verification.

---

#### 4. User Logout
* **Endpoint:** `POST /api/account/logout/`
* **Description:** Invalidates the provided refresh token by adding it to a blacklist, effectively logging the user out.
* **Authentication Requirement:** `Authenticated` (Although view implementation indicated this was commented, typical security practice mandates authentication).
* **Request Payload:**
    ```json
    {
      "refresh": "your_refresh_token_here"
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "msg": "Logout successful."
    }
    ```
* **Error Response (HTTP 400 Bad Request):** Triggered if the refresh token is absent or invalid.

---

#### 5. User Profile Retrieval
* **Endpoint:** `GET /api/account/profile/`
* **Description:** Fetches the profile information of the currently authenticated user.
* **Authentication Requirement:** `Authenticated`.
* **Successful Response (HTTP 200 OK):** The structure is contingent upon the `UserProfileSerializer` definition.
    ```json
    {
      "id": 123,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "student",
      "is_active": true,
      "student_profile": {
        "id": 1,
        "institute_name": "Example Institute",
        "course_name": "Computer Science",
        // ... other student-specific fields
      }
    }
    ```

---

#### 6. Password Modification
* **Endpoint:** `POST /api/account/change-password/`
* **Description:** Permits an authenticated user to modify their existing password.
* **Authentication Requirement:** `Authenticated`.
* **Request Payload:**
    ```json
    {
      "old_password": "currentSecurePassword",
      "new_password": "newSecurePassword123",
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "msg": "Password changed successfully."
    }
    ```
* **Error Response (HTTP 400 Bad Request):** Occurs if the current password is incorrect, or if the new passwords do not match or fail validation criteria.

---

#### 7. Password Reset Email Request
* **Endpoint:** `POST /api/account/send-reset-password-email/`
* **Description:** Initiates the password reset process by dispatching an email containing a unique reset link to the user's registered email address.
* **Authentication Requirement:** `AllowAny`.
* **Request Payload:**
    ```json
    {
      "email": "user@example.com"
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "msg": "If an account with that email exists and is active, a password reset link has been sent."
    }
    ```

---

#### 8. Password Reset Confirmation
* **Endpoint:** `POST /api/account/reset-password/<str:uid>/<str:token>/`
* **Description:** Finalizes the password reset procedure using the unique user identifier (UID) and token provided in the reset link.
* **Authentication Requirement:** `AllowAny`.
* **Path Parameters:**
    * `uid`: A URL-safe, base64-encoded user identifier.
    * `token`: The password reset token.
* **Request Payload:**
    ```json
    {
      "new_password": "newStrongPassword123",
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "msg": "Password has been reset successfully."
    }
    ```
* **Error Response (HTTP 400 Bad Request):** Returned if the token is invalid or has expired, or if the new passwords do not match or fail validation.

---
---

### Director API (`/api/director/`)

This module encompasses functionalities for the management of directors, institutional entities, academic courses, branches, and hostel facilities associated with directors.

---

#### 1. Director and Institute Registration
* **Endpoint:** `POST /api/director/register/`
* **Description:** Facilitates the registration of a new Director, which includes the simultaneous creation of an associated Institute.
* **Authentication Requirement:** `AllowAny`.
* **Request Payload:** (Derived from `DirectorRegistrationSerializer`)
    ```json
    {
      "email": "director@example.com",
      "password": "directorSecurePassword123",
      "first_name": "Jane",
      "last_name": "Director",
      "designation": "Director",
      "contact_number": "1234567890",
      "institute_name": "Grand Tech Institute",
      "institute_address": "123 Tech Park",
      "institute_city": "Techville",
      "institute_state": "State",
      "institute_pincode": "12345"
    }
    ```
* **Successful Response (HTTP 201 Created):**
    ```json
    {
      "msg": "Director registered successfully. Institute created.",
      "director_id": 1,
      "user_id": 124,
      "institute_id": 1,
      "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
    ```
* **Error Response (HTTP 400 Bad Request):** Indicates failure in validation (e.g., pre-existing email or institute name).

---

#### 2. Director Profile Administration
* **Endpoint:** `GET, PUT, PATCH /api/director/directors/<int:pk>/`
* **Description:** Enables retrieval, complete update, or partial update of a Director's profile. Deletion is typically managed through account deactivation or by a superuser.
* **Authentication Requirement:** `Authenticated`. A custom permission class such as `IsDirectorOwnerOrReadOnly` typically restricts modification privileges to the director concerned or a superuser.
* **Path Parameters:**
    * `pk`: The unique identifier of the Director.
* **Request Payload (for PUT/PATCH methods):** Comprises fields from `DirectorRegistrationSerializer`, excluding immutable fields like password, email, and institute creation parameters.
    ```json
    {
      "first_name": "Janet",
      "contact_number": "0987654321"
      // ... other modifiable director profile fields.
    }
    ```
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "id": 1,
      "user": 124, 
      "institute": 1,
      "first_name": "Janet",
      "last_name": "Director",
      // ... other director profile fields.
    }
    ```

---

#### 3. Institute Listing
* **Endpoint:** `GET /api/director/institutes/`
* **Description:** Retrieves a comprehensive list of all registered institutes.
* **Authentication Requirement:** `Authenticated`.
* **Successful Response (HTTP 200 OK):**
    ```json
    [
      {
        "id": 1,
        "name": "Grand Tech Institute",
        "address": "123 Tech Park",
        // ... other institute fields as defined in InstituteSerializer.
      },
      // ... additional institute entries.
    ]
    ```

---

#### 4. Institute Detail Retrieval
* **Endpoint:** `GET /api/director/institutes/<int:pk>/`
* **Description:** Fetches detailed information for a specifically identified institute.
* **Authentication Requirement:** `Authenticated`.
* **Path Parameters:**
    * `pk`: The unique identifier of the Institute.
* **Successful Response (HTTP 200 OK):**
    ```json
    {
      "id": 1,
      "name": "Grand Tech Institute",
      "address": "123 Tech Park",
      // ... other institute-specific fields.
    }
    ```

---

#### 5. Academic Course Management
* **List Courses:** `GET /api/director/courses/`
    * **Description:** Provides a list of academic courses. This list can be filtered by `institute_id`.
    * **Authentication Requirement:** `Authenticated`. Directors are authorized to view courses within their affiliated institute, while Superusers have unrestricted access.
    * **Query Parameters:** `?institute_id=<ID>` (Optional filter).
    * **Successful Response (HTTP 200 OK):** A collection of course objects.
* **Create Course:** `POST /api/director/courses/`
    * **Description:** Enables the creation of a new academic course. For authenticated Directors, the course is associated with their institute; Superusers may specify the institute.
    * **Authentication Requirement:** `Authenticated` (Director or Superuser).
    * **Request Payload:**
        ```json
        {
          "name": "Bachelor of Engineering",
          "code": "BE",
          "institute": 1 
        }
        ```
    * **Successful Response (HTTP 201 Created):** The newly created course object.
* **Course Detail Operations:** `GET, PUT, PATCH, DELETE /api/director/courses/<int:pk>/`
    * **Description:** Allows for the retrieval, update, partial update, or deletion of a specific academic course.
    * **Authentication Requirement:** `Authenticated` (Director of the course's institute or Superuser).
    * **Path Parameters:** `pk` (Course ID).
    * **Request Payload (for PUT/PATCH methods):** Includes fields such as `name`, `code`.
    * **Successful Response (HTTP 200 OK for GET/PUT/PATCH; HTTP 204 No Content for DELETE):** The course object or an empty response upon successful deletion.

---

#### 6. Academic Branch Management
* **List Branches:** `GET /api/director/branches/`
    * **Description:** Retrieves a list of academic branches, filterable by `course_id`.
    * **Authentication Requirement:** `Authenticated`.
    * **Query Parameters:** `?course_id=<ID>` (Essential for effective filtering). The `institute_id` may be utilized internally via serializer context.
    * **Successful Response (HTTP 200 OK):** A collection of branch objects.
* **Create Branch:** `POST /api/director/branches/`
    * **Description:** Facilitates the creation of a new academic branch under a specified course within the Director's institute.
    * **Authentication Requirement:** `Authenticated` (Director or Superuser).
    * **Request Payload:**
        ```json
        {
          "name": "Computer Science Engineering",
          "code": "CSE",
          "course": 1
        }
        ```
    * **Successful Response (HTTP 201 Created):** The newly created branch object.
* **Branch Detail Operations:** `GET, PUT, PATCH, DELETE /api/director/branches/<int:pk>/`
    * **Description:** Enables retrieval, update, partial update, or deletion of a specific academic branch.
    * **Authentication Requirement:** `Authenticated` (Director of the branch's institute or Superuser).
    * **Path Parameters:** `pk` (Branch ID).
    * **Request Payload (for PUT/PATCH methods):** Includes fields such as `name`, `code`.
    * **Successful Response (HTTP 200 OK for GET/PUT/PATCH; HTTP 204 No Content for DELETE):** The branch object or an empty response upon successful deletion.

---

#### 7. Hostel Facility Management by Director
* **List Hostels:** `GET /api/director/hostels/`
    * **Description:** Provides a list of hostel facilities associated with the authenticated Director's institute. Superusers have access to all hostel listings.
    * **Authentication Requirement:** `Authenticated` (Director or Superuser).
    * **Successful Response (HTTP 200 OK):** A collection of hostel objects, with details as per `HostelSerializer`.
* **Create Hostel:** `POST /api/director/hostels/`
    * **Description:** Enables the creation of a new hostel facility. The `director` and `institute` fields are automatically populated for an authenticated Director. Superusers are required to specify the `institute`.
    * **Authentication Requirement:** `Authenticated` (Director or Superuser).
    * **Request Payload:** (Fields correspond to `HostelSerializer`)
        ```json
        {
          "name": "Alpha Boys Hostel",
          "institute": 1, // Mandatory if requestor is a superuser; otherwise, auto-assigned from the director's profile.
          "address_line1": "12 Hostel Road",
          "city": "Techville",
          "state": "State",
          "pincode": "12345",
          "hostel_type": "boys", // Permissible values: 'boys', 'girls', 'coed'.
          "total_rooms": 50,
          "available_rooms": 50,
          "rent_per_month": 5000.00,
          "facilities": ["wifi", "mess"] // Illustrative example of facilities.
        }
        ```
    * **Successful Response (HTTP 201 Created):** The newly created hostel object.
* **Hostel Detail Operations:** `GET, PUT, PATCH, DELETE /api/director/hostels/<int:pk>/`
    * **Description:** Allows for the retrieval, update, partial update, or deletion of a specific hostel facility.
    * **Authentication Requirement:** `Authenticated` (Director of the hostel's institute or Superuser).
    * **Path Parameters:** `pk` (Hostel ID).
    * **Request Payload (for PUT/PATCH methods):** Comprises modifiable fields from `HostelSerializer`.
    * **Successful Response (HTTP 200 OK for GET/PUT/PATCH; HTTP 204 No Content for DELETE):** The hostel object or an empty response upon successful deletion.

---
---

### Hostel API (`/api/hostel/`)

This module is dedicated to hostel-specific operations, including the management of rooms, assignment of managers, and processing of student applications.

---

#### 1. Room Inventory Management
* **List Rooms:** `GET /api/hostel/rooms/`
    * **Description:** Retrieves a list of rooms, optionally filtered by `hostel_id`.
    * **Authentication Requirement:** `Authenticated` (Director or Manager of the specified hostel, or Superuser).
    * **Query Parameters:** `?hostel_id=<ID>` (Optional, but recommended for targeted queries).
    * **Successful Response (HTTP 200 OK):** A collection of room objects, with details as per `RoomSerializer`.
* **Create Room:** `POST /api/hostel/rooms/`
    * **Description:** Facilitates the creation of a new room within a designated hostel.
    * **Authentication Requirement:** `Authenticated` (Director or Manager of the specified hostel, or Superuser).
    * **Request Payload:** (Fields correspond to `RoomSerializer`)
        ```json
        {
          "hostel": 1,
          "room_number": "A101",
          "room_type": "single", // E.g., 'single', 'double', 'dormitory'.
          "capacity": 1,
          "current_occupancy": 0,
          "rent_per_bed": 6000.00,
          "is_available": true
        }
        ```
    * **Successful Response (HTTP 201 Created):** The newly created room object.
* **Room Detail Operations:** `GET, PUT, PATCH, DELETE /api/hostel/rooms/<int:pk>/`
    * **Description:** Enables retrieval, update, partial update, or deletion of a specific room.
    * **Authentication Requirement:** `Authenticated` (Director or Manager of the room's hostel, or Superuser).
    * **Path Parameters:** `pk` (Room ID).
    * **Request Payload (for PUT/PATCH methods):** Comprises modifiable fields from `RoomSerializer`.
    * **Successful Response (HTTP 200 OK for GET/PUT/PATCH; HTTP 204 No Content for DELETE):** The room object or an empty response upon successful deletion.

---

#### 2. Hostel Manager Administration
* **List Hostel Managers:** `GET /api/hostel/managers/`
    * **Description:** Retrieves a list of hostel managers. For Directors, this list is typically scoped to their institute; Superusers have access to all manager profiles.
    * **Authentication Requirement:** `Authenticated` (Director or Superuser).
    * **Successful Response (HTTP 200 OK):** A collection of hostel manager objects, with details as per `HostelManagerSerializer`.
* **Create/Assign Hostel Manager:** `POST /api/hostel/managers/`
    * **Description:** Enables the creation of a new hostel manager profile and associates it with an existing user (who must possess the 'Manager' role) and an institute.
    * **Authentication Requirement:** `Authenticated` (Director or Superuser). Directors are restricted to assignments within their own institute.
    * **Request Payload:** (Fields correspond to `HostelManagerSerializer`)
        ```json
        {
          "user": 25, 
          "institute": 1,
          "designation": "Senior Hostel Warden",
          "contact_number": "1122334455"
          // ... other relevant fields such as address, start_date.
        }
        ```
    * **Successful Response (HTTP 201 Created):** The newly created hostel manager object.
* **Hostel Manager Detail Operations:** `GET, PUT, PATCH, DELETE /api/hostel/managers/<int:pk>/`
    * **Description:** Allows for the retrieval, update, partial update, or deletion of a specific hostel manager's profile. A manager can be disassociated from a hostel by setting their `managed_hostel` attribute to `null` via the Hostel detail endpoint. Deletion of a manager via this endpoint removes their managerial profile.
    * **Authentication Requirement:** `Authenticated` (Director of the manager's institute or Superuser).
    * **Path Parameters:** `pk` (HostelManager ID).
    * **Request Payload (for PUT/PATCH methods):** Comprises modifiable fields from `HostelManagerSerializer`.
    * **Successful Response (HTTP 200 OK for GET/PUT/PATCH; HTTP 204 No Content for DELETE):** The hostel manager object or an empty response upon successful deletion.

---

#### 3. Hostel Application Management (ViewSet)
* **Base Endpoint:** `/api/hostel/applications/`
* **Description:** Governs the lifecycle of student applications for hostel accommodation.
* **Authentication Requirement:** `Authenticated`. Specific actions are subject to role-based permissions:
    * **Students:** Permitted to create applications for themselves and view their own application status.
    * **Directors/Managers:** Authorized to view applications pertaining to their institute or managed hostel, and to update application statuses.
    * **Superusers:** Possess unrestricted access to all application functionalities.
* **Supported Actions:**
    * **List Applications:** `GET /api/hostel/applications/`
        * **Response:** A collection of application objects, filtered according to the requestor's role and permissions.
    * **Create Application:** `POST /api/hostel/applications/` (Restricted to Students)
        * **Request Payload:** (Fields correspond to `HostelApplicationSerializer`)
            ```json
            {
              // Fields such as student, institute, course_at_application, and branch_at_application are automatically populated for the submitting student.
              "preferred_hostel": 1, // Optional: Hostel ID.
              "preferred_room_type": "double", // E.g., 'single', 'double'.
              "reason_for_hostel": "Proximity to college and conducive study environment."
            }
            ```
        * **Response (HTTP 201 Created):** The application object, with an initial `status` of "pending".
    * **Retrieve Application:** `GET /api/hostel/applications/<int:pk>/`
        * **Response:** The details of the specified application object.
    * **Update Application:** `PUT / PATCH /api/hostel/applications/<int:pk>/`
        * **Students:** May update certain fields (e.g., `reason_for_hostel`) if the application status is still 'pending'.
        * **Directors/Managers:** Authorized to modify the `status` (e.g., to 'approved', 'rejected', 'waitlisted') and append `remarks_by_reviewer`.
        * **Request Payload:** Contains the fields to be updated.
            ```json
            // Example: Manager approving an application.
            {
              "status": "approved", // Permissible values: "approved", "rejected", "waitlisted".
              "remarks_by_reviewer": "Application approved based on availability."
            }
            ```
        * **Response (HTTP 200 OK):** The updated application object.
    * **Delete Application:** `DELETE /api/hostel/applications/<int:pk>/`
        * **Permissions:** Typically restricted to Administrators/Superusers, or Students for their own PENDING applications.
        * **Response (HTTP 204 No Content).**

---

## 📝 General Remarks and Future Development Trajectory

* **Error Handling Conventions:** The API adheres to standard HTTP status codes for conveying error conditions (e.g., 400 for client-side bad requests or validation failures, 401 for unauthorized access, 403 for forbidden actions, 404 for resource not found). Error responses typically include a `detail` field or field-specific error messages for client guidance.
* **Permissions Granularity:** While foundational permission classes are established, certain views incorporate more nuanced authorization logic directly within their methods (e.g., verifying a director's ownership of an institute). For enhanced maintainability and adherence to DRY principles, such logic should ideally be encapsulated within custom Django REST Framework permission classes.
* **Prospective Enhancements:**
    * Implementation of dedicated endpoints for `RoomAllocation` and `Payment` functionalities, leveraging the existing serializer definitions.
    * Development of a comprehensive suite of automated tests to ensure code quality and reliability.
    * Augmentation of the email notification system to encompass alerts for application status transitions, payment reminders, and other pertinent events.
    * Exploration of WebSocket integration for real-time data updates, particularly for features such as application status tracking.
* **Configuration Settings:** It is imperative to ensure that the `settings.py` file contains appropriate configurations for `SIMPLE_JWT` (including token lifetime parameters), `FRONTEND_PASSWORD_RESET_URL`, and the designated email backend services.

This README document aims to provide a thorough and professional overview of the Hostel Management System API.