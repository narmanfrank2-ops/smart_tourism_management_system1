# Smart Tourism Management System

A web-based application to help tourists plan and manage their travel
activities efficiently — explore destinations, book tour packages, make
payments, and track bookings, all from a single platform.

## About the Project

The Smart Tourism Management System provides detailed information about
tourist destinations, hotels, transportation facilities, and tour packages.
Users can explore travel options, book packages, make online payments, and
track their bookings through a single platform. It simplifies travel
planning, reduces manual effort, and enhances the overall travel experience
through a user-friendly and efficient interface.

## Objectives

- Provide online access to tourist destination information.
- Enable users to book tour packages easily.
- Maintain tourist and booking details in a database.
- Provide hotel and transportation information.
- Simplify travel planning and management.

## Modules

### 1. Admin Module
- Admin login
- Manage tour packages (add / edit / delete)
- Manage hotels and transport (add / delete)
- View all user bookings, filter by status, and update booking status

### 2. User Module
- User registration and login
- Search tourist places
- Book tour packages
- View booking history

### 3. Booking Module
- Package selection
- Booking confirmation
- Payment details (demo payment gateway)
- Booking status tracking (Pending Payment → Confirmed → Completed / Cancelled)

## Tech Stack

| Layer      | Technology                     |
|------------|---------------------------------|
| Front-End  | HTML, CSS, JavaScript (Jinja2)  |
| Back-End   | Python (Flask)                  |
| Database   | SQLite (via SQLAlchemy ORM)     |

## Project Structure

```
smart_tourism_management_system/
├── app.py                     # Main Flask application (all routes)
├── models.py                  # SQLAlchemy database models
├── init_db.py                 # Script to create & seed the database
├── requirements.txt           # Python dependencies
├── tourism.db                 # SQLite database (created after init_db.py runs)
├── static/
│   ├── css/style.css          # Stylesheet
│   ├── js/script.js           # Client-side JavaScript
│   └── images/                # Image assets
└── templates/
    ├── base.html              # Shared layout (navbar/footer)
    ├── index.html              # Home page
    ├── destinations.html       # Search tourist places
    ├── destination_detail.html
    ├── packages.html           # All tour packages
    ├── package_detail.html
    ├── register.html
    ├── login.html
    ├── book_package.html       # Booking Module: package selection
    ├── payment.html            # Booking Module: payment details
    ├── booking_confirmation.html
    ├── my_bookings.html        # User booking history
    ├── 404.html
    └── admin/
        ├── admin_login.html
        ├── dashboard.html
        ├── manage_packages.html
        ├── edit_package.html
        ├── manage_hotels.html
        ├── manage_transport.html
        └── view_bookings.html
```

## Setup Instructions

1. **Install Python 3.9+** if not already installed.

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database** (creates `tourism.db` with sample data):
   ```bash
   python init_db.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. Open your browser and go to: **http://127.0.0.1:5000**

## Demo Login Credentials

After running `init_db.py`, use these accounts to explore the system:

| Role  | Email                         | Password    |
|-------|--------------------------------|-------------|
| Admin | admin@smarttourism.com         | Admin@123   |
| User  | user@smarttourism.com          | User@123    |

Admin login page: `http://127.0.0.1:5000/admin/login`

## Notes for Presentation / Viva

- The payment flow is a **demo/mock gateway** — no real transactions or
  external payment processors are integrated, which is standard for an
  academic project of this scope.
- The database (SQLite) is created automatically by `init_db.py`; delete
  `tourism.db` and re-run the script to reset all data.
- Passwords are securely hashed using Werkzeug's `generate_password_hash`
  (never stored in plain text).
- To add screenshots or a project report, this project can be extended
  further, or exported alongside a Word/PDF report.

## Academic Year
2025–2026
