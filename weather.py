
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import datetime
import numpy as np

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
	"latitude": 52.52,
	"longitude": 13.41,
	"current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature"],
	"hourly": ["cloud_cover", "visibility","precipitation_probability"],
	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "daylight_duration", "rain_sum", "snowfall_sum", "precipitation_probability_max", "wind_speed_10m_max"],
	"timezone": "auto"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E") #
# print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}") #
print(f"Timezone difference to GMT+ {response.UtcOffsetSeconds()/3600}") #

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_apparent_temperature = current.Variables(2).Value()

print(f"Current time {datetime.datetime.fromtimestamp(current.Time()+response.UtcOffsetSeconds())}") #
print(f"Current temperature_2m - {round(current_temperature_2m)}\xb0 C") # celcius
print(f"Current relative_humidity_2m - {round(current_relative_humidity_2m)}%") # percent
print(f"Current apparent_temperature - {round(current_apparent_temperature)}\xb0 C") # celcius

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

n7cloudcover = np.array(hourly_dataframe1.cloud_cover) #
print(n7cloudcover) #percent

n7visibility = np.array(hourly_dataframe1.visibility) #
print(n7visibility) #kms

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code1 = daily.Variables(0).ValuesAsNumpy()
daily_weather_code =[]
for i in daily_weather_code1:
    daily_weather_code.append(weather_conditions
                              [int(i)])
daily_temperature_2m_max = np.round(daily.Variables(1).ValuesAsNumpy()).astype(int)
daily_temperature_2m_min = np.round(daily.Variables(2).ValuesAsNumpy()).astype(int)
daily_apparent_temperature_max = np.round(daily.Variables(3).ValuesAsNumpy()).astype(int)
daily_apparent_temperature_min = np.round(daily.Variables(4).ValuesAsNumpy()).astype(int)
daily_daylight_duration = np.round(daily.Variables(5).ValuesAsNumpy()/3600).astype(int)
daily_rain_sum = np.round(daily.Variables(6).ValuesAsNumpy()/10).astype(int)
daily_snowfall_sum = daily.Variables(7).ValuesAsNumpy().astype(int)
daily_precipitation_probability_max = daily.Variables(8).ValuesAsNumpy().astype(int)
daily_wind_speed_10m_max = np.round(daily.Variables(9).ValuesAsNumpy()).astype(int)

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time()+response.UtcOffsetSeconds(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd()+response.UtcOffsetSeconds(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["weather_code"] = daily_weather_code # summary
daily_data["temperature_2m_max"] = daily_temperature_2m_max # celcius
daily_data["temperature_2m_min"] = daily_temperature_2m_min # celcius
daily_data["apparent_temperature_max"] = daily_apparent_temperature_max # celcius
daily_data["apparent_temperature_min"] = daily_apparent_temperature_min # celcius
daily_data["daylight_duration"] = daily_daylight_duration # hours
daily_data["rain_sum"] = daily_rain_sum # cms
daily_data["snowfall_sum"] = daily_snowfall_sum # cms
# daily_data["precipitation_hours"] = daily_precipitation_hours
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max # percent
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max # kmph

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)



