import pytest
import json
import httpx

from app.builder import load_indicateur_loyers, get_ville_infos, format_nom_ville
from app import settings

config = settings.get_settings()


def test_load_indicateur_loyers():
    file = config.INDICATEUR_LOYERS
    result = load_indicateur_loyers(file)
    assert len(result) == 3959
    assert result[0]["loyer_moyen"] == 10.07
    assert result[0]["code_insee"] == "01004"
    assert result[0]["departement"] == "1"


def test_load_indicateur_loyer_file_not_exits():
    file = "./dummy"
    with pytest.raises(FileNotFoundError):
        load_indicateur_loyers(file)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Châtillon-en-Michaille", "chatillon-en-michaille"),
        ("La Voulte-sur-Rhône", "voulte-sur-rhone"),
        ("Marseille 10e Arrondissement", "marseille"),
        ("Le Test l'ile", "test-l-ile"),
        ("D'eau clemence", "d-eau-clemence"),
        ("Le D'estampe", "d-estampe"),
        ("LeGrand Tabout", "legrand-tabout"),
        ("L'ile au trésor", "ile-au-tresor"),
    ],
)
def test_format_non_ville(input, expected):
    assert format_nom_ville(input) == expected


@pytest.mark.asyncio
@pytest.mark.respx(base_url=config.API_GEO_URL)
async def test_get_city_infos_HttpStatusError(respx_mock):
    respx_mock.get("/communes/3098").mock(return_value=httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        await get_ville_infos(3098)


@pytest.mark.asyncio
@pytest.mark.respx(base_url=config.API_GEO_URL)
async def test_get_city_infos_HttpError(respx_mock):
    respx_mock.get("/communes/3098").mock(return_value=httpx.Response(502))
    with pytest.raises(httpx.HTTPError):
        await get_ville_infos(3098)


@pytest.mark.asyncio
@pytest.mark.respx(base_url=config.API_GEO_URL)
async def test_get_city_infos_DecodeError(respx_mock):
    respx_mock.get("/communes/3098").mock(
        return_value=httpx.Response(text="'nom':'test'", status_code=200)
    )
    with pytest.raises(json.decoder.JSONDecodeError):
        await get_ville_infos(3098)


@pytest.mark.asyncio
@pytest.mark.respx(base_url=config.API_GEO_URL)
async def test_get_city_infos_KeyError(respx_mock):
    response = {
        "nom": "Melun",
        "codesPostaux": ["77000"],
        "populatio": 40844,
    }

    respx_mock.get("/communes/3098").mock(
        return_value=httpx.Response(json=response, status_code=200)
    )
    with pytest.raises(KeyError):
        await get_ville_infos(3098)
