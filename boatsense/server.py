#!/usr/bin/env uvicorn main:app --reload

from fastapi import Depends, FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"msg": "Hello"}
