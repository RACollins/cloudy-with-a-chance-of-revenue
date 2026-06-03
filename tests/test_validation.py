from app.services.validation import ValidationError, validate_csv


def test_validate_csv_ok():
    csv_content = "timestamp,value\n2024-01-01,10\n2024-01-02,12\n"
    result = validate_csv(csv_content, "timestamp", "value")
    assert result.summary.row_count == 2


def test_validate_csv_missing_column():
    try:
        validate_csv("value\n10\n", "timestamp", "value")
        assert False, "expected ValidationError"
    except ValidationError:
        pass
