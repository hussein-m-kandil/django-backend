# Django Backend

A back-end web app built with Django to support multiple front-end apps.

> Deploy back-end once, support any front-end.

## Apps

Applications that utilizes this backend project.

- [**MonoText**](https://husseinkandil.pythonanywhere.com/monotext/)
- [**Provetrina**](https://provetrina.pages.dev/)

## Technologies

- **Python**
- **Django**
- **Django REST Framework (DRF)**
- **DRF Simple JWT**
- **DRF Spectacular**
- **PostgreSQL**
- **Docker Compose**
- **FPDF2**
- **Faker**

## Features

- **[PDF Generation](./provetrina/resume.py)**
- **Automated Testing**
- **JWT-Based Authentication**
- **Automated [Database Management](./pg.py) and [Seeding](./provetrina/management/commands/seed_provetrina.py)**

---

## How to Run the Application

### Prerequisites

- **Python** 3.14
- **Docker** 29 -- _for running the **PostgreSQL** locally_

### Setup

1. Navigate to the `backend` directory.
2. Optionally, activate a Python virtual environment `venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Create a `.env` file based on the `.env.sample`.
5. Start the database: `python3 pg.py up`.
6. Run migrations: `python3 manage.py migrate`.
7. Optionally, seed the database: `python3 manage.py seed`.
8. Start the server: `python3 manage.py runserver`.

### Testing

Run backend tests with `python3 manage.py test`.
