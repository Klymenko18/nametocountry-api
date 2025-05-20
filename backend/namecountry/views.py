from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NameCountryLink, Country
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Name, NameCountryLink
from .serializer import NameCountryLinkSerializer
from rest_framework.renderers import JSONRenderer
from .services import (
    get_or_create_name,
    get_fresh_links_for_name,
    fetch_and_save_nationalities,
)
from rest_framework.permissions import AllowAny

class NameNationalityAPIView(APIView):
      permission_classes = [AllowAny]
      renderer_classes = [JSONRenderer]
      
      """
      Get the list of nationalities associated with a given name.

      Query Parameters:
      - name (str, required): The name for which to retrieve nationality data.

      Returns:
      - 200 OK: List of country links and probabilities for the given name.
      - 400 Bad Request: If the 'name' parameter is missing.
      - 404 Not Found: If no data is available for the given name or an error occurred during fetching.

      Example:
      GET /api/nationality/?name=Maxim
      Response: [
            {"country": "UA", "probability": 0.34, ...},
            ...
      ]
      """

      def get(self, request):
            name_param = request.query_params.get("name")
            if not name_param:
                  return Response({"error": "Missing 'name' parameter"}, status=status.HTTP_400_BAD_REQUEST)

            name_obj = get_or_create_name(name_param)
            links = get_fresh_links_for_name(name_obj)
            if links:
                  data = NameCountryLinkSerializer(links, many=True).data
                  return Response(data, status=status.HTTP_200_OK)

            links, error = fetch_and_save_nationalities(name_param, name_obj)
            if error:
                  return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            data = NameCountryLinkSerializer(links, many=True).data
            return Response(data, status=status.HTTP_200_OK)


class TopNamesByCountryAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    """
    Get the top 5 most requested names for a given country.

    Query Parameters:
    - country (str, required): Country code (ISO, e.g. 'UA', 'PL').

    Returns:
    - 200 OK: List of names and their request counts for the country.
    - 400 Bad Request: If the 'country' parameter is missing.
    - 404 Not Found: If the country does not exist or there is no data for it.

    Example:
    GET /api/top-names/?country=UA
    Response: [
          {"name": "Maksym", "requests": 12},
          ...
    ]
    """

    def get(self, request):
        country_code = request.query_params.get("country")
        if not country_code:
            return Response({"error": "Missing 'country' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        country_objs = Country.objects.filter(country__icontains=country_code)
        if not country_objs.exists():
            return Response({"error": "No data for this country"}, status=status.HTTP_404_NOT_FOUND)

        qs = (
            NameCountryLink.objects.filter(country__in=country_objs)
            .values("name__name")
            .annotate(requests=Count("name"))
            .order_by("-requests")[:5]
        )
        if not qs:
            return Response({"error": "No data for this country"}, status=status.HTTP_404_NOT_FOUND)

        data = [{"name": row["name__name"], "requests": row["requests"]} for row in qs]
        return Response(data, status=status.HTTP_200_OK)


class AddNameCountryLinkAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    """
    Add one or more names to a specified country.

    Request Body (application/json):
    - country (str, required): The country string (e.g., "UA,Ukraine,Україна").
    - names (list of str, required): The names to add.
    - probability (float, optional): Probability value for the link (default: 0.5).

    Returns:
    - 201 Created: List of added names.
    - 400 Bad Request: If 'country' or 'names' is missing.

    Example:
    POST /api/dev-add-name/
    {
        "country": "UA,Ukraine,Україна",
        "names": ["Ivan", "Petro"],
        "probability": 0.5
    }
    Response: {
        "created": ["Ivan", "Petro"]
    }
    """
    def post(self, request):
        country_name = request.data.get("country")
        names = request.data.get("names", [])
        probability = request.data.get("probability", 0.5)
        if not country_name or not names:
            return Response({"error": "country and names required"}, status=400)
        country, _ = Country.objects.get_or_create(country=country_name)
        created = []
        for name_str in names:
            name, _ = Name.objects.get_or_create(name=name_str)
            link, is_created = NameCountryLink.objects.get_or_create(
                name=name, country=country, defaults={"probability": probability}
            )
            if is_created:
                created.append(name_str)
        return Response({"created": created}, status=201)


class UpdateNameCountryLinkAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    """
    Update the probability value for one or more NameCountryLink objects.

    Request Body (application/json):
    - country (str, required): The country string.
    - names (list of str, required): The names to update.
    - probability (float, required): New probability value.

    Returns:
    - 200 OK: List of updated names.
    - 400 Bad Request: If 'country', 'names', or 'probability' is missing.
    - 404 Not Found: If the country does not exist.

    Example:
    PUT /api/dev-update-name/
    {
        "country": "UA,Ukraine,Україна",
        "names": ["Ivan", "Petro"],
        "probability": 0.75
    }
    Response: {
        "updated": ["Ivan", "Petro"]
    }
    """
    def put(self, request):
        country_name = request.data.get("country")
        names = request.data.get("names", [])
        probability = request.data.get("probability")
        if not country_name or not names or probability is None:
            return Response({"error": "country, names, and probability required"}, status=400)
        country = Country.objects.filter(country=country_name).first()
        if not country:
            return Response({"error": "Country not found"}, status=404)
        updated = []
        for name_str in names:
            name = Name.objects.filter(name=name_str).first()
            if name:
                updated_count = NameCountryLink.objects.filter(name=name, country=country).update(probability=probability)
                if updated_count:
                    updated.append(name_str)
        return Response({"updated": updated}, status=200)


class DeleteNameCountryLinkAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    """
    Delete one or more NameCountryLink objects for a given country and list of names.

    Request Body (application/json):
    - country (str, required): The country string.
    - names (list of str, required): The names to delete links for.

    Returns:
    - 200 OK: List of deleted names.
    - 400 Bad Request: If 'country' or 'names' is missing.
    - 404 Not Found: If the country does not exist.

    Example:
    DELETE /api/dev-delete-name/
    {
        "country": "UA,Ukraine,Україна",
        "names": ["Ivan", "Petro"]
    }
    Response: {
        "deleted": ["Ivan", "Petro"]
    }
    """
    def delete(self, request):
        country_name = request.data.get("country")
        names = request.data.get("names", [])
        if not country_name or not names:
            return Response({"error": "country and names required"}, status=400)
        country = Country.objects.filter(country=country_name).first()
        if not country:
            return Response({"error": "Country not found"}, status=404)
        deleted = []
        for name_str in names:
            name = Name.objects.filter(name=name_str).first()
            if name:
                deleted_count, _ = NameCountryLink.objects.filter(name=name, country=country).delete()
                if deleted_count:
                    deleted.append(name_str)
        return Response({"deleted": deleted}, status=200)