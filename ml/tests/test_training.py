from ml.feature_importance.export import export_feature_importance_stub


def test_export_stub_has_contract():
    result = export_feature_importance_stub("job-123")
    assert result["job_id"] == "job-123"
    assert len(result["features"]) >= 1
    assert "name" in result["features"][0]
    assert "importance" in result["features"][0]
