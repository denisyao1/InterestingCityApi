from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine


from app import settings
from app.models import Ville

config = settings.get_settings()


def load_results() -> list[dict]:
    """
    Load results.csv file into a list of dict.
    """
    import json
    import pathlib

    file = pathlib.Path(f"{config.RESSOURCES_FOLDER}/results.json")

    if not file.exists():
        raise FileNotFoundError(f"Le fichier {file} n'existe pas")

    with open(file, encoding="UTF-8") as file:
        return json.load(file)


def create_cities(engine: Engine):
    """
    Load result files cities and copy them to Database.
    """

    results = load_results()
    cities = [Ville(**row) for row in results]
    with Session(engine) as db:
        db.add_all(cities)
        db.commit()


def get_cities(
    db: Session, departement: str, surface: int, loyer_max: int
) -> list[Ville]:
    """
    Return cities of the defined department.
    """
    cities = (
        db.query(Ville)
        .filter(
            Ville.departement == departement, Ville.loyer_moyen * surface <= loyer_max
        )
        .order_by(Ville.note.desc())
        .order_by(Ville.nom.asc())
        .all()
    )

    return cities
