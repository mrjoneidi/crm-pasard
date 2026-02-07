# Real Estate CRM System

A production-ready CRM system for a real estate registry office, built with Python, Flask, SQLAlchemy, and PostgreSQL/SQLite.

## Key Features

*   **Persian Language Support:** All database columns and API fields are in Persian.
*   **Case Management:** Create, update, search, and archive cases.
*   **Document Management:** Upload and manage unlimited documents per case.
*   **Subdivision (Tafkik):** Create sub-cases from parent cases with document transfer.
*   **Audit Trail:** Full history logging of all changes.
*   **Rent & Invoicing:** Manage lease contracts and automatically generate invoices.
*   **Swagger API Docs:** Interactive API documentation.

## Project Structure

*   `app.py`: Application entry point and configuration.
*   `config.py`: Configuration settings.
*   `modules/`: Reusable core modules.
    *   `models.py`: Database models (Case, Person, Document, etc.).
    *   `schemas.py`: Marshmallow schemas for serialization/validation.
    *   `audit.py`: Audit logging logic.
    *   `db.py`: Database instance.
*   `api/`: API Blueprints.
    *   `cases/`: Case management endpoints.
    *   `documents/`: Document upload/download.
    *   `contracts/`: Lease contract management.
    *   `invoices/`: Invoice generation and reporting.

## Setup & Running

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize Database:**
    The database is automatically initialized on the first run of `app.py`.
    To populate with sample data:
    ```bash
    python3 populate_db.py
    ```

3.  **Run the Application:**
    ```bash
    python3 app.py
    ```
    The server will start at `http://localhost:5000`.

## API Documentation (Swagger)

Once the application is running, visit:
**`http://localhost:5000/apidocs`**

This provides an interactive UI to test the API endpoints.

## Testing

Run the automated test suite:
```bash
python3 tests/test_system.py
```

## Database Schema (Persian)

*   **Cases (`cases`):** `شماره_پرونده`, `شماره_کلاسه`, `وضعیت`, `آدرس`, ...
*   **People (`people`):** `نام_و_نام_خانوادگی`, `کد_ملی`, `تلفن_همراه`, ...
*   **Ownerships (`ownerships`):** Links Cases and People.
*   **Documents (`documents`):** File metadata.
*   **LeaseContracts (`lease_contracts`):** Rent info.
*   **Invoices (`invoices`):** Generated bills.
*   **AuditLogs (`audit_logs`):** System history.
