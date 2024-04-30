from harsh import get_weather
import json
import pprint
a =json.loads(get_weather(52.52,13.41))
print(a['Latlong'])