from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NameCountryLink, Country
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Name, NameCountryLink
from .serializers import NameCountryLinkSerializer
from .services import (
    get_or_create_name,
    get_fresh_links_for_name,
    fetch_and_save_nationalities,
)

class NameNationalityAPIView(APIView):
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
      def get(self, request):
            country_code = request.query_params.get("country")
            if not country_code:
                  return Response({"error": "Missing 'country' parameter"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                  country = Country.objects.get(code__iexact=country_code)
            except Country.DoesNotExist:
                  return Response({"error": "No data for this country"}, status=status.HTTP_404_NOT_FOUND)

            qs = (
                  NameCountryLink.objects.filter(country=country)
                  .values("name__value")
                  .annotate(requests=Count("name"))
                  .order_by("-requests")[:5]
            )
            if not qs:
                  return Response({"error": "No data for this country"}, status=status.HTTP_404_NOT_FOUND)

            data = [{"name": row["name__value"], "requests": row["requests"]} for row in qs]
            return Response(data, status=status.HTTP_200_OK)
