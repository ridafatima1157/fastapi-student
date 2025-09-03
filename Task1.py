from fastapi import FastAPI

app = FastAPI()

student = {
    "id": "BSE223046",
    "name": "Rida Fatima",
    "field_of_study": "Software Engineering"
}

@app.get("/")
def hello():
    return {
        "student_details": student
    }
