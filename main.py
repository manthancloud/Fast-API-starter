from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
import os

app = FastAPI()

class patient(BaseModel):
    id: Annotated[str, Field(..., description='Id of patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='name of patient')]
    city: Annotated[str, Field(..., description='city where patient lives')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of patient')]
    gender: Annotated[Literal['Male', 'Female', 'others'], Field(..., description='gender of patient')]
    height: Annotated[float, Field(..., gt=0, description='height of patient')]
    weight: Annotated[float, Field(..., gt=0, description='weight of patient')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi < 25:
            return 'normal'
        elif self.bmi < 30:
            return 'normal'
        else:
            return 'obessed'

class patient_update(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]   
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]     
    height: Annotated[Optional[int], Field(default=None, gt=0)]
    weight: Annotated[Optional[int], Field(default=None, gt=0)]


def load_data():
    # Create the file with an empty JSON object if it doesn't exist
    if not os.path.exists('patients.json'):
        with open('patients.json', 'w') as f:
            json.dump({}, f)
            
    try:
        with open('patients.json', 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is empty or corrupted, return an empty dict
        return {}

def save_data(data):
    with open('patients.json', 'w') as f:  # Make sure mode is 'w' (write), not 'r'
        json.dump(data, f, indent=4)


@app.get("/")
def hello():
    return {"messege": "Hello World"}

@app.get("/about")
def about():
    return {'messege': 'uvicorn is started on uvicorn'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='patients are not fouund')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='sort on basis of height, weight or bim'), order: str = Query('asc', description='sort in asc or dsc order')):
    valid_fields = ['height', 'weight', 'bim']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail=f'Invalid order select between asc and desc')
    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail='patient already exist')

    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={'messege': 'patient created successfully'})

@app.put('/edit/{patient_id}')
def Update_patient(patient_id: str, patient_update: patient_update):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient not found')

    # Note: Use patient_id instead of patient.id here
    existing_data = data[patient_id]
    update_data = patient_update.model_dump(exclude_unset=True)
    existing_data.update(update_data)

    data[patient_id] = existing_data

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient updated successfully'})



