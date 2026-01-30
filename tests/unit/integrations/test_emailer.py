from datetime import date
from src.integrations.emailer import TaskHistoryEmailer

def test_email_success_and_call_args(mocker):
    mock_send = mocker.patch("src.integrations.emailer.SMTPClient.send", return_value=True)
    ok = TaskHistoryEmailer().send_task_history("a@b.c", "Feature A", ["CREATED", "ASSIGNED"])
    assert ok is True
    mock_send.assert_called_once()
    subject, body, to_ = mock_send.call_args[0]
    assert subject == f"Task History {date.today().isoformat()}"
    assert 'Feature A' in body and "CREATED" in body and "ASSIGNED" in body
    assert to_ == "a@b.c"

def test_email_failure_returns_false(mocker):
    mocker.patch("src.integrations.emailer.SMTPClient.send", return_value=False)
    assert TaskHistoryEmailer().send_task_history("x@y.z", "T", []) is False

def test_email_empty_events_body(mocker):
    mock_send = mocker.patch("src.integrations.emailer.SMTPClient.send", return_value=True)
    assert TaskHistoryEmailer().send_task_history("a@b.c", "T", []) is True
    _, body, _ = mock_send.call_args[0]
    assert 'events: []' in body

def test_email_raises_when_smtp_throws(mocker):
    import pytest
    mocker.patch("src.integrations.emailer.SMTPClient.send", side_effect=Exception("smtp down"))
    with pytest.raises(Exception, match="smtp down"):
        TaskHistoryEmailer().send_task_history("a@b.c", "T", ["CREATED"])