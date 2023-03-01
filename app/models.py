from sqlalchemy import Column, Integer, Float, String

from app.db import Base


class Ville(Base):
    __tablename__ = "ville"

    nom = Column(String)
    loyer_moyen = Column(Float)
    note = Column(Float, default=0)
    population = Column(Integer)
    code_postal = Column(String)
    departement = Column(String, index=True)
    code_insee = Column(String, primary_key=True)

    def __init__(
        self,
        nom: str,
        loyer_moyen: float,
        note: float,
        population: int,
        code_postal: str,
        departement: str,
        code_insee: str,
    ) -> None:
        super().__init__()
        self.nom = nom
        self.loyer_moyen = loyer_moyen
        self.note = note
        self.population = population
        self.code_postal = code_postal
        self.departement = departement
        self.code_insee = code_insee

    def json(self):
        """
        Return a dict of attribute.
        """
        return {
            "nom": self.nom,
            "loyer_moyen": self.loyer_moyen,
            "note": self.note,
            "population": self.population,
            "code_postal": self.code_postal,
            "departement": self.departement,
            "code_insee": self.code_insee,
        }
