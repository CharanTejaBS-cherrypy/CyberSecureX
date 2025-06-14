from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.utils import scanner, lan_scan, password_checker, file_share

import time
import os

from .utils.lan_scan import scan_lan

# ------------------- App Setup -------------------

app = FastAPI()
from pathlib import Path

base_dir = Path(__file__).resolve().parent
static_dir = base_dir / "static"
upload_dir = base_dir / "uploads"
templates_dir = base_dir / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
if upload_dir.exists():
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

templates = Jinja2Templates(directory=templates_dir)


# ------------------- DB Init -------------------

file_share.init_db()

# ------------------- Routes -------------------


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/scanner", response_class=HTMLResponse)
async def scanner_page(request: Request):
    return templates.TemplateResponse("scanner.html", {"request": request})


@app.get("/lan", response_class=HTMLResponse)
async def lan_page(request: Request):
    return templates.TemplateResponse("lan.html", {"request": request})


@app.get("/password-checker", response_class=HTMLResponse)
async def password_page(request: Request):
    return templates.TemplateResponse("password.html", {"request": request})


@app.get("/secure-share", response_class=HTMLResponse)
async def secure_share_page(request: Request):
    with file_share.sqlite3.connect(file_share.DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT token, filename, downloads, max_downloads, expires_at FROM links")
        links = [
            {
                "token": row[0],
                "filename": row[1],
                "downloads": row[2],
                "max_downloads": row[3],
                "expired": time.time() > row[4]
            }
            for row in cursor.fetchall()
        ]
    return templates.TemplateResponse("secure_share.html", {"request": request, "links": links})

# ------------------- API Endpoints -------------------

# SCANNER


class ScanRequest(BaseModel):
    target: str


@app.post("/scan")
async def scan_site(data: ScanRequest):
    return await scanner.scan_website(data.target)

# LAN DISCOVERY


@app.get("/scan-lan")
async def scan_lan_api():
    try:
        result = scan_lan()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# PASSWORD CHECKER


class PasswordCheckRequest(BaseModel):
    password: str


@app.post("/check-password")
async def check_password(data: PasswordCheckRequest):
    strength = password_checker.evaluate_strength(data.password)
    pwned_count = await password_checker.check_pwned(data.password)
    return {"strength": strength, "breached": pwned_count > 0, "pwned_count": pwned_count}

# FILE UPLOAD


@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    expiry_minutes: int = Form(...),
    max_downloads: int = Form(...),
    password: str = Form(None)
):
    token = file_share.save_file(file, expiry_minutes, max_downloads, password)
    return RedirectResponse(url="/secure-share", status_code=303)

# DOWNLOAD FORM PAGE


@app.get("/file/{token}", response_class=HTMLResponse)
async def download_form(request: Request, token: str):
    return templates.TemplateResponse("download_form.html", {"request": request, "token": token})

# DOWNLOAD FILE POST


@app.post("/file/{token}")
async def download_file(request: Request, token: str, password: str = Form("")):
    link = file_share.get_link(token)

    if not link:
        raise HTTPException(status_code=404, detail="Invalid or expired link.")

    filename, filepath, expires_at, max_downloads, downloads, stored_password = link

    if time.time() > expires_at:
        file_share.delete_link(token)
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=410, detail="Link has expired.")

    if stored_password and stored_password != password:
        return templates.TemplateResponse("download_form.html", {
            "request": request,
            "token": token,
            "error": "Invalid password"
        })

    if downloads >= max_downloads:
        file_share.delete_link(token)
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=403, detail="Download limit exceeded.")

    file_share.increment_downloads(token)
    return FileResponse(path=filepath, filename=filename, media_type="application/octet-stream")
