from django.urls import path
from .views import NameNationalityAPIView, TopNamesByCountryAPIView,AddNameCountryLinkAPIView,UpdateNameCountryLinkAPIView,DeleteNameCountryLinkAPIView

urlpatterns = [
    path("names/", NameNationalityAPIView.as_view()),
    path("popular-names/", TopNamesByCountryAPIView.as_view()),
    path("dev-add-name/", AddNameCountryLinkAPIView.as_view()),
    path("dev-update-name/", UpdateNameCountryLinkAPIView.as_view()),
    path("dev-delete-name/", DeleteNameCountryLinkAPIView.as_view()),
]
