# Real Estate CRM System

A production-ready CRM system for a real estate registry office, built with Python, Flask, SQLAlchemy, and PostgreSQL/SQLite.

## Key Features

*   **Persian Language Support:** All database columns and API fields are in Persian.
*   **Case Management:** Create, update, search, and archive cases.
    *   **Fields:** Case Number, Classification Number, Status, Full Address, Description.
    *   **Owner Info:** Full Name, National ID, Mobile Phone, Alternative Phone.
    *   **Ownership History:** Track changes in ownership with dates.
*   **Document Management:** Upload and manage unlimited documents per case.
    *   **File Types:** Photos, Contracts, Maps, Permits.
    *   **Metadata:** Title, Category, Registration Date, Document Date.
*   **Subdivision (Tafkik):** Create sub-cases from parent cases with document transfer.
*   **Audit Trail:** Full history logging of all changes.
*   **Rent & Invoicing:** Manage lease contracts and automatically generate invoices.
*   **Swagger API Docs:** Interactive API documentation.

## Database Management & Persistence

The application uses an SQLite database (`instance/crm.db`) by default. This file persists on disk, meaning your data remains safe even if you stop or restart the application.

**Important:** Do NOT delete `instance/crm.db` unless you want to erase all data.

### Management Commands (`manage.py`)

We have created a dedicated script `manage.py` to handle database operations safely.

1.  **Initialize Database (Create Tables):**
    Run this command *once* to set up the database structure.
    ```bash
    python3 manage.py init
    ```

2.  **Populate with Sample Data:**
    Run this to add fake data for testing.
    ```bash
    python3 manage.py populate
    ```

3.  **Reset Database (Delete All Data):**
    **WARNING:** This will delete all your data! Use with caution.
    ```bash
    python3 manage.py drop
    ```

## Running the Application

### Option 1: Running Directly (Python)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize Database:**
    ```bash
    python3 manage.py init
    ```

3.  **Run the Server:**
    ```bash
    python3 app.py
    ```
    The server will start at `http://localhost:5000`.

### Option 2: Running with Docker (Recommended for Production)

Running with Docker ensures a consistent environment and automatic restarts.

1.  **Build and Run:**
    ```bash
    docker-compose up --build -d
    ```

2.  **Initialize Database (Inside Container):**
    ```bash
    docker-compose exec web python manage.py init
    ```

3.  **Access the App:**
    Visit `http://localhost:5000`.

4.  **Stop the App:**
    ```bash
    docker-compose down
    ```
    *Note: Data in `instance/` and `uploads/` is preserved via volumes.*

## Project Structure

*   `app.py`: Application entry point.
*   `manage.py`: Database management script.
*   `config.py`: Configuration settings.
*   `modules/`: Reusable core modules (Models, Schemas, DB).
*   `api/`: API Blueprints (Cases, Documents, Contracts).
*   `templates/`: HTML templates for the UI.
*   `static/`: CSS/JS files.
*   `tests/`: Unit tests.

## API Documentation (Swagger)

Once the application is running, visit:
**`http://localhost:5000/apidocs`**

This provides an interactive UI to test the API endpoints.
