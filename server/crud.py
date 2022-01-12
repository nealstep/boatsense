from datetime import datetime
from sqlalchemy.orm import Session

from . import DB_LIMIT, model, schema
from .db import Base

def get_dates(db: Session, base: Base, skip: int=0, limit: int=DB_LIMIT):
    return db.query(base).offset(skip).limit(limit).all()

def get_date(db: Session, base: Base, name: str):
    return db.query(base).filter(base.name == name).first()

def set_date(db: Session, base: Base, name: str, asat: datetime):
    print("here")
    item = base(name=name, asat=asat)
    db.merge(item)
    db.commit()
    return item
