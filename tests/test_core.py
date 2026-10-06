import pytest
from services.core import profile_completion, gap_analysis, profile_analysis, verify_password, _password, recommendations

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
