from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os  # <--- Added to handle directory creation

from routes import (
    backend_tech,
    client,
    frontend_tech,
    database_type,
    module_type,
    project_type,
    common_api,
    projects,
    modules,
    menu,
    project_users,
    tickets,
    login
)

app = FastAPI(title="Support Tool")

# --- 1. SETUP UPLOAD DIRECTORY ---
# Create the folder if it doesn't exist
os.makedirs("uploaded_files", exist_ok=True)

# --- 2. MOUNT STATIC & UPLOAD PATHS ---
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
# This exposes http://127.0.0.1:8000/uploaded_files/... to the web
app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://127.0.0.1",
    "https://resolvex.softcoretech.in",
    "http://resolvex.softcoretech.in",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# API ROUTERS
# -------------------------------------------------------------
app.include_router(login.router,        prefix="/api",              tags=["Authentication"])
app.include_router(backend_tech.router, prefix="/api/backend-tech", tags=["Backend Tech Stack"])
app.include_router(frontend_tech.router,prefix="/api/frontend-tech",tags=["Frontend Tech Stack"])
app.include_router(database_type.router,prefix="/api/database-type",tags=["Database Type"])
app.include_router(module_type.router,  prefix="/api/module-type",  tags=["Module Type"])
app.include_router(client.router,       prefix="/api/clients",      tags=["Client"])
app.include_router(project_type.router, prefix="/api/project-type", tags=["Project Type"])
app.include_router(common_api.router,   prefix="/api",       tags=["Common"])
app.include_router(projects.router,     prefix="/api/projects",     tags=["Projects"])
app.include_router(modules.router,      prefix="/api/modules",      tags=["Modules"])
app.include_router(menu.router,         prefix="/api/menu",         tags=["Menu"])
app.include_router(project_users.router,prefix="/api/project-users",tags=["Project Users"])
app.include_router(tickets.router,      prefix="/api/tickets",      tags=["Tickets"])

# -------------------------------------------------------------
# HTML PAGE ROUTES
# -------------------------------------------------------------

@app.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/register.html", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")

@app.get("/index.html", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/pages/backend-tech", response_class=HTMLResponse)
async def backend_tech_page(request: Request):
    return templates.TemplateResponse(request, "BackEndTech.html")

@app.get("/pages/frontend-tech", response_class=HTMLResponse)
async def frontend_tech_page(request: Request):
    return templates.TemplateResponse(request, "FrontEndTech.html")

@app.get("/pages/database-type", response_class=HTMLResponse)
async def database_type_page(request: Request):
    return templates.TemplateResponse(request, "DBType.html")

@app.get("/pages/module-type", response_class=HTMLResponse)
async def module_type_page(request: Request):
    return templates.TemplateResponse(request, "ModuleType.html")

@app.get("/pages/client", response_class=HTMLResponse)
async def client_page(request: Request):
    return templates.TemplateResponse(request, "Client.html")

@app.get("/pages/project-type", response_class=HTMLResponse)
async def project_type_page(request: Request):
    return templates.TemplateResponse(request, "ProjType.html")

@app.get("/pages/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    return templates.TemplateResponse(request, "Project.html")

@app.get("/pages/modules", response_class=HTMLResponse)
async def modules_page(request: Request):
    return templates.TemplateResponse(request, "Module.html")

@app.get("/pages/menu", response_class=HTMLResponse)
async def menu_page(request: Request):
    return templates.TemplateResponse(request, "menu.html")

@app.get("/pages/project_users", response_class=HTMLResponse)
async def project_users_page(request: Request):
    return templates.TemplateResponse(request, "ProjUsers.html")

@app.get("/pages/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request):
    return templates.TemplateResponse(request, "Tickets.html")

@app.get("/pages/changes", response_class=HTMLResponse)
async def changes_page(request: Request):
    return templates.TemplateResponse(request, "Changes.html")

# pages for the standalone change logs
@app.get("/pages/db-changes", response_class=HTMLResponse)
async def db_changes_page(request: Request):
    return templates.TemplateResponse(request, "db_changes.html")

@app.get("/pages/code-changes", response_class=HTMLResponse)
async def code_changes_page(request: Request):
    return templates.TemplateResponse(request, "code_changes.html")

@app.get("/pages/changes-report", response_class=HTMLResponse)
async def changes_report_page(request: Request):
    # read the changelog files if they exist
    db_text = ""
    code_text = ""
    try:
        with open("DBCHANGELOG.md", "r", encoding="utf-8") as f:
            db_text = f.read()
    except FileNotFoundError:
        db_text = "(No database changes logged yet)"
    try:
        with open("CHANGELOG.md", "r", encoding="utf-8") as f:
            code_text = f.read()
    except FileNotFoundError:
        code_text = "(No code changes logged yet)"

    return templates.TemplateResponse(
        request,
        "ChangesReport.html",
        {"db_log": db_text, "code_log": code_text}
    )

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "login.html")