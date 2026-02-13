import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

def connect_to_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def show_datas():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def insert_data(id,name,age):
    if not isinstance(name, str) or not name.strip():
        return {"status": "error", "message": "Invalid name provided"}
    try:
        age = int(age)
    except (ValueError, TypeError):
        return {"status": "error", "message": f"Invalid age: {age}"}
    if id is not None:
        try:
            id = int(id)
        except (ValueError, TypeError):
            return {"status": "error", "message": f"Invalid id: {id}"}

    try:
        conn = connect_to_db()
        cur = conn.cursor()
        if id is not None:
            cur.execute("INSERT INTO students(id, name, age) VALUES(%s,%s,%s)", (id, name.strip(), age))
        else:
            cur.execute("INSERT INTO students(name, age) VALUES(%s,%s) RETURNING id", (name.strip(), age))
            id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "inserted", "id": id}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.close()
        conn.close()
        return {"status": "error", "message": f"Student with id {id} already exists"}

def update_data(id, name,age):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE students SET name=%s, age=%s WHERE id=%s",
        (name, age, id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "updated"}

def delete_data(id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "deleted"}