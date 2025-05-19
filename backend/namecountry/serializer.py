from rest_framework import serializers
from .models import Name, Country, NameCountryLink

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name
        fields = '__all__'

class NameCountryLinkSerializer(serializers.ModelSerializer):
    name = NameSerializer(read_only=True)
    country = CountrySerializer(read_only=True)

    class Meta:
        model = NameCountryLink
        fields = '__all__'