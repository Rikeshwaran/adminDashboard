from fastapi import FastAPI, Form, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from typing import List
import json
import os
import uuid
app = FastAPI()

# Styles

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database 

DATABASE_URL = "mysql+mysqlconnector://root:2004@localhost/admindashboard"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, bind=engine)
from models.models import Base, Project
Base.metadata.create_all(bind=engine)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#login in functions 

@app.get("/", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/admin")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":
        return templates.TemplateResponse("admin.html", {"request": request, "username": username})
    else:
        return templates.TemplateResponse("oops.html", {"request": request})
@app.post("/logout")
async def logout():
    return RedirectResponse(url="/", status_code=303)




@app.post("/submit")
async def submit_project(
    request: Request,
    name: str = Form(...),
    entry_id: str = Form(...),
    status: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    files: List[UploadFile] = File(...),
    planned_bys: List[str] = Form(...),
    planned_ats: List[str] = Form(...),
    revision_ids: List[str] = Form(...)
):
    db = SessionLocal()
    try:
        file_paths = []
        for file in files:
            if file.filename:
                filename = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, filename)
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
                file_paths.append(filename)
        project = Project(
            name=name,
            entry_id=entry_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            file_paths=file_paths,
            planned_bys=planned_bys,
            planned_ats=planned_ats,
            revision_ids=revision_ids
        )
        db.add(project)
        db.commit()
        return {"message": "Project submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=jsonable_encoder({"error": str(e)})
        )
    finally:
        db.close()
@app.get("/data")
async def get_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "entry_id": p.entry_id,
                "status": p.status,
                "start_date": str(p.start_date),
                "end_date": str(p.end_date),
                "file_paths": p.file_paths or [],
                "planned_bys": p.planned_bys or [],
                "planned_ats": p.planned_ats or [],
                "revision_ids": p.revision_ids or []
            }
            for p in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
@app.put("/update/{project_id}")
async def update_project(
    project_id: int,
    request: Request,
    name: str = Form(...),
    entry_id: str = Form(...),
    status: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    files: List[UploadFile] = File([]),
    planned_bys: List[str] = Form(...),
    planned_ats: List[str] = Form(...),
    revision_ids: List[str] = Form(...),
    existing_files: str = Form("[]") 
):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        existing_files_list = json.loads(existing_files)
        file_paths = existing_files_list.copy()
        for i, file in enumerate(files):
            if file.filename:
                filename = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, filename)
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
                if i < len(file_paths):
                    file_paths[i] = filename
                else:
                    file_paths.append(filename)
        project.name = name
        project.entry_id = entry_id
        project.status = status
        project.start_date = start_date
        project.end_date = end_date
        project.file_paths = file_paths
        project.planned_bys = planned_bys
        project.planned_ats = planned_ats
        project.revision_ids = revision_ids
        db.commit()
        return {"message": "Project updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=jsonable_encoder({"error": str(e)})
        )
    finally:
        db.close()
@app.delete("/delete/{project_id}")
async def delete_project(project_id: int):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            db.delete(project)
            db.commit()
        return {"message": "Project deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# the other ports not working well use this port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)
    
