from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
import os

app = FastAPI()

DATA_FILE = "students.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
class Student(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., gt=5, lt=100)
    roll_number: str
    grade: str | None = None
@app.post("/students/")
def add_student(student: Student):
    students = load_data()
    for s in students:
        if s["id"] == student.id:
            raise HTTPException(status_code=400, detail="ID already exists")
        if s["roll_number"] == student.roll_number:
            raise HTTPException(status_code=400, detail="Roll number already exists")

    students.append(student.dict())
    save_data(students)
    return {"message": "Student added successfully", "student": student}

@app.get("/students/")
def get_all_students():
    students = load_data()
    return {"students": students}

@app.get("/students/{id}")
def get_student(id: int):
    students = load_data()
    for s in students:
        if s["id"] == id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")
