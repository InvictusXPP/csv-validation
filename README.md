# DataCheck

DataCheck is a local CSV quality analyzer with a React/Vite interface and a FastAPI backend.

## Requirements

- Python 3.10+
- Node.js 18+

## Run locally

Start the API:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal, start the web app:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal. The API runs at `http://localhost:8000`; interactive API docs are at `/docs`.

## Analysis

Upload UTF-8 or UTF-8-BOM CSV files up to 20 MB. The API detects common delimiters, previews up to 100 rows, and reports missing cells, fully duplicated rows, likely type mismatches, invalid dates and numbers, and numeric outliers using the IQR rule. Column rules can be passed as JSON to require columns, select types, and set numeric bounds. Analysis is in memory; uploaded files are not persisted.

## API

- `POST /api/analyze` multipart fields: `file`, optional `rules` (JSON string)
- `GET /api/health`

Rules example:

```json
{
  "required_columns": ["email", "amount"],
  "columns": {
    "amount": {"type": "number", "min": 0, "max": 10000},
    "created_at": {"type": "date"}
  }
}
```

Download the analysis as JSON from the result screen.
