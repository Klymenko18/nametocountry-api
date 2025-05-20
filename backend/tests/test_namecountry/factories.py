import factory
from namecountry.models import Name, Country, NameCountryLink
from django.utils import timezone

class NameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Name
    name = factory.Sequence(lambda n: f"TestName{n}")
    count_of_requests = factory.Faker("pyint", min_value=0, max_value=50)
    last_accessed = factory.LazyFunction(timezone.now)

class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country
    country = factory.Sequence(lambda n: f"UA,Ukraine{n},Україна{n}")
    region = factory.Faker("word")
    independent = factory.Faker("pystr", max_chars=10)
    google_maps = factory.Faker("url")
    open_street_map = factory.Faker("url")
    capital_name = factory.Faker("city")
    capital_coordinates = factory.LazyAttribute(lambda _: "50.45,30.52")
    flag_png = factory.Faker("image_url")
    flag_svg = factory.Faker("image_url")
    flag_alt = factory.Faker("sentence", nb_words=6)
    coat_of_arms_png = factory.Faker("image_url")
    coat_of_arms_svg = factory.Faker("image_url")
    borders_with = factory.LazyAttribute(lambda _: "PL,RO,HU,SK,BY,RU,MD")

class NameCountryLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NameCountryLink
    name = factory.SubFactory(NameFactory)
    country = factory.SubFactory(CountryFactory)
    probability = factory.Faker("pyfloat", left_digits=0, right_digits=3, min_value=0.001, max_value=1, positive=True)
