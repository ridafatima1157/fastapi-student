from fastapi import FastAPI, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open("students.json", "r") as f:
        return json.load(f)
    
# 1)Endpoint to retrieve all students data
@app.get("/students")
def get_all_students():
    data = load_data()
    return {"status": 200, "students": data}

# 2) Endpoint to view a student by id
@app.get("/students/{student_key}")
def get_student(student_key: str):
    data = load_data()
    if student_key in data:
        return {"status": 200, "student": data[student_key]}
    raise HTTPException(status_code=404, detail="Student not found")

# 3) Endpoint to sort students by CGPA
@app.get("/students/sort")
def sort_students(order: str = Query("asc", enum=["asc", "desc"])):
    data = load_data()
    students = list(data.values())
    if order == "asc":
        students = sorted(students, key=lambda x: x["CGPA"])
    else:
        students = sorted(students, key=lambda x: x["CGPA"], reverse=True)
    return {"status": 200, "sorted_students": students}
