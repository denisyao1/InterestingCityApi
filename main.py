from fastapi import FastAPI, Query

from app import models

tags_data = [{"name": "Départements"}]
app = FastAPI(title="API Villes Interessantes", version="1.0.0", tags_metadata=tags_data)


@app.on_event("startup")
async def startup():
    models.create_db_and_data()


@app.get("/departements/{code}/villes", tags=["Départements"])
async def recherche_villes_departement(
    code: str = Query(
        ..., description="Le code du departement sur lequel porte la recherche"
    ),
    loyer_max: int = Query(..., description="Le loyer en Euros maximun du logement"),
    surface: int = Query(..., description="La surface du logement en m²"),
) -> models.Villes:
    """
    Recherche les villes d'un département par note décroissante.
    """

    return models.get_cities(departement=code, loyer_max=loyer_max, surface=surface)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
