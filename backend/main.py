from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

import json
import os

#1 loading data from json file
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

@app.get('/patients/{patient_id}')
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve")):
    # load all the patient data and find the patient with the given ID
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else:        
        raise HTTPException(status_code=404, detail="Patient not found")
    

# query parameter example: /sort?sort_by=height&order=asc
@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description="Sort on the basis of height, weight, or age"), 
                  order: str = Query('asc', description="Order of sorting: 'asc' for ascending, 'desc' for descending")):
    valid_fields = ['height', 'weight', 'age']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of {valid_fields}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=False if order == 'asc' else True)
    return sorted_data