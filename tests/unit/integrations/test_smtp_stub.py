from src.integrations.smtp import SMTPClient

def test_smtp_stub_returns_false():
    assert SMTPClient.send("subj", "body", "a@b.c") is False