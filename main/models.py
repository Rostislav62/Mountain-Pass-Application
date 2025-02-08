from django.db import models

from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    fam = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    otc = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.email


class Coords(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    height = models.IntegerField()

    def __str__(self):
        return f"({self.latitude}, {self.longitude}, {self.height})"


class PerevalAdded(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coord = models.ForeignKey(Coords, on_delete=models.CASCADE)
    beautyTitle = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True, null=True)
    connect = models.TextField(blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    level_winter = models.CharField(max_length=10, blank=True, null=True)
    level_summer = models.CharField(max_length=10, blank=True, null=True)
    level_autumn = models.CharField(max_length=10, blank=True, null=True)
    level_spring = models.CharField(max_length=10, blank=True, null=True)
    route_description = models.TextField(blank=True, null=True)
    hazards = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class PerevalImages(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
    image_path = models.TextField()

    def __str__(self):
        return self.image_path


class PerevalGpsTracks(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
    track_path = models.TextField()

    def __str__(self):
        return self.track_path


class PerevalHistory(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pass_date = models.DateField()
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pereval.title} - {self.pass_date}"


class RelatedObjects(models.Model):
    RELATED_TYPE_CHOICES = [
        ('mountain', 'Mountain'),
        ('ridge', 'Ridge'),
        ('other', 'Other'),
    ]

    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
    related_name = models.CharField(max_length=255)
    related_type = models.CharField(max_length=50, choices=RELATED_TYPE_CHOICES)

    def __str__(self):
        return f"{self.related_name} ({self.related_type})"


class WeatherInfo(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    precipitation = models.CharField(max_length=50, blank=True, null=True)
    weather_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather for {self.pereval.title} on {self.weather_date}"

