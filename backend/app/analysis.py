import json
from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import HTTPException


def parse_rules(raw_rules: str | None) -> dict[str, Any]:
    try:
        rules = json.loads(raw_rules) if raw_rules else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "Reguły muszą być poprawnym obiektem JSON.") from exc
    if not isinstance(rules, dict):
        raise HTTPException(400, "Reguły muszą być poprawnym obiektem JSON.")
    return rules


def analyze_frame(frame: pd.DataFrame, filename: str, delimiter: str, rules: dict[str, Any]) -> dict[str, Any]:
    issues = find_duplicate_issues(frame)
    issues.extend(find_missing_value_issues(frame))
    issues.extend(find_missing_column_issues(frame, rules))

    column_stats = []
    column_rules = rules.get("columns", {})
    if not isinstance(column_rules, dict):
        column_rules = {}
    for column_name in frame.columns:
        rule = column_rules.get(column_name, {})
        column_issues, stats = analyze_column(frame[column_name], column_name, rule)
        issues.extend(column_issues)
        column_stats.append(stats)

    return build_report(frame, filename, delimiter, issues, column_stats)


def find_duplicate_issues(frame: pd.DataFrame) -> list[dict[str, Any]]:
    duplicate_rows = frame.index[frame.duplicated(keep="first")][:500]
    return [make_issue(int(row) + 2, None, "duplicate", "warning", None, "Powielony rekord") for row in duplicate_rows]


def find_missing_value_issues(frame: pd.DataFrame) -> list[dict[str, Any]]:
    issues = []
    for column_name in frame.columns:
        missing = frame[column_name].isna() | frame[column_name].astype(str).str.strip().eq("")
        for row in frame.index[missing][:500]:
            issues.append(make_issue(int(row) + 2, column_name, "missing", "warning", None, "Brak wartości"))
    return issues


def find_missing_column_issues(frame: pd.DataFrame, rules: dict[str, Any]) -> list[dict[str, Any]]:
    required = rules.get("required_columns", [])
    if not isinstance(required, list):
        return []
    missing = [name for name in required if name not in frame.columns]
    return [make_issue(None, name, "missing_column", "error", None, "Brak wymaganej kolumny") for name in missing]


def analyze_column(series: pd.Series, column_name: str, rule: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not isinstance(rule, dict):
        rule = {}
    clean_values = series.dropna().astype(str).str.strip()
    clean_values = clean_values[clean_values != ""]
    detected_type = infer_type(series)
    expected_type = rule.get("type", detected_type)
    numeric_values = parse_numeric_values(series)

    issues = find_invalid_value_issues(series, column_name, expected_type, numeric_values)
    if expected_type == "number":
        issues.extend(find_range_issues(series, column_name, numeric_values, rule))
        issues.extend(find_outlier_issues(series, column_name, numeric_values))

    stats = {
        "name": column_name,
        "detected_type": detected_type,
        "expected_type": expected_type,
        "missing": int((series.isna() | series.astype(str).str.strip().eq("")).sum()),
        "unique": int(clean_values.nunique()),
        "sample": clean_values.head(3).tolist(),
    }
    if detected_type == "number" and numeric_values.notna().any():
        stats.update({
            "min": json_safe(numeric_values.min()),
            "max": json_safe(numeric_values.max()),
            "mean": round(float(numeric_values.mean()), 2),
        })
    return issues, stats


def find_invalid_value_issues(series: pd.Series, column_name: str, expected_type: str, numeric: pd.Series) -> list[dict[str, Any]]:
    if expected_type not in ("number", "date"):
        return []
    parsed = numeric if expected_type == "number" else pd.to_datetime(series, errors="coerce", format="mixed")
    populated = series.notna() & series.astype(str).str.strip().ne("")
    bad_rows = series.index[populated & parsed.isna()][:500]
    label = "liczby" if expected_type == "number" else "daty"
    return [
        make_issue(int(row) + 2, column_name, f"invalid_{expected_type}", "error", str(series.loc[row]), f"Nieprawidłowa wartość: oczekiwano {label}")
        for row in bad_rows
    ]


def find_range_issues(series: pd.Series, column_name: str, numeric: pd.Series, rule: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    for bound in ("min", "max"):
        limit = parse_bound(rule.get(bound))
        if limit is None:
            continue
        outside = numeric.notna() & (numeric < limit if bound == "min" else numeric > limit)
        for row in series.index[outside][:500]:
            issues.append(make_issue(int(row) + 2, column_name, "out_of_range", "warning", str(series.loc[row]), f"Wartość poza zakresem {bound}={limit:g}"))
    return issues


def find_outlier_issues(series: pd.Series, column_name: str, numeric: pd.Series) -> list[dict[str, Any]]:
    valid_values = numeric.dropna()
    if len(valid_values) < 4:
        return []
    first_quartile, third_quartile = valid_values.quantile(.25), valid_values.quantile(.75)
    spread = third_quartile - first_quartile
    is_outlier = (numeric < first_quartile - 1.5 * spread) | (numeric > third_quartile + 1.5 * spread)
    return [
        make_issue(int(row) + 2, column_name, "outlier", "info", str(series.loc[row]), "Wartość odstająca (reguła IQR)")
        for row in series.index[is_outlier.fillna(False)][:100]
    ]


def build_report(frame: pd.DataFrame, filename: str, delimiter: str, issues: list[dict[str, Any]], column_stats: list[dict[str, Any]]) -> dict[str, Any]:
    errors = sum(issue["severity"] == "error" for issue in issues)
    warnings = sum(issue["severity"] == "warning" for issue in issues)
    informational = sum(issue["severity"] == "info" for issue in issues)
    score = max(0, round(100 - errors * 8 - warnings * 2 - informational))
    delimiter_names = {",": "przecinek", ";": "średnik", "\t": "tabulator", "|": "pionowa kreska"}
    return {
        "filename": filename,
        "delimiter": delimiter_names.get(delimiter, delimiter),
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "score": score,
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "issues": len(issues),
            "duplicates": sum(issue["type"] == "duplicate" for issue in issues),
            "missing_cells": sum(column["missing"] for column in column_stats),
        },
        "column_stats": column_stats,
        "preview": [{name: json_safe(value) for name, value in row.items()} for row in frame.head(100).to_dict(orient="records")],
        "issues": issues[:2000],
    }


def infer_type(series: pd.Series) -> str:
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]
    if values.empty:
        return "empty"
    numeric = pd.to_numeric(values.str.replace(",", "", regex=False), errors="coerce")
    if numeric.notna().mean() >= 0.85:
        return "number"
    dates = pd.to_datetime(values, errors="coerce", format="mixed", dayfirst=False)
    if dates.notna().mean() >= 0.85:
        return "date"
    booleans = values.str.lower().isin(["true", "false", "yes", "no", "0", "1"])
    if booleans.mean() >= 0.85:
        return "boolean"
    return "text"


def parse_numeric_values(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip().str.replace(",", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def parse_bound(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def make_issue(row: int | None, column: str | None, issue_type: str, severity: str, value: Any, message: str) -> dict[str, Any]:
    return {"row": row, "column": column, "type": issue_type, "severity": severity, "value": value, "message": message}
