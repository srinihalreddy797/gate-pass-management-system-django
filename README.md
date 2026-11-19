# Gate Pass Management System

Gate Pass Management System is a full-stack Django web application for handling gate pass requests, approvals, and manual security verification using unique Pass IDs.

## Tech Stack

- Backend: Django
- Frontend: HTML, CSS, JavaScript
- Styling: Tailwind CSS via CDN
- Database: SQLite

## Features

- Custom user model with `Admin`, `Security`, and `User` roles
- User signup, login, and logout using Django authentication
- Auto-generated unique Pass IDs in `GP2026XXXX` format
- Pass application workflow with `Pending`, `Approved`, and `Rejected` status
- Security verification by manually entering Pass ID
- Entry and exit logging
- Django Admin customization for users, passes, and logs
- Search, status filtering, pagination, flash messages, and dark mode toggle

## Local Setup

1. Install Django:

   ```bash
   python -m pip install django
   ```

2. Run migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

5. Open:

   ```text
   http://127.0.0.1:8000/
   ```

## Replit Setup

1. Create a new Python Replit project.
2. Upload this project or import the folder.
3. In the Replit shell, run:

   ```bash
   python -m pip install django
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver 0.0.0.0:8000
   ```

4. Set the Replit run command to:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Default Role Notes

- Public signup creates `User` accounts.
- Create `Admin` and `Security` users from Django Admin by editing the `role` field.
- Superusers can access both the custom admin dashboard and Django Admin panel.
