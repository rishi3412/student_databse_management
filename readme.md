# How to Run the Project

## 1. Clone the Repository

```bash
git clone https://github.com/rishi3412/student_databse_management
cd student_database_management
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

## 3. Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## 4. Install Required Packages

```bash
pip install -r requirements.txt
```

## 5. Install and Open PostgreSQL

Open PostgreSQL and pgAdmin.

## 6. Create Database

Run the following SQL command in PostgreSQL Query Tool:

```sql
CREATE DATABASE student_management;
```

## 7. Configure Database URL

Inside `database.py`, update:

```python
DATABASE_URL = "postgresql://postgres:password@localhost/student_management"
```

Replace:
- username
- password
- database name

according to your PostgreSQL setup.

## 8. Run the Project

```bash
uvicorn app.main:app --reload
```

## 9. Open Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

## Default Admin Credentials

```text
Email: admin@gmail.com
Password: admin123
```