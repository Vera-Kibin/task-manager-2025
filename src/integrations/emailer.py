from datetime import date
from typing import Sequence
from src.integrations.smtp import SMTPClient

class TaskHistoryEmailer:
    def __init__(self, smtp: SMTPClient = None):
        self.smtp = smtp or SMTPClient()

    def send_task_history(self, email: str, task_title: str, events: Sequence[str]) -> bool:
        subject = f"Task History {date.today().isoformat()}"
        body = f'Task "{task_title}" events: {list(events)}'
        return self.smtp.send(subject, body, email)