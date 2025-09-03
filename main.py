from fastapi import FastAPI

app=FastAPI()

student={"id":"BSE223046","name":"Rida Fatima","field of study":"Software Engineeing"}

@app.get("/")
def hello():
    return student
