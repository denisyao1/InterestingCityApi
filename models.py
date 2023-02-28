import pathlib

from sqlmodel import Field, Session, SQLModel, create_engine, select

from app import settings

config = settings.get_settings()


class Ville(SQLModel):
    nom: str
    loyer_moyen: float
    note: float = Field(default=0)
    population: int
    code_postal: str
    departement: str = Field(index=True)
    code_insee: str = Field(unique=True)


class CityDB(Ville, table=True):
    __tablename__ = "cities"
    id: int | None = Field(default=None, primary_key=True)


class Villes(SQLModel):
    count: int
    villes: list[Ville] = []


engine = create_engine(config.DATABASE_URL, echo=True)


def create_db_and_data():
    """
    Create the Database and load data into it.
    """
    SQLModel.metadata.create_all(engine)
    try:
        create_cities()
    except:
        pass


def load_results() -> list[dict]:
    """
    Load results.csv file into a list of dict.
    """
    import csv

    file = pathlib.Path(f"{config.RESSOURCES_FOLDER}/results.csv")

    if not file.exists():
        raise FileNotFoundError(f"Le fichier {file} n'existe pas")

    with open(file, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        return [row for row in reader]


def create_cities():
    """
    Load result files cities and copy them to Database.
    """

    cities = load_results()
    cities = [CityDB(**row) for row in cities]
    with Session(engine) as session:
        session.add_all(cities)
        session.commit()


def get_cities(departement: str, surface: int, loyer_max: int) -> Villes:
    """
    Return cities of the defined department.
    """
    with Session(engine) as session:
        statement = (
            select(CityDB)
            .where(CityDB.departement == departement)
            .where(CityDB.loyer_moyen * surface <= loyer_max)
            .order_by(CityDB.note.desc())
            .order_by(CityDB.nom.asc())
        )
        results = session.exec(statement).all()
        results = [Ville(**elm.dict()) for elm in results]
        return Villes(count=len(results), villes=results)
