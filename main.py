from fastapi import FastAPI, HTTPException
import sqlite3

from database import create_table, get_connection
from models import Student


app = FastAPI(title="Student Database CRUD Application")


# Create the database table when the application starts
@app.on_event("startup")
def startup():
    create_table()


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to Student Database CRUD Application!"
    }


# CREATE: Add a new student
@app.post("/students", status_code=201)
def add_student(student: Student):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO students
            (name, date_of_birth, email, phone, course)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student.name,
                student.date_of_birth.isoformat(),
                str(student.email),
                student.phone,
                student.course,
            ),
        )

        connection.commit()

        return {
            "message": "Student added successfully",
            "student_id": cursor.lastrowid,
        }

    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(
                status_code=409,
                detail="A student with this email already exists",
            )

        raise HTTPException(
            status_code=400,
            detail="Could not add student because of a database constraint",
        )

    finally:
        connection.close()


# READ: Get all students
@app.get("/students")
def get_students():
    connection = get_connection()

    try:
        cursor = connection.execute(
            "SELECT * FROM students ORDER BY id"
        )

        students = cursor.fetchall()

        return [dict(student) for student in students]

    finally:
        connection.close()


# SEARCH: Search students by name or course
# IMPORTANT: Keep this route before /students/{student_id}
@app.get("/students/search")
def search_students(
    name: str | None = None,
    course: str | None = None,
):
    connection = get_connection()

    try:
        query = "SELECT * FROM students WHERE 1=1"
        parameters = []

        if name:
            query += " AND name LIKE ?"
            parameters.append(f"%{name}%")

        if course:
            query += " AND course LIKE ?"
            parameters.append(f"%{course}%")

        query += " ORDER BY id"

        cursor = connection.execute(query, parameters)
        students = cursor.fetchall()

        return [dict(student) for student in students]

    finally:
        connection.close()


# READ: Get one student using their ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,),
        )

        student = cursor.fetchone()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        return dict(student)

    finally:
        connection.close()


# UPDATE: Update an existing student
@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE students
            SET name = ?,
                date_of_birth = ?,
                email = ?,
                phone = ?,
                course = ?
            WHERE id = ?
            """,
            (
                student.name,
                student.date_of_birth.isoformat(),
                str(student.email),
                student.phone,
                student.course,
                student_id,
            ),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        connection.commit()

        return {
            "message": "Student updated successfully",
            "student_id": student_id,
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="This email is already used by another student",
        )

    finally:
        connection.close()


# DELETE: Delete a student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        connection.commit()

        return {
            "message": "Student deleted successfully",
            "student_id": student_id,
        }

    finally:
        connection.close()