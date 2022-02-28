#!/usr/bin/env uvicorn main:app --reload

import json
from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from boatsense import CFG, Data, crud, model, schema
from boatsense.db import SessionLocal, engine

model.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.exception_handler(IntegrityError)
async def validation_exception_handler(request, exc):
    raise PlainTextResponse(status_code=404, detail="Integrity Constraint")

@app.get("/", response_model=schema.Message)
async def root():
    msg = {"msg": "Hello"}
    return msg

@app.get("/date/{name}/", response_model=schema.DateInfo)
def get_date(name: str , db: Session = Depends(get_db)):
    item = crud.get_date(db, name)
    return item

#@app.get("/dates/", response_model=list[schema.DateInfo])
#def get_dates(db: Session = Depends(get_db)):
#    items = crud.get_dates(db)
#    return items

@app.post("/updates/", response_model=schema.Message)
def do_updates(updates: list[schema.Update], db: Session = Depends(get_db)):
    s = True
    for item in updates:
        if item:
            print(type(item))
        else:
            s = False
    if s:
        msg = {'msg': 'success'}
    else:
        msg = {'msg': 'fail'}
    return msg
