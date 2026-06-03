from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_bucket_name: str = "local-bucket"
    jobs_table_name: str = "cloudy-jobs"
    sagemaker_role_arn: str = "arn:aws:iam::000000000000:role/sagemaker"
    training_image_uri: str = "000000000000.dkr.ecr.us-east-1.amazonaws.com/cloudy-training:latest"
    aws_region: str = "us-east-1"


settings = Settings()
