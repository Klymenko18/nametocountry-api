import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from factories import NameFactory, CountryFactory, NameCountryLinkFactory

from rest_framework.test import APIClient
import pytest


@pytest.mark.django_db
def test_top_names_by_country_missing_param():
    client = APIClient()
    resp = client.get('/api/popular-names/')
    assert resp.status_code == 400
    assert "country" in resp.json()["error"].lower()

@pytest.mark.django_db
def test_top_names_by_country_not_found():
    client = APIClient()
    resp = client.get('/api/popular-names/?country=XX')
    assert resp.status_code == 404

@pytest.mark.django_db
def test_nationality_by_name_returns_links(db, monkeypatch):
    country = CountryFactory(country="UA,Ukraine,Україна")
    name = NameFactory(name="Maksym")
    link = NameCountryLinkFactory(name=name, country=country, probability=0.55)

    client = APIClient()
    response = client.get("/api/names/?name=Maksym")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("country" in el for el in data) or any("country" in el and "probability" in el for el in data)

@pytest.mark.django_db
def test_nationality_by_name_missing_param():
    client = APIClient()
    resp = client.get("/api/names/")
    assert resp.status_code == 400
    assert "name" in resp.json()["error"].lower()

@pytest.mark.django_db
def test_nationality_by_name_not_found(monkeypatch):
    def mock_fetch_and_save_nationalities(name_param, name_obj):
        return None, "No countries found for this name"
    from namecountry import services
    monkeypatch.setattr(services, "fetch_and_save_nationalities", mock_fetch_and_save_nationalities)
    client = APIClient()
    response = client.get("/api/names/?name=UnlikelyName")
    assert response.status_code == 404
    assert "no countries" in response.json()["error"].lower()
