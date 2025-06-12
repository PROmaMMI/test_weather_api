from django.db import models

class ForecastOverride(models.Model):
    city = models.CharField(max_length=100)
    date = models.DateField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    
    class Meta:
        unique_together = ('city', 'date')
        indexes = [
            models.Index(fields=['city', 'date']),
        ]
    
    def __str__(self):
        return f"{self.city} ({self.date}): min={self.min_temperature}, max={self.max_temperature}"