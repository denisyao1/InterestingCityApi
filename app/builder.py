import csv
import json
import pathlib
import decimal
from datetime import datetime

import httpx
import json
import bs4
import unidecode

import settings

# Open loyer appart et importer code inssee et loyerpm2

config = settings.get_settings()


def load_indicateur_loyers(filename: str) -> list[dict]:
    """
    Charge en mémoire l'indicateur de loyer par code insee.

    Args:
        file: Le nom du fichier des indicateur de loyer.

    Returns:
        Une list de dictionnaire contenant le loyer de chaque ville.
        exemple:
        [{"code_insee" : "1234", "departement": "74", "loyer_moyen": 11,85}]

    Raises:
        FileNotFoundError : Si le fichier est introuvable.
    """
    path = pathlib.Path(filename)

    if not path.exists():
        raise FileNotFoundError(f"Le fichier {filename} n'existe pas")

    result = []
    with open(path) as csv_file:
        print(csv_file.name)
        reader = csv.DictReader(csv_file, delimiter=";")
        communes = [row for row in reader if row["TYPPRED"] == "commune"]
        for row in communes:
            loyer_str: str = row["loypredm2"]
            loyer_decimal = decimal.Decimal(loyer_str.replace(",", "."))
            code_insee = row["INSEE"]
            code_insee = code_insee if len(code_insee) == 5 else f"0{code_insee}"
            city = {
                "code_insee": code_insee,
                "departement": row["DEP"],
                "loyer_moyen": float(round(loyer_decimal, 2)),
            }
            result.append(city)

    return result


async def get_ville_infos(code_insee: str) -> dict:
    """
    Retourne les informations de la ville definit par le code insee.

    Args:
        code_insee: le code insee de la ville.

    Returns:
        Un dictionnaire des informations de la ville.
        exemple:
        {"nom": "ville1", "code_postal":"45007", "population": 123456}

    Raises:
        httpx.HTTPStatusError : L'API Geo ne trouve aucune information pour le code insee.
        httpx.HTTPError: Impossible de se connecter à l'API Geo.
        httpx.DecodingError: Impossible de Décoder la response obtenu de l'API Geo.
        KeyError : Une clé n'existe pas dans le json retourné.

    """
    params = {"fields": "nom,codesPostaux,population"}
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient(base_url=config.API_GEO_URL) as client:
        try:
            response = await client.get(
                f"/communes/{code_insee}", params=params, headers=headers
            )
            response.raise_for_status()
        except httpx.HTTPStatusError:
            print(f"Cannot found informations for city : {code_insee}")
            raise
        except httpx.HTTPError:
            print(
                f"Unable to connect to GeoAPI to get informations for city :{code_insee}"
            )
            raise
    try:
        r_json = response.json()
        response = {
            "nom": r_json["nom"],
            "code_postal": r_json["codesPostaux"][0],
            "population": r_json["population"],
        }
        return response
    except (json.decoder.JSONDecodeError, KeyError):
        print(f"Unable to decode response for city :{code_insee} :")
        print(f"-> {response.text}")
        raise


def format_nom_ville(nom_ville: str) -> str:
    """
    Format le nom de la commune pour le rendre compatible au site de notation.
    """
    # les caractère non unicode tels que les é, è sont remplacés par e
    nom_ville = unidecode.unidecode(nom_ville.lower())

    # Si le nom contient arrondissement alors garders le premier mot
    # Exemple marseille 11e arrondissement => marseille
    nom_ville = nom_ville.split(" ")[0] if "arrondissement" in nom_ville else nom_ville

    nom_ville = nom_ville.strip().replace(" ", "-")
    # Un nom de ville commençant par le, la , les, l' representé dans l'url du site sans le prefixe
    # example la Chapelle-du-Chetelard => Chapelle-du-Chetelard
    for w in ["le-", "la-", "les-", "l'"]:
        if nom_ville.startswith(w):
            nom_ville = nom_ville.replace(w, "", 1)

    # si après l'operation précédente le nom de la ville contient l' ou d' tels
    # le l' ou d' est remplacé par l-
    nom_ville = nom_ville.replace("l'", "l-") if "l'" in nom_ville else nom_ville
    nom_ville = nom_ville.replace("d'", "d-") if "d'" in nom_ville else nom_ville

    return nom_ville


async def get_note_ville(nom_ville: str, code_insee: str) -> float:
    """
    Retourne la note globale de la ville.

    Args:
        nom_ville: le nom de la ville.
        code_insee: Le code insee de la ville.

    Returns:
        la note globale de la ville.
        example: 3.8.
    Raises:
        httpx.HTTPStatusError: Impossible de recuperer la page de notation de la ville.
        httpx.HTTPError: Impossible de se connecter au Site Web de notation des villes.
        IndexError: Impossible d'obtenir les div de la page html
        ValueError: La note n'est pas convertible en float


    """
    nom_ville = format_nom_ville(nom_ville)
    async with httpx.AsyncClient(base_url=config.NOTE_WEBSITE_URL) as client:
        try:
            response = await client.get(f"/{nom_ville}-{code_insee}/")
            response.raise_for_status()
        except httpx.HTTPStatusError:
            print(
                f"Impossible d'obtenir la page de notation de : {nom_ville}-{code_insee}"
            )
            raise
        except httpx.HTTPError:
            print(
                (
                    f"Impossible de se connecter au site {config.NOTE_WEBSITE_URL} pour recuperer"
                    f"la note de la ville {nom_ville}-{code_insee}."
                )
            )
            raise

    soup = bs4.BeautifulSoup(response.text, "html.parser")
    try:
        raw_total: str = soup.find_all("div", class_="total")[-1].get_text()
    except IndexError:
        print(f"Impossible de lire la note de {nom_ville}-{code_insee}.")
    try:
        note = float(raw_total.split("/")[0])
        return note
    except ValueError:
        print(f"Impossible de convertir la note de la ville {nom_ville}-{code_insee}.")


async def get_cities_informations(filename: str) -> list[dict]:
    """
    Retourne les informations des villes du fichier.

    Args:
        filename: le nom du fichier contenant les villes.

    Returns:
        Une liste de dictionnaire contenant les informations sur les villes.
        Exemple:
        [{
            "code_insee" : "1234",
            "departement": "74",
            "loyer_moyen": 11,85,
            "nom": "ville1",
            "code_postal":"45007",
            "population": 123456,
            "note" : 3.8
            }]
    """

    results = load_indicateur_loyers(filename)
    start_date = datetime.now()
    for ville in results:
        try:
            code_insee = ville.get("code_insee")
            infos = await get_ville_infos(code_insee)
            ville.update(infos)
        except (
            httpx.HTTPStatusError,
            httpx.HTTPError,
            json.decoder.JSONDecodeError,
            KeyError,
        ):
            continue
        try:
            nom_ville: str = ville.get("nom")
            note = await get_note_ville(nom_ville, code_insee)
            ville["note"] = note
        except (httpx.HTTPStatusError, httpx.HTTPError, IndexError, ValueError):
            ville["note"] = None
    end_date = datetime.now()
    print(f"--> programme exécuté en {end_date - start_date}")
    results = list(filter(lambda element: element.get("nom") is not None, results))
    return results


def save_into_json(cities_infos: list[dict]) -> None:
    """
    Save cities information to json file.
    """
    with open(
        f"{config.RESSOURCES_FOLDER}/results.json", "w", encoding="utf-8"
    ) as json_file:
        json.dump(cities_infos, json_file, indent=4)


async def main():
    """
    Get cities information from file and save them csv file.
    """
    results = await get_cities_informations(config.INDICATEUR_LOYERS)
    save_into_json(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
