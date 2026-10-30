import uuid

import pytest
from services.core import connect, profile_completion, gap_analysis, profile_analysis, verify_password, _password, recommendations, register, add_skill

def test_password_hash_roundtrip():
    hashed = _password("sample-password")
    assert verify_password("sample-password", hashed)
    assert not verify_password("incorrect", hashed)

def test_profile_completion_and_missing_fields():
    score, missing = profile_completion({}, [])
    assert score == 0
    assert "Skills" in missing

def test_skill_gap_uses_role_requirements():
    gaps = gap_analysis("Senior Software Engineer", [{"name":"Python","proficiency":"Advanced"}])
    python = next(row for row in gaps if row["skill"] == "Python")
    assert python["gap"] == 1
    assert python["priority"] == "Medium"

def test_recommendations_have_offline_fallback():
    recs = recommendations({"target_role":"Data Analyst"}, [])
    assert recs
    assert any("profile" in r["title"].lower() or "develop" in r["title"].lower() for r in recs)

def test_profile_analysis_bounded():
    result = profile_analysis({"target_role":"HR Manager","summary":"People operations"}, [])
    assert 0 <= result["score"] <= 100


def test_duplicate_skill_names_are_case_insensitive():
    email = f"skill-{uuid.uuid4().hex}@example.com"
    ok, _ = register("Skill Tester", email, "securepass123")
    assert ok

    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    created = add_skill(user_id, "Python", "Technical", "Advanced", 3)
    assert created[0]
    duplicate = add_skill(user_id, " python ", "Technical", "Advanced", 3)
    assert not duplicate[0]
    assert "already" in duplicate[1].lower()


def test_database_initialization_and_migration_idempotent():
    from services.core import init_db, connect
    # Calling init_db multiple times must be idempotent and non-destructive
    init_db()
    init_db()
    with connect() as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "users" in tables
        assert "sessions" in tables
        assert "password_resets" in tables


def test_unregistered_email_rejected_and_no_url(capsys):
    from services.core import request_password_reset
    ok, msg = request_password_reset("nonexistent-user-12345@domain.com")
    assert not ok
    assert "not registered" in msg.lower()
    captured = capsys.readouterr()
    assert "Password reset URL:" not in captured.out


def test_reset_url_printed_to_terminal(capsys):
    from services.core import register, request_password_reset
    email = f"print-test-{uuid.uuid4().hex[:8]}@example.com"
    register("Print Test", email, "InitialPass123")
    ok, msg = request_password_reset(email)
    assert ok
    captured = capsys.readouterr()
    assert "Password reset URL: http" in captured.out
    assert "?reset_token=" in captured.out


def test_password_reset_success_flow():
    from services.core import register, request_password_reset, connect, validate_reset_token, reset_password, login, verify_password
    email = f"reset-user-{uuid.uuid4().hex[:8]}@example.com"
    ok, _ = register("Reset User", email, "InitialPass123")
    assert ok

    # Request password reset
    ok_req, msg_req = request_password_reset(email)
    assert ok_req

    with connect() as db:
        user_row = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        reset_row = db.execute("SELECT * FROM password_resets WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_row["id"],)).fetchone()
        assert reset_row is not None
        assert reset_row["used"] == 0

    # Since raw token is hashed in DB, let's test validate_reset_token with valid token
    # To test direct token validation, we create a known token
    import secrets, hashlib
    raw_tok = secrets.token_urlsafe(32)
    tok_hash = hashlib.sha256(raw_tok.encode("utf-8")).hexdigest()
    from datetime import datetime, timedelta
    exp = (datetime.now() + timedelta(minutes=20)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,0,?)",
                   (user_row["id"], tok_hash, exp, datetime.now().isoformat()))

    # Validate token
    token_info = validate_reset_token(raw_tok)
    assert token_info is not None
    assert token_info["user_id"] == user_row["id"]
    assert token_info["email"] == email

    # Reset password
    ok_reset, msg_reset = reset_password(raw_tok, "NewSecurePassword456")
    assert ok_reset
    assert "successfully" in msg_reset.lower()

    # Old password fails, new password succeeds
    assert login(email, "InitialPass123") is None
    new_user = login(email, "NewSecurePassword456")
    assert new_user is not None
    assert new_user["email"] == email


def test_reset_token_invalidation_reuse_and_expiration():
    from services.core import register, connect, validate_reset_token, reset_password
    import secrets, hashlib
    from datetime import datetime, timedelta

    email = f"reuse-user-{uuid.uuid4().hex[:8]}@example.com"
    register("Reuse User", email, "InitialPass123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    # 1. Expired token
    raw_exp = secrets.token_urlsafe(32)
    hash_exp = hashlib.sha256(raw_exp.encode("utf-8")).hexdigest()
    past_time = (datetime.now() - timedelta(minutes=5)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,0,?)",
                   (user_id, hash_exp, past_time, past_time))
    assert validate_reset_token(raw_exp) is None
    ok_exp, _ = reset_password(raw_exp, "AnotherPass789")
    assert not ok_exp

    # 2. Used token
    raw_used = secrets.token_urlsafe(32)
    hash_used = hashlib.sha256(raw_used.encode("utf-8")).hexdigest()
    future_time = (datetime.now() + timedelta(minutes=20)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,1,?)",
                   (user_id, hash_used, future_time, datetime.now().isoformat()))
    assert validate_reset_token(raw_used) is None
    ok_used, _ = reset_password(raw_used, "AnotherPass789")
    assert not ok_used

    # 3. Invalid token
    assert validate_reset_token("completely-non-existent-token") is None


def test_password_change_invalidates_all_outstanding_reset_tokens():
    from services.core import register, connect, reset_password, validate_reset_token
    import secrets, hashlib
    from datetime import datetime, timedelta

    email = f"multi-token-{uuid.uuid4().hex[:8]}@example.com"
    register("Multi Token User", email, "InitialPass123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    tokens = [secrets.token_urlsafe(32) for _ in range(3)]
    future = (datetime.now() + timedelta(minutes=20)).isoformat()
    with connect() as db:
        for t in tokens:
            h = hashlib.sha256(t.encode("utf-8")).hexdigest()
            db.execute("INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,0,?)",
                       (user_id, h, future, datetime.now().isoformat()))

    # Reset password with token 0
    ok, _ = reset_password(tokens[0], "UpdatedPass321")
    assert ok

    # All tokens (including 1 and 2) must now be invalidated
    assert validate_reset_token(tokens[0]) is None
    assert validate_reset_token(tokens[1]) is None
    assert validate_reset_token(tokens[2]) is None


def test_rate_limiting_of_reset_requests():
    from services.core import register, request_password_reset, connect
    email = f"ratelimit-{uuid.uuid4().hex[:8]}@example.com"
    register("Rate Limit User", email, "InitialPass123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    # First request
    ok1, _ = request_password_reset(email)
    assert ok1
    with connect() as db:
        cnt1 = db.execute("SELECT COUNT(*) as c FROM password_resets WHERE user_id=?", (user_id,)).fetchone()["c"]
    assert cnt1 == 1

    # Second request immediately (within cooldown)
    ok2, msg2 = request_password_reset(email)
    assert not ok2
    assert "recently submitted" in msg2.lower()
    with connect() as db:
        cnt2 = db.execute("SELECT COUNT(*) as c FROM password_resets WHERE user_id=?", (user_id,)).fetchone()["c"]
    # Cooldown prevents inserting a new token row
    assert cnt2 == 1


def test_password_reset_email_failure_handled_safely(monkeypatch):
    from services.core import send_reset_email
    # When SMTP is unconfigured, returns False safely
    monkeypatch.setenv("SMTP_HOST", "")
    assert not send_reset_email("user@example.com", "http://localhost:8501/?reset_token=abc")

    # When SMTP server connection fails, catches exception and returns False without crashing
    monkeypatch.setenv("SMTP_HOST", "invalid-smtp-host.talentsphere.local")
    monkeypatch.setenv("SMTP_PORT", "2525")
    assert not send_reset_email("user@example.com", "http://localhost:8501/?reset_token=abc")


def test_persistent_session_creation_validation_and_expiration():
    from services.core import register, connect, create_persistent_session, validate_persistent_session
    email = f"sess-user-{uuid.uuid4().hex[:8]}@example.com"
    register("Session User", email, "SessionPass123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    # Create persistent session
    signed_token = create_persistent_session(user_id)
    assert signed_token
    assert "." in signed_token

    # Validate valid session
    session = validate_persistent_session(signed_token)
    assert session is not None
    assert session["id"] == user_id
    assert session["email"] == email

    # Tampered signature
    raw_part = signed_token.split(".")[0]
    tampered_token = f"{raw_part}.invalid_hmac_signature"
    assert validate_persistent_session(tampered_token) is None

    # Expired session
    from datetime import datetime, timedelta
    past_exp = (datetime.now() - timedelta(days=1)).isoformat()
    with connect() as db:
        db.execute("UPDATE sessions SET expires_at=? WHERE user_id=?", (past_exp, user_id))
    assert validate_persistent_session(signed_token) is None


def test_persistent_session_logout_and_revocation():
    from services.core import register, connect, create_persistent_session, validate_persistent_session, revoke_session
    email = f"logout-sess-{uuid.uuid4().hex[:8]}@example.com"
    register("Logout User", email, "SessionPass123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    signed_token = create_persistent_session(user_id)
    assert validate_persistent_session(signed_token) is not None

    # Revoke session
    revoke_session(signed_token)
    assert validate_persistent_session(signed_token) is None


def test_password_reset_revokes_all_active_persistent_sessions():
    from services.core import register, connect, create_persistent_session, validate_persistent_session, reset_password
    import secrets, hashlib
    from datetime import datetime, timedelta

    email = f"sess-reset-{uuid.uuid4().hex[:8]}@example.com"
    register("Sess Reset User", email, "OldPassword123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    sess_token_1 = create_persistent_session(user_id)
    sess_token_2 = create_persistent_session(user_id)
    assert validate_persistent_session(sess_token_1) is not None
    assert validate_persistent_session(sess_token_2) is not None

    # Reset password
    raw_tok = secrets.token_urlsafe(32)
    tok_hash = hashlib.sha256(raw_tok.encode("utf-8")).hexdigest()
    future = (datetime.now() + timedelta(minutes=20)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,0,?)",
                   (user_id, tok_hash, future, datetime.now().isoformat()))

    ok, _ = reset_password(raw_tok, "BrandNewPassword456")
    assert ok

    # Both persistent sessions must now be revoked
    assert validate_persistent_session(sess_token_1) is None
    assert validate_persistent_session(sess_token_2) is None


def test_session_isolation_between_different_users():
    from services.core import register, connect, create_persistent_session, validate_persistent_session, revoke_session
    email_a = f"user-a-{uuid.uuid4().hex[:8]}@example.com"
    email_b = f"user-b-{uuid.uuid4().hex[:8]}@example.com"
    register("User A", email_a, "PasswordA123")
    register("User B", email_b, "PasswordB123")

    with connect() as db:
        id_a = db.execute("SELECT id FROM users WHERE email=?", (email_a,)).fetchone()["id"]
        id_b = db.execute("SELECT id FROM users WHERE email=?", (email_b,)).fetchone()["id"]

    token_a = create_persistent_session(id_a)
    token_b = create_persistent_session(id_b)

    assert validate_persistent_session(token_a)["id"] == id_a
    assert validate_persistent_session(token_b)["id"] == id_b

    # Revoking session for User A must NOT affect User B
    revoke_session(token_a)
    assert validate_persistent_session(token_a) is None
    assert validate_persistent_session(token_b)["id"] == id_b
