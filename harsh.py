import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import datetime
import numpy as np
import json

def get_weather(lat=52.52,long=13.41):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    
    weather_conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Cloudy",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light intensity",
        53: "Drizzle: Moderate intensity",
        55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light intensity",
        57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight intensity",
        63: "Rain: Moderate intensity",
        65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light intensity",
        67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight intensity",
        73: "Snow fall: Moderate intensity",
        75: "Snow fall: Heavy intensity",
        77: "Snow grains",
        80: "Rain showers: Slight intensity",
        81: "Rain showers: Moderate intensity",
        82: "Rain showers: Violent intensity",
        85: "Snow showers: Slight intensity",
        86: "Snow showers: Heavy intensity",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    """
    daily_weather_code =[]
    for i in daily_weather_code1:
        daily_weather_code.append(weather_conditions
                                  [int(i)])
                                  """
    params = {
    	"latitude": lat,
    	"longitude": long,
    	"current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature"],
    	"hourly": ["cloud_cover", "visibility","precipitation_probability"],
    	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "daylight_duration", "rain_sum", "snowfall_sum", "precipitation_probability_max", "wind_speed_10m_max"],
    	"timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_cloud_cover = hourly.Variables(0).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(1).ValuesAsNumpy()/1000
    hourly_precip_prob = hourly.Variables(2).ValuesAsNumpy()
    hourly_data = {"date": pd.date_range(
    	start = pd.to_datetime(hourly.Time()+response.UtcOffsetSeconds(), unit = "s", utc = True),
    	end = pd.to_datetime(hourly.TimeEnd()+response.UtcOffsetSeconds(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )}
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["visibility"] = hourly_visibility
    hourly_dataframe = pd.DataFrame(data = hourly_data)

    newList  = np.round(np.divide(np.array_split(hourly_precip_prob, 7), 100))


    def find_ones_indices(arr):
        return [i+1 for i, x in enumerate(arr) if x == 1]
    hrs_of_precip =[]
    for i in range(len(newList)):
        arr = newList[i]
        indices_of_ones = find_ones_indices(arr)
        # print(indices_of_ones)
        hrs_of_precip.append(indices_of_ones)

# hrs_of_precip # hours of day

    hourly_dataframe1 = hourly_dataframe.groupby([hourly_dataframe['date'].dt.date]).mean()
    hourly_dataframe1=hourly_dataframe1.drop('date', axis=1)
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    n7cloudcover = np.array(hourly_dataframe1.cloud_cover) #
    n7cloudcover = [int(x) for x in n7cloudcover]
    n7visibility = np.array(hourly_dataframe1.visibility) #
    n7visibility = [int(x) for x in n7visibility]
    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_weather_code1 = daily.Variables(0).ValuesAsNumpy()
    daily_weather_code =[]  # summary
    for i in daily_weather_code1:
        daily_weather_code.append(weather_conditions
                                  [int(i)])
    daily_temperature_2m_max = np.round(daily.Variables(1).ValuesAsNumpy()).astype(int) # celcius
    daily_temperature_2m_min = np.round(daily.Variables(2).ValuesAsNumpy()).astype(int) # celcius
    daily_apparent_temperature_max = np.round(daily.Variables(3).ValuesAsNumpy()).astype(int) # celcius
    daily_apparent_temperature_min = np.round(daily.Variables(4).ValuesAsNumpy()).astype(int) # celcius
    daily_daylight_duration = np.round(daily.Variables(5).ValuesAsNumpy()/3600).astype(int) # hours
    Nightduration = [int(abs(x - 24)) for x in daily_daylight_duration] # hours
    daily_rain_sum = np.round(daily.Variables(6).ValuesAsNumpy()/10).astype(int) # cms
    daily_snowfall_sum = daily.Variables(7).ValuesAsNumpy().astype(int) # cms
    daily_precipitation_probability_max = daily.Variables(8).ValuesAsNumpy().astype(int) # percent
    daily_wind_speed_10m_max = np.round(daily.Variables(9).ValuesAsNumpy()).astype(int)  # kmph
    data = {
        "Latlong": f"Lat {response.Latitude()} N, Long {response.Longitude()} E",
        "Timezone": f"Timezone - {response.Timezone().decode('utf-8')} {response.TimezoneAbbreviation().decode('utf-8')} GMT+ {response.UtcOffsetSeconds()/3600}" ,
        "Currentdate":f"Today's date - {datetime.datetime.fromtimestamp(current.Time()).date()}", #+response.UtcOffsetSeconds()
        "Currenttemp": f"Current Temperature - {round(current_temperature_2m)} C",
        "Currenthumidity":f"Current Humidity - {round(current_relative_humidity_2m)}%",
        "Feelsliketemp":f"Current Feels like Temperature - {round(current_apparent_temperature)} C",
        "Cloudcover": f"Here's the Cloudcover for today, along with the forecast for the upcoming six days(in percentage) - {str(n7cloudcover)[1:-1]}",
        "Visibility": f"Here's the Visibility for today, along with the forecast for the upcoming six days(in meters) - {str(n7visibility)[1:-1]}",
        "Weathercode": f"Here's the Weather is today, along with the forecast for the upcoming six days - {str(daily_weather_code)[1:-1]}",
        "Dailytempmax": f"Here's the Expected maximum temperature for today, along with the forecast for the upcoming six days(in celcius) - {str(daily_temperature_2m_max)[1:-1]}",
        "Dailytempmin": f"Here's the Expected minimum temperature for today, along with the forecast for the upcoming six days(in celcius) - {str(daily_temperature_2m_min)[1:-1]}",
        "Dailyfeelsliketempmax": f"Here's the Feels like maximum temperature for today, along with the forecast for the upcoming six days(in celcius) - {str(daily_apparent_temperature_max)[1:-1]}",
        "Dailyfeelsliketempmin": f"Here's the Feels like minimum temperature for today, along with the forecast for the upcoming six days(in celcius) - {str(daily_apparent_temperature_min)[1:-1]}",
        "Dailydaylightduration": f"Here's the Expected Day duration for today, along with the forecast for the upcoming six days(in hours) - {str(daily_daylight_duration)[1:-1]}",
        "Dailynightduration": f"Here's the Expected Night duration for today, along with the forecast for the upcoming six days(in hours) - {str(Nightduration)[1:-1]}",
        "Dailyrainsum": f"Here's the Expected amount of rain for today, along with the forecast for the upcoming six days(in cms) - {str(daily_rain_sum)[1:-1]}",
        "Dailysnowfallsum": f"Here's the Expected amount of snow for today, along with the forecast for the upcoming six days(in cms) - {str(daily_snowfall_sum)[1:-1]}",
        "Dailyprecipitationprobabilitymax": f"Here's the maximum chance of Precipitation for today, along with the forecast for the upcoming six days(in percentage) - {str(daily_precipitation_probability_max)[1:-1]}",
        "Dailywindspeedmax": f"Here's the Expected maximum wind speed for today, along with the forecast for the upcoming six days(in kmph) - {str(daily_wind_speed_10m_max)[1:-1]}",  
        "currentoverviewweather":f"Lat {response.Latitude()} N, Long {response.Longitude()} E Today's date - {datetime.datetime.fromtimestamp(current.Time()).date()} Timezone - {response.Timezone().decode('utf-8')} {response.TimezoneAbbreviation().decode('utf-8')} GMT+ {response.UtcOffsetSeconds()/3600} Current weather - {str(daily_weather_code[0])} Current Temperature - {round(current_temperature_2m)} C Current Feels like Temperature - {round(current_apparent_temperature)} C Current Humidity - {round(current_relative_humidity_2m)}% The maximum chance of Precipitation - {str(daily_precipitation_probability_max[0])}% "
            }
    
    return json.dumps(data)
    
