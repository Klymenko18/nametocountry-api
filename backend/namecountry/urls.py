from django.urls import path
from .views import NameNationalityAPIView, PopularNamesAPIView

urlpatterns = [
    path("names/", NameNationalityAPIView.as_view()),
    path("popular-names/", PopularNamesAPIView.as_view()),
]
