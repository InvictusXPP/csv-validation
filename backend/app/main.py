from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.analysis import analyze_frame, parse_rules
from app.csv_reader import read_csv_upload

app = FastAPI(title="DataCheck API", version="1.0.0", description="CSV data quality analysis")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), rules: str | None = Form(default=None)) -> dict[str, Any]:
    frame, delimiter = await read_csv_upload(file)
    config = parse_rules(rules)
    return analyze_frame(frame, file.filename or "upload.csv", delimiter, config)
