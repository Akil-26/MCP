from fastapi import FastAPI
import psycopg2
from dotenv import load_dotenv
import os

app = FastAPI()
def conn():
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

@app.get("/show-all")
def show_all_students():
    connection = conn()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students;")
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    return students

@app.post("/add-student/{name}/{age}")
def add_student(name: str, age: int):
    connection = conn()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO students (name, age) VALUES (%s, %s);", (name, age))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "student added"}

@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int):
    connection = conn()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s;", (student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "student deleted"}


@app.put("/update-student/{student_id}/{name}/{age}/{class_id}")
def update_student(student_id: int, name: str, age: int,class_id: int):
    connection = conn()
    cursor = connection.cursor()
    cursor.execute("UPDATE students SET name = %s, age = %s, class_id = %s WHERE id = %s;", (name, age, class_id, student_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "student updated"}