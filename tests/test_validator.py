import pytest
from pipeline.validator import Validator

def test_empty_data():
    validator = Validator()
    result = validator.validate([])
    assert not result["is_valid"]
    assert any("Empty output" in err for err in result["errors"])

def test_missing_required_fields():
    """2/2 articles missing fields → 100% rate → still hard-fails (rate > 0.3)."""
    validator = Validator(required_fields=["title", "content"])
    data = [
        {"title": "Test Title", "content": ""},
        {"title": "", "content": "Some content"}
    ]
    result = validator.validate(data)
    assert not result["is_valid"]
    # Error text now mentions rate, not a flat "Missing required fields" label
    assert any("missing rate" in err.lower() for err in result["errors"])


def test_sparse_fields_do_not_fail_below_threshold():
    """1 article missing a field out of 10 = 10% → valid, but generates a warning."""
    validator = Validator(required_fields=["title", "content"])
    data = [{"title": f"T{i}", "content": f"C{i}"} for i in range(9)]
    data.append({"title": "", "content": ""})  # 10th article has empty fields
    result = validator.validate(data)
    # 10% missing is below the 30% threshold — batch should be valid
    assert result["is_valid"], "Batch with 10% sparse records should still be valid"
    assert result["errors"] == []
    # But we do expect a warning and the missing_fields diagnostic
    assert any("Sparse" in w for w in result["warnings"])
    assert len(result["missing_fields"]) > 0


def test_rate_just_above_threshold_hard_fails():
    """4/10 = 40% missing → above threshold → invalid."""
    validator = Validator(required_fields=["title", "content"])
    data = [{"title": f"T{i}", "content": f"C{i}"} for i in range(6)]
    data += [{"title": "", "content": ""} for _ in range(4)]  # 40% bad
    result = validator.validate(data)
    assert not result["is_valid"]
    assert any("missing rate" in err.lower() for err in result["errors"])


def test_missing_fields_key_exposed_for_healer():
    """Validator always exposes missing_fields and missing_rate for healer routing."""
    validator = Validator(required_fields=["title", "content"])
    data = [{"title": "T", "content": "C"}]  # fully valid
    result = validator.validate(data)
    assert "missing_fields" in result
    assert "missing_rate" in result
    assert result["missing_fields"] == []
    assert result["missing_rate"] == 0.0

def test_valid_data():
    validator = Validator(min_articles=2, required_fields=["title", "content"])
    data = [
        {"title": "Title 1", "content": "Content 1"},
        {"title": "Title 2", "content": "Content 2"}
    ]
    result = validator.validate(data)
    assert result["is_valid"]
    assert len(result["errors"]) == 0
    assert len(result["warnings"]) == 0

def test_low_output_warning():
    validator = Validator(min_articles=5, required_fields=["title", "content"])
    data = [
        {"title": "Title 1", "content": "Content 1"}
    ]
    result = validator.validate(data)
    assert result["is_valid"]
    assert len(result["errors"]) == 0
    assert len(result["warnings"]) == 1
    assert "Low output" in result["warnings"][0]

def test_non_list_shapes():
    validator = Validator()
    
    # 1. Single article dict (should be coerced and validated successfully)
    single_article = {"title": "Valid Title", "content": "Valid Content"}
    result = validator.validate(single_article)
    assert result["is_valid"]
    
    # 2. Status/Error dict (should fail validation cleanly)
    error_dict = {"status": "error", "message": "Failed to fetch dataset"}
    result2 = validator.validate(error_dict)
    assert not result2["is_valid"]
    assert any("Invalid output shape" in err for err in result2["errors"])

    # 3. Random scalar (should fail validation cleanly)
    result3 = validator.validate("not a dict or list")
    assert not result3["is_valid"]
    assert any("Invalid output shape" in err for err in result3["errors"])
