from ml.inference.predict import predict


def test_predict_stub_horizon():
    forecast = predict("s3://bucket/model.tar.gz", horizon=3)
    assert len(forecast) == 3
    assert "timestamp" in forecast[0]
    assert "prediction" in forecast[0]
