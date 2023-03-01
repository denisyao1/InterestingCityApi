from pydantic import BaseModel


class Ville(BaseModel):
    nom: str
    loyer_moyen: float
    note: float
    population: int
    code_postal: str
    departement: str
    code_insee: str


class City(Ville):
    id: int

    class Config:
        orm_mode = True


class ListeVilles(BaseModel):
    nombre: int
    villes: list[Ville] = []
