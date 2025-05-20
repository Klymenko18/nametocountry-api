import requests
from datetime import timedelta
from django.utils import timezone
from .models import Name, Country, NameCountryLink

RESTCOUNTRIES_URL = "https://restcountries.com/v3.1/alpha/{code}"
NATIONALIZE_URL = "https://api.nationalize.io/?name={name}"

def fetch_country_data(code):
    resp = requests.get(RESTCOUNTRIES_URL.format(code=code.lower()), timeout=10)
    if resp.status_code == 200 and resp.json():
        data = resp.json()[0]
        return {
            "country": ",".join([
                data.get("cca2", ""),
                data.get("name", {}).get("common", ""),
                data.get("name", {}).get("official", "")
            ]),
            "region": data.get("region", ""),
            "independent": str(data.get("independent", "")),
            "google_maps": data.get("maps", {}).get("googleMaps", ""),
            "open_street_map": data.get("maps", {}).get("openStreetMaps", ""),
            "capital_name": data.get("capital", [""])[0] if data.get("capital") else "",
            "capital_coordinates": (
                ",".join([str(x) for x in data.get("capitalInfo", {}).get("latlng", ["", ""])])
                if data.get("capitalInfo", {}).get("latlng") else ""
            ),
            "flag_png": data.get("flags", {}).get("png", ""),
            "flag_svg": data.get("flags", {}).get("svg", ""),
            "flag_alt": data.get("flags", {}).get("alt", ""),
            "coat_of_arms_png": data.get("coatOfArms", {}).get("png", ""),
            "coat_of_arms_svg": data.get("coatOfArms", {}).get("svg", ""),
            "borders_with": ",".join(data.get("borders", [])),
        }
    return {}


def get_or_create_country(code):
    data = fetch_country_data(code)
    country_field = data.get("country", "")  
    if not country_field:
        return None
    country, created = Country.objects.get_or_create(country=country_field)
    if created or not country.region:
        for field, value in data.items():
            if hasattr(country, field):
                setattr(country, field, value)
        country.save()
    return country


def get_or_create_name(name_value):
    name_obj, _ = Name.objects.get_or_create(name__iexact=name_value, defaults={"name": name_value})
    name_obj.count_of_requests += 1
    name_obj.last_accessed = timezone.now()
    name_obj.save()
    return name_obj


def get_fresh_links_for_name(name_obj):
    if name_obj.last_accessed and name_obj.last_accessed >= timezone.now() - timedelta(days=1):
        return NameCountryLink.objects.filter(name=name_obj)
    return None


def fetch_and_save_nationalities(name_param, name_obj):
    response = requests.get(NATIONALIZE_URL.format(name=name_param))
    if response.status_code != 200:
        return None, "Nationalize.io API error"
    results = response.json().get("country", [])
    if not results:
        return None, "No countries found for this name"
    links = []
    for country_data in results:
        code = country_data.get("country_id")
        probability = country_data.get("probability", 0)
        if not code:
            continue
        country = get_or_create_country(code)
        link, _ = NameCountryLink.objects.get_or_create(
            name=name_obj, country=country, defaults={"probability": probability}
        )
        link.probability = probability
        link.save()
        links.append(link)
    return links, None
