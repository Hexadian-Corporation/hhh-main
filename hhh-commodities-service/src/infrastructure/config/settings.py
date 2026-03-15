from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "hhh-commodities-service"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "hhh_commodities"
    host: str = "0.0.0.0"
    port: int = 8007

    model_config = {"env_prefix": "HHH_COMMODITIES_"}
