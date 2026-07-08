import json

from src.audit import AUDIT_DIR, write_audit_event


def test_write_audit_event_creates_json_file(tmp_path, monkeypatch):
    monkeypatch.setattr("src.audit.AUDIT_DIR", tmp_path)
    audit_id = write_audit_event("claim_assessment", {"status": "ok"})
    audit_file = tmp_path / f"{audit_id}.json"

    assert audit_file.exists()
    payload = json.loads(audit_file.read_text(encoding="utf-8"))
    assert payload["event_type"] == "claim_assessment"
    assert payload["payload"] == {"status": "ok"}
    assert payload["audit_id"] == audit_id
