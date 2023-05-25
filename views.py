from django.views.generic import ListView, TemplateView
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import WeatherData

from django.db.models import F
#from django.db.models.functions import ExtractWeek, ExtractMonth
from django.db.models.functions import TruncWeek, TruncMonth


import requests
from django.shortcuts import render
from django.conf import settings

class WeatherForecast(TemplateView):
    template_name = 'weather_forecast.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Realizar la llamada a la API y extraer los valores
        api_url = "https://api.weather.com/v3/wx/forecast/daily/5day"
        params = {
            "geocode": settings.WU_STATION_LAT + ',' + settings.WU_STATION_LON,
            "format": "json",
            "units": "m",
            "language": "es-ES",
            "apiKey": settings.WU_API_KEY
        }

        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
        
            combined_data = list(zip(data['daypart'][0]['precipChance'], data['daypart'][0]['qpf']))
 
            context['combined_data'] = combined_data
            context['weather_forecast'] = data
        else:
            error_message = "Error al obtener los datos del pronóstico del tiempo."
            context['error_message'] = error_message
            context['error_template'] = 'error.html'

        return context

class WeatherCurrent(TemplateView):
    template_name = 'weather_current.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Realizar la llamada a la API y extraer los valores
        api_url = "https://api.weather.com/v2/pws/observations/current"
        params = {
            "stationId": settings.WU_STATION_ID,
            "format": "json",
            "units": "m",
            "apiKey": settings.WU_API_KEY
        }
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()

            observations = data["observations"]
            if observations:
                observation = observations[0]  # Tomar solo la primera observación
                context = {
                    "stationID": observation["stationID"],
                    "obsTimeUtc": observation["obsTimeUtc"],
                    "obsTimeLocal": observation["obsTimeLocal"],
                    "neighborhood": observation["neighborhood"],
                    "country": observation["country"],
                    "lat": observation["lat"],
                    "lon": observation["lon"],
                    "humidity": observation["humidity"],
                    "temp": observation["metric"]["temp"],
                    "heatIndex": observation["metric"]["heatIndex"],
                    "dewpt": observation["metric"]["dewpt"],
                    "windChill": observation["metric"]["windChill"],
                    "windSpeed": observation["metric"]["windSpeed"],
                    "windGust": observation["metric"]["windGust"],
                    "pressure": observation["metric"]["pressure"],
                    "precipRate": observation["metric"]["precipRate"],
                    "precipTotal": observation["metric"]["precipTotal"],
                    "elev": observation["metric"]["elev"],
                }
            else:
                context = {}  # Si no hay observaciones, enviar un contexto vacío
        else:
            error_message = "Error al obtener los valores actuales de la estación."
            context['error_message'] = error_message
            context['error_template'] = 'error.html'
   
        return context


class WeatherDataListView(ListView):
    model = WeatherData
    template_name = 'weatherdata_list.html'
    context_object_name = 'weatherdata_list'
    paginate_by = 10  # Número de elementos por página


    def get_queryset(self):
        queryset = super().get_queryset()

        # Obtener el valor del parámetro 'summary' de la URL (semanal o mensual)
        summary = self.request.GET.get('summary', None)

        # Aplicar resumen semanal o mensual y calcular la media de etc y tempLow
        if summary == 'semanal':
            queryset = queryset.annotate(week=TruncWeek('obsTimeLocal'))
            queryset = queryset.values('week').annotate(
                                                           tempAvg=Avg('tempAvg'),
                                                           tempHigh=Avg('tempHigh'),
                                                           tempLow=Avg('tempLow'),
                                                           humidityAvg=Avg('humidityAvg'),
                                                           humidityHigh=Avg('humidityHigh'),
                                                           humidityLow=Avg('humidityLow'),
                                                           dewptAvg=Avg('dewptAvg'),
                                                           precipRate=Avg('precipRate'),
                                                           precipTotal=Avg('precipTotal'),
                                                           pressureMax=Avg('pressureMax'),
                                                           pressureMin=Avg('pressureMin'),
                                                           pressureTrend=Avg('pressureTrend'),
                                                           windgustAvg=Avg('windgustAvg'),
                                                           windspeedAvg=Avg('windspeedAvg'),
                                                           winddirAvg=Avg('winddirAvg'),
                                                           etc=Avg('etc'),
                                                           water_req=Avg('water_req'),
                                                        ).order_by('week')
        elif summary == 'mensual':
            queryset = queryset.annotate(month=TruncMonth('obsTimeLocal'))
            queryset = queryset.values('month').annotate(
                                                           tempAvg=Avg('tempAvg'),
                                                           tempHigh=Avg('tempHigh'),
                                                           tempLow=Avg('tempLow'),
                                                           humidityAvg=Avg('humidityAvg'),
                                                           humidityHigh=Avg('humidityHigh'),
                                                           humidityLow=Avg('humidityLow'),
                                                           dewptAvg=Avg('dewptAvg'),
                                                           precipRate=Avg('precipRate'),
                                                           precipTotal=Avg('precipTotal'),
                                                           pressureMax=Avg('pressureMax'),
                                                           pressureMin=Avg('pressureMin'),
                                                           pressureTrend=Avg('pressureTrend'),
                                                           windgustAvg=Avg('windgustAvg'),
                                                           windspeedAvg=Avg('windspeedAvg'),
                                                           winddirAvg=Avg('winddirAvg'),
                                                           etc=Avg('etc'),
                                                           water_req=Avg('water_req'),
                                                        ).order_by('month')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el valor del parámetro 'summary' de la URL (semanal o mensual)
        summary = self.request.GET.get('summary', None)
        
        queryset = context['weatherdata_list']

        # Paginar los resultados
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        weatherdata_list = paginator.get_page(page)
        
        context['weatherdata_list'] = weatherdata_list
        context['summary'] = summary
        
        return context
