from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional, Literal, Annotated
from datetime import datetime, timezone
import json
import os

DATA_FILE = "students.json"

class StudentCreate(BaseModel):
    name: str
    email: str
    age: Annotated[int, Field(gt=10, lt=100)]
    department: Optional[str] = None
    CGPA: float

class Student(StudentCreate):
    id: Annotated[UUID, Field(default_factory=uuid4)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4, default=str)

app = FastAPI(title="Student Management")


@app.post("/create_student")
def create_student(student: StudentCreate):
    students = load_data()
    # Duplicate email check
    if any(s["email"] == student.email for s in students):
        raise HTTPException(status_code=400, detail="Email already exists")
    if len(student.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters long")
    
    new_student = Student(**student.dict())
    students.append(new_student.dict())
    save_data(students)
    return {"message": "Student created successfully", "student": new_student}


@app.get("/get_student/{student_id}")
def get_student(student_id: UUID):
    students = load_data()
    student = next((s for s in students if s["id"] == str(student_id)), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/search_students")
def search_students(
    name: Optional[str] = None,
    email: Optional[str] = None,
    department: Optional[str] = None,
    sort_by_age: Optional[Literal["asc", "desc"]] = None,
    sort_by_name: Optional[Literal["asc", "desc"]] = None
):
    students = load_data()
    
    if name:
        students = [s for s in students if name.lower() in s["name"].lower()]
    if email:
        students = [s for s in students if s["email"] == email]
    if department:
        students = [s for s in students if s.get("department") and department.lower() in s["department"].lower()]
    
    if sort_by_age:
        students.sort(key=lambda x: x["age"], reverse=(sort_by_age == "desc"))
    if sort_by_name:
        students.sort(key=lambda x: x["name"].lower(), reverse=(sort_by_name == "desc"))
    
    return students


@app.get("/stats")
def get_stats():
    students = load_data()
    total_students = len(students)
    if total_students == 0:
        return {"message": "No students found!"}
    
    avg_age = sum(s["age"] for s in students) / total_students
    department_count = {}
    for s in students:
        dept = s.get("department", "Not Specified")
        department_count[dept] = department_count.get(dept, 0) + 1
    
    return {"total_students": total_students, "average_age": avg_age, "department_count": department_count}


@app.put("/update_student/{student_email}")
def update_student(student_email: str, student_update: StudentCreate):
    students = load_data()
    student = next((s for s in students if s["email"] == student_email), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student["email"] != student_update.email and any(s["email"] == student_update.email for s in students):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    student.update(student_update.dict())
    save_data(students)
    return {"message": "Student updated successfully", "student": student}

@app.delete("/delete_student/{student_email}")
def delete_student(student_email: str):
    students = load_data()
    student = next((s for s in students if s["email"] == student_email), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    students.remove(student)
    save_data(students)
    return {"message": "Student deleted successfully"}
