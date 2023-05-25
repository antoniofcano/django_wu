from django.db import models

class WeatherData(models.Model):
    epoch = models.IntegerField()
    humidityAvg = models.FloatField()
    humidityHigh = models.FloatField()
    humidityLow = models.FloatField()
    lat = models.FloatField()
    lon = models.FloatField()
    obsTimeLocal = models.DateTimeField()
    obsTimeUtc = models.DateTimeField()
    solarRadiationHigh = models.FloatField(null=True)
    stationID = models.CharField(max_length=255)
    tz = models.CharField(max_length=255)
    uvHigh = models.FloatField(null=True)
    winddirAvg = models.FloatField()
    dewptAvg = models.FloatField()
    dewptHigh = models.FloatField()
    dewptLow = models.FloatField()
    heatindexAvg = models.FloatField()
    heatindexHigh = models.FloatField()
    heatindexLow = models.FloatField()
    precipRate = models.FloatField()
    precipTotal = models.FloatField()
    pressureMax = models.FloatField()
    pressureMin = models.FloatField()
    pressureTrend = models.FloatField()
    qcStatus = models.IntegerField()
    tempAvg = models.FloatField()
    tempHigh = models.FloatField()
    tempLow = models.FloatField()
    windchillAvg = models.FloatField()
    windchillHigh = models.FloatField()
    windchillLow = models.FloatField()
    windgustAvg = models.FloatField()
    windgustHigh = models.FloatField()
    windgustLow = models.FloatField()
    windspeedAvg = models.FloatField()
    windspeedHigh = models.FloatField()
    windspeedLow = models.FloatField()
    etc = models.FloatField()
    water_req = models.FloatField()

    @staticmethod
    def get_last_date():
        last_entry = WeatherData.objects.order_by('-obsTimeUtc').first()
        if last_entry is not None:
            return last_entry.obsTimeUtc
        else:
            return None
