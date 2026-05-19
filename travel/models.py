from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 


class Hotel(models.Model):
    name = models.CharField(max_length=200, verbose_name="Otel Adı")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    district = models.CharField(max_length=100, verbose_name="İlçe", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Gecelik Fiyat")
    
    
    star_rating = models.FloatField(
        verbose_name="Yıldız Puanı", 
        default=4.5,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    
    review_count = models.IntegerField(verbose_name="Yorum Sayısı", default=0)

    class Meta:
        verbose_name = "Otel"
        verbose_name_plural = "Oteller"

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"