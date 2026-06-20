from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

import json
import os

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique identifier for the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="The name of the patient")]
    city: Annotated[str, Field(..., description="The city where the patient resides")]
    age: Annotated[int, Field(..., gt=0, lt=150, description="The age of the patient")]
    gender: Annotated[Literal["Male", "Female", "Other"], Field(..., description="The gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="The height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="The weight of the patient in kilograms")]

    @computed_field
    @property
    def bmi(self) -> float:
        if self.height == 0:
            return 0
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None, description="The name of the patient")]
    city: Annotated[Optional[str], Field(None, description="The city where the patient resides")]
    age: Annotated[Optional[int], Field(None, gt=0, lt=150, description="The age of the patient")]
    gender: Annotated[Optional[Literal["Male", "Female", "Other"]], Field(None, description="The gender of the patient")]
    height: Annotated[Optional[float], Field(None, gt=0, description="The height of the patient in meters")]
    weight: Annotated[Optional[float], Field(None, gt=0, description="The weight of the patient in kilograms")]

#1 loading data from json file
def load_data():
    with open('patients.json', 'r') as f:
        return json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

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

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data and check if patient with the same ID already exists
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    # add the new patient to the data dictionary
    data[patient.id] = patient.model_dump(exclude={'id'})
    
    # save the updated data back to the JSON file
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": patient.model_dump()})

@app.put('/edit/{patient_id}')
def edit_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # update the existing patient data with the new values
    existing_patient = data[patient_id]
    updated_patient = patient_update.model_dump(exclude_unset=True)
    # existing_patient.update(updated_patient)
    
    for key, value in updated_patient.items():
        existing_patient[key] = value

    existing_patient['id'] = patient_id  # Ensure the ID remains unchanged
    patient_obj = Patient(**existing_patient)  # Create a Patient object to compute BMI and verdict
    existing_patient = patient_obj.model_dump(exclude={'id'}) # Update existing_patient with the computed fields

    data[patient_id] = existing_patient

    # save the updated data back to the JSON file
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully", "patient": patient_obj.model_dump()})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})