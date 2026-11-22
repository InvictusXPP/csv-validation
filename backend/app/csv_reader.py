import csv
import io

import pandas as pd
from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE = 20 * 1024 * 1024


async def read_csv_upload(file: UploadFile) -> tuple[pd.DataFrame, str]:
    filename = file.filename or "upload.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(400, "Prześlij plik z rozszerzeniem .csv.")

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "Plik jest większy niż 20 MB.")
    if not content:
        raise HTTPException(400, "Plik jest pusty.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(400, "Nie można odczytać pliku. Zapisz CSV jako UTF-8.") from exc

    delimiter = detect_delimiter(text)
    try:
        frame = pd.read_csv(
            io.StringIO(text), sep=delimiter, dtype=object,
            keep_default_na=True, on_bad_lines="error",
        )
    except Exception as exc:
        raise HTTPException(400, f"Nie udało się odczytać CSV: {exc}") from exc

    validate_headers(frame)
    return frame, delimiter


def detect_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:65536], delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def validate_headers(frame: pd.DataFrame) -> None:
    if len(frame.columns) == 0:
        raise HTTPException(400, "Plik nie zawiera nagłówków kolumn.")
    frame.columns = [str(column).strip() for column in frame.columns]
    if any(not column for column in frame.columns):
        raise HTTPException(400, "Każda kolumna musi mieć nazwę.")
    if frame.columns.duplicated().any():
        raise HTTPException(400, "Nagłówki kolumn muszą być unikalne.")
