from django.urls import path
from .views import NameNationalityAPIView, TopNamesByCountryAPIView

urlpatterns = [
    path("names/", NameNationalityAPIView.as_view()),
    path("popular-names/", TopNamesByCountryAPIView.as_view()),
]
