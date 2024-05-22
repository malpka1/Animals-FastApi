from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import databases
from celery_worker import save_to_db

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Animal(BaseModel):
    name: str
    description: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    query = "SELECT * FROM animals"
    animals = await database.fetch_all(query)
    return templates.TemplateResponse("index.html", {"request": request, "animals": animals})

@app.get("/sync_add", response_class=HTMLResponse)
async def get_sync_form(request: Request):
    return templates.TemplateResponse("sync_add.html", {"request": request})

@app.post("/sync_add")
async def sync_add(name: str = Form(...), description: str = Form(...)):
    query = "INSERT INTO animals(name, description) VALUES (:name, :description)"
    await database.execute(query, values={"name": name, "description": description})
    return RedirectResponse("/", status_code=303)

@app.get("/async_add", response_class=HTMLResponse)
async def get_async_form(request: Request):
    return templates.TemplateResponse("acync_add.html", {"request": request})

@app.post("/async_add")
async def async_add(background_tasks: BackgroundTasks, name: str = Form(...), description: str = Form(...)):
    background_tasks.add_task(save_to_db, name, description)
    return {"message": "Animal added successfully!"}
