from django.db import models

class Name(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    count_of_requests = models.PositiveIntegerField(default=0, verbose_name="Count of requests")
    last_accessed = models.DateTimeField(null=True, blank=True, verbose_name="Last accessed")
    def __str__(self): return self.name

class Country(models.Model):
    country = models.CharField(max_length=512, verbose_name="Country")
    region = models.CharField(max_length=100, blank=True, verbose_name="Region")
    independent = models.CharField(max_length=10, blank=True, verbose_name="Independent")
    google_maps = models.URLField(blank=True, verbose_name="Google maps")
    open_street_map = models.URLField(blank=True, verbose_name="Open street map")
    capital_name = models.CharField(max_length=100, blank=True, verbose_name="Capital Name")
    capital_coordinates = models.CharField(max_length=50, blank=True, verbose_name="Capital Coordinates")
    flag_png = models.URLField(blank=True, verbose_name="Flag (png)")
    flag_svg = models.URLField(blank=True, verbose_name="Flag (svg)")
    flag_alt = models.CharField(max_length=255, blank=True, verbose_name="Flag alt")
    coat_of_arms_png = models.URLField(blank=True, verbose_name="Coat of arms (png)")
    coat_of_arms_svg = models.URLField(blank=True, verbose_name="Coat of arms (svg)")
    borders_with = models.CharField(max_length=255, blank=True, verbose_name="Borders with")
    def __str__(self): return self.country

class NameCountryLink(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    probability = models.FloatField(verbose_name="Probability")
    class Meta: unique_together = ('name', 'country')
    def __str__(self): return f"{self.name.name} - {self.country.country}: {self.probability}"
