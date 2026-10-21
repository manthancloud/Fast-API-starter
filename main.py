from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open ('patients.json', 'r') as f:
        data = json.load(f)

    return data


@app.get("/")
def hello():
    return {"messege" : "Hello  World"}

@app.get("/about")
def about():
    return {'messege' : 'uvicorn is started on uvicorn'}

@app.get("/view")
def view():
    data = load_data()

    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id : str):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='patients are not fouund')

@app.get('/sort')
def sort_patients(sort_by : str = Query(..., description='sort on basis of height, weight or bim'), order : str = Query('asc', description='sort in asc or dsc order')):

    valid_fields = ['height', 'weight', 'bim']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail=f'Invalid order select between asc and desc')
    data = load_data()

    sort_order = True if order =='desc' else False

    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data



