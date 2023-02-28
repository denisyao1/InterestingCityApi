from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    INDICATEUR_LOYERS: str = "./ressources/indicateurs-loyers-appartements.csv"
    API_GEO_URL: str = "https://geo.api.gouv.fr"
    NOTE_WEBSITE_URL: str = "https://www.bien-dans-ma-ville.fr/"
    DATABASE_URL: str = "sqlite:///cities.db"
    RESSOURCES_FOLDER = "./ressources"

    class Config:
        env_file = "../.env"


@lru_cache
def get_settings() -> Settings:
    """
    Return App Settings.
    """
    print(Settings().INDICATEUR_LOYERS)
    print(Settings().DATABASE_URL)
    return Settings()
