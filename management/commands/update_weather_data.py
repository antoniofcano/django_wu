from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django_wu.models import WeatherData

from django.utils.timezone import make_aware, get_current_timezone

from datetime import datetime, date

from agro_calculations import AgroCalculations
from estacion_meteorologica import EstacionMeteorologica


class Command(BaseCommand):
    help = 'Actualiza los datos meteorológicos de Weather Underground'

    def add_arguments(self, parser):
        parser.add_argument('growth_stage', type=str, help='Indica el growth stage para actualizar la base de datos.')

    def handle(self, *args, **options):
        weather_data = WeatherData()

        growth_stage = options['growth_stage']
        
        # Lista de growth stages válidos
        valid_growth_stages = ['parada_invernal', 'desarrollo', 'cuajado', 'maduración']

        # Verifica si el growth stage proporcionado es válido
        if growth_stage not in valid_growth_stages:
            raise CommandError(f"Growth stage '{growth_stage}' no es válido. Los valores válidos son: {', '.join(valid_growth_stages)}")
        
        # Verifica si last_date es None y establece una fecha de inicio predeterminada si es así
        last_date = weather_data.get_last_date()

        if last_date:
            fecha_inicio = last_date.date()
        else:
            fecha_inicio = date(2021, 12, 25)

        print(' Va a ejecutar la llamada al API WU ' )

        # Crea una instancia de tu clase EstacionMeteorologica
        estacion = EstacionMeteorologica(settings.WU_API_KEY, settings.WU_STATION_ID)


        # Llama al método de esta clase que obtiene los nuevos datos
        estacion.obtener_datos_estacion(fecha_inicio)
        estacion.limpieza_datos()
        new_data = estacion.get_datos()
    
        # Añade los nuevos datos a la base de datos
        for data in new_data.to_dict('records'):
            weather_data = WeatherData()
            calculations = AgroCalculations(settings.WU_STATION_LAT, settings.WU_STATION_ELEVATION, growth_stage)

            obs_time_local = datetime.strptime(data['obsTimeLocal'], "%Y-%m-%d %H:%M:%S")
            day_of_year = obs_time_local.timetuple().tm_yday
            etc = calculations.penman_monteith_modified(
                data['metric.tempHigh'], 
                data['metric.tempLow'], 
                data['metric.tempAvg'], 
                data['humidityHigh'], 
                data['humidityLow'], 
                day_of_year
            )
            water_required = calculations.calculate_water_required(etc, data['metric.precipTotal'] )

            weather_data.epoch = data['epoch']
            weather_data.humidityAvg = data['humidityAvg']
            weather_data.humidityHigh = data['humidityHigh']
            weather_data.humidityLow = data['humidityLow']
            weather_data.lat = data['lat']
            weather_data.lon = data['lon']

            weather_data.obsTimeLocal = make_aware(obs_time_local, get_current_timezone())

            obs_time_utc = datetime.strptime(data['obsTimeUtc'], "%Y-%m-%dT%H:%M:%SZ")
            weather_data.obsTimeUtc = make_aware(obs_time_utc, get_current_timezone())
          
            weather_data.solarRadiationHigh = data['solarRadiationHigh']
            weather_data.stationID = data['stationID'] 
            weather_data.tz = data['tz'] 
            weather_data.uvHigh = data['uvHigh']
            weather_data.winddirAvg = data['winddirAvg']
            weather_data.dewptAvg = data['metric.dewptAvg']
            weather_data.dewptHigh = data['metric.dewptHigh']
            weather_data.dewptLow = data['metric.dewptLow']
            weather_data.heatindexAvg = data['metric.heatindexAvg']
            weather_data.heatindexHigh = data['metric.heatindexHigh']
            weather_data.heatindexLow = data['metric.heatindexLow']
            weather_data.precipRate = data['metric.precipRate']
            weather_data.precipTotal = data['metric.precipTotal']
            weather_data.pressureMax = data['metric.pressureMax']
            weather_data.pressureMin = data['metric.pressureMin']
            weather_data.pressureTrend = data['metric.pressureTrend']
            weather_data.qcStatus = data['qcStatus']
            weather_data.tempAvg = data['metric.tempAvg']
            weather_data.tempHigh = data['metric.tempHigh']
            weather_data.tempLow = data['metric.tempLow']
            weather_data.windchillAvg = data['metric.windchillAvg']
            weather_data.windchillHigh = data['metric.windchillHigh']
            weather_data.windchillLow = data['metric.windchillLow']
            weather_data.windgustAvg = data['metric.windgustAvg']
            weather_data.windgustHigh = data['metric.windgustHigh']
            weather_data.windgustLow = data['metric.windgustLow']
            weather_data.windspeedAvg = data['metric.windspeedAvg']
            weather_data.windspeedHigh = data['metric.windspeedHigh']
            weather_data.windspeedLow = data['metric.windspeedLow']
            weather_data.etc = etc
            weather_data.water_req = water_required 

            weather_data.save()


        self.stdout.write(self.style.SUCCESS('Base de datos actualizada exitosamente.'))
