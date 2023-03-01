from fastapi import FastAPI, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import services, models, schemas
from app.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


tags_data = [{"name": "Départements"}]
app = FastAPI(
    title="API Villes Interessantes", version="1.0.0", tags_metadata=tags_data
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    try:
        services.create_cities(engine)
    except IntegrityError:
        pass
    except Exception as e:
        raise


@app.get("/departements/{code}/villes", tags=["Départements"])
async def recherche_villes_departement(
    db: Session = Depends(get_db),
    code: str = Query(
        ..., description="Le code du departement sur lequel porte la recherche"
    ),
    loyer_max: int = Query(..., description="Le loyer en Euros maximun du logement"),
    surface: int = Query(..., description="La surface du logement en m²"),
) -> schemas.ListeVilles:
    """
    Recherche les villes d'un département par note décroissante.
    """
    cities = services.get_cities(
        db, departement=code, loyer_max=loyer_max, surface=surface
    )
    return schemas.ListeVilles(
        nombre=len(cities), villes=[city.json() for city in cities]
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
