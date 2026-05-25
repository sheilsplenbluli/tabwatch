from typing import Dict, List, Optional
from app.models.custom_report import CustomReport

_store: Dict[str, CustomReport] = {}


def add_report(report: CustomReport) -> None:
    _store[report.report_id] = report


def get_report(report_id: str) -> Optional[CustomReport]:
    return _store.get(report_id)


def get_reports_for_user(user_id: str) -> List[CustomReport]:
    return [r for r in _store.values() if r.user_id == user_id]


def update_report(report: CustomReport) -> None:
    if report.report_id not in _store:
        raise KeyError(f"Report {report.report_id} not found")
    _store[report.report_id] = report


def delete_report(report_id: str) -> bool:
    if report_id in _store:
        del _store[report_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()
