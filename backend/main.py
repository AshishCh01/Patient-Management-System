from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

import json
import os

#1
def load_data():
    with open('patients.json', 'r') as f:
        return json.load(f)
    return data

@app.get("/")
def read_root():    
    return {"message": "Patient Management System API"}

@app.get("/about")
def read_about():
    return {"message": "This is the Patient Management System API."}

@app.get("/view")
def view():
    data = load_data()
    return data

