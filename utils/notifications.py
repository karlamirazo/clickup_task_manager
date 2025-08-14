from typing import Dict, List, Tuple


async def send_email_async(recipients: List[str], subject: str, text_body: str, html_body: str) -> None:
    return None


async def send_telegram_async(recipients: List[str], message: str) -> None:
    return None


async def send_sms_async(recipients: List[str], message: str) -> None:
    return None


def build_task_email_content(action: str, task_id: str, name: str, status: str, priority: int, assignee_name: str | None, due_date_iso: str | None) -> Tuple[str, str, str]:
    subject = f"Task {action}: {name}"
    text_body = f"Task {action}: {name} (ID: {task_id})"
    html_body = text_body
    return subject, text_body, html_body


def build_task_telegram_message(action: str, task_id: str, name: str, status: str, priority: int, assignee_name: str | None, due_date_iso: str | None) -> str:
    return f"Task {action}: {name} (ID: {task_id})"


def build_task_sms_message(action: str, task_id: str, name: str, status: str, priority: int, assignee_name: str | None, due_date_iso: str | None) -> str:
    return f"Task {action}: {name} (ID: {task_id})"


def extract_contacts_from_custom_fields(custom_fields: Dict) -> Tuple[List[str], List[str], List[str]]:
    emails: List[str] = []
    telegrams: List[str] = []
    sms: List[str] = []
    for key, value in (custom_fields or {}).items():
        if isinstance(value, str) and "@" in value:
            emails.append(value)
        if isinstance(value, str) and value.isdigit() and len(value) >= 8:
            sms.append(value)
    return emails, telegrams, sms


def log_notification(channel: str, recipient: str, message: str) -> None:
    return None


