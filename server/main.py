from typing import List
from datetime import datetime, timezone
from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import DB_LIMIT, crud, model, schema
from .db import SessionLocal, engine

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

@app.get("/")
async def root():
    return {"msg": "Hello"}

def get_dates(db, base, skip, limit):
    return crud.get_dates(db, base, skip=skip, limit=limit)

def get_date(db, base, name):
    return crud.get_date(db, base, name)

def set_date(db, base, name, asat_real):
    asat = datetime.fromtimestamp(asat_real)
    asat = asat.astimezone(tz=timezone.utc)
    return crud.set_date(db, base, name, asat)

@app.get("/updates/", response_model=List[schema.Update])
def get_updates(skip: int = 0, limit: int = DB_LIMIT, db: Session = Depends(get_db)):
    return get_dates(db, model.Update, skip, limit)

@app.get("/update/{name}", response_model=schema.Update)
def get_update(name: str , db: Session = Depends(get_db)):
    return get_date(db, model.Update, name)

@app.post("/update/{name}/{asat_real}", response_model=schema.Update)
def add_update(name: str, asat_real: float, db: Session = Depends(get_db)):
    return set_date(db, model.Update, name, asat_real)

@app.get("/reads/", response_model=List[schema.Read])
def get_reads(skip: int = 0, limit: int = DB_LIMIT, db: Session = Depends(get_db)):
    return get_dates(db, model.Read, skip, limit)

@app.get("/read/{name}", response_model=schema.Read)
def get_read(name: str , db: Session = Depends(get_db)):
    return get_date(db, model.Read, name)

@app.post("/read/{name}/{asat_real}", response_model=schema.Read)
def add_read(name: str, asat_real: float, db: Session = Depends(get_db)):
    return set_date(db, model.Read, name, asat_real)
