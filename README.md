NameCountry API
REST API for working with names and their associated countries.

Endpoints Overview
/api/names/
NameNationalityAPIView
Returns a list of nationalities and probabilities for a given name.

/api/popular-names/
TopNamesByCountryAPIView
Returns the top 5 most frequent names for a specified country.

/api/dev-add-name/
AddNameCountryLinkAPIView
Adds one or more names for a country.

/api/dev-update-name/
UpdateNameCountryLinkAPIView
Updates the probability for name-country links.

/api/dev-delete-name/
DeleteNameCountryLinkAPIView
Deletes one or more names for a country.

To run locally:

docker-compose build
docker-compose up


Tests:
export DJANGO_TESTING=TRUE
pytest
