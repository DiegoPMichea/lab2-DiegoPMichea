import openmeteo_requests
from openmeteo_sdk.Variable import Variable
import requests
import folium
from folium.plugins import HeatMap
import json
import geonamescache

# API keys and clients
OPENWEATHERMAP_API_KEY = "52b5154533fcf3d1cfb8f475e69bc48c"
TOMORROW_IO_API_KEY = "l7aDY42v0zgyzC0C4wq1GV8KNQcYclf0"
om = openmeteo_requests.Client()

def load_countries_and_cities():
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    cities_dict = gc.get_cities()

    # List of top 30 countries by GDP with their ISO 3166-1 alpha-2 codes
    top_30_countries = [
        'US', 'CN', 'JP', 'DE', 'GB', 'IN', 'FR', 'IT', 'CA', 'BR',
        'RU', 'KR', 'AU', 'MX', 'ES', 'ID', 'NL', 'CH', 'SA', 'TR',
        'TW', 'PL', 'SE', 'BE', 'TH', 'IE', 'AR', 'NO', 'IL', 'SG'
    ]

    cities = []
    for country_code in top_30_countries:
        if country_code in countries:
            country_name = countries[country_code]['name']
            
            # Get cities for this country
            country_cities = [city for city in cities_dict.values() if city['countrycode'] == country_code]
            
            # Sort cities by population and take the top one
            if country_cities:
                largest_city = max(country_cities, key=lambda x: x['population'])
                
                cities.append({
                    "name": largest_city['name'],
                    "lat": largest_city['latitude'],
                    "lon": largest_city['longitude'],
                    "country": country_name
                })
    
    return cities

def get_weather_meteo(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"]
    }
    responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]
    current = response.Current()
    current_variables = list(map(lambda i: current.Variables(i), range(0, current.VariablesLength())))
    temp = next(filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, current_variables)).Value()
    humidity = next(filter(lambda x: x.Variable() == Variable.relative_humidity and x.Altitude() == 2, current_variables)).Value()
    weather_code = next(filter(lambda x: x.Variable() == Variable.weather_code, current_variables)).Value()
    return temp, humidity, weather_code

def get_weather_openweathermap(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp'], data['main']['humidity'], data['weather'][0]['id']
    return None, None, None

def get_weather_tomorrow(lat, lon):
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&apikey={TOMORROW_IO_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current = data['timelines']['minutely'][0]['values']
        return current['temperature'], current['humidity'], current['weatherCode']
    return None, None, None

def get_weather_description(weather_code, api):
    if weather_code is None:
        return "Unknown"
    
    if api == 'meteo':
        return "Clear" if weather_code == 0 else "Cloudy" if weather_code < 50 else "Rainy"
    elif api == 'openweathermap':
        return "Clear" if weather_code < 300 else "Cloudy" if weather_code < 500 else "Rainy"
    elif api == 'tomorrow':
        return "Clear" if weather_code < 1000 else "Cloudy" if weather_code < 4000 else "Rainy"
    else:
        return "Unknown"

cities = load_countries_and_cities()

map_weather = folium.Map(location=[0, 0], zoom_start=2)
heat_data = []
humidity_data = []

for city in cities:
    temp_meteo, humidity_meteo, weather_code_meteo = get_weather_meteo(city['lat'], city['lon'])
    temp_owm, humidity_owm, weather_code_owm = get_weather_openweathermap(city['name'])
    temp_tomorrow, humidity_tomorrow, weather_code_tomorrow = get_weather_tomorrow(city['lat'], city['lon'])

    temps = [t for t in [temp_meteo, temp_owm, temp_tomorrow] if t is not None]
    humidities = [h for h in [humidity_meteo, humidity_owm, humidity_tomorrow] if h is not None]

    if temps and humidities:
        avg_temp = sum(temps) / len(temps)
        avg_humidity = sum(humidities) / len(humidities)
        max_temp = max(temps)
        min_temp = min(temps)
        max_humidity = max(humidities)
        min_humidity = min(humidities)

        popup_text = f"{city['name']}:<br>" \
                     f"Temperature (°C): Avg {avg_temp:.1f}, Max {max_temp:.1f}, Min {min_temp:.1f}<br>" \
                     f"Humidity (%): Avg {avg_humidity:.1f}, Max {max_humidity:.1f}, Min {min_humidity:.1f}<br>" \
                     f"Conditions: {get_weather_description(weather_code_meteo, 'meteo')}/" \
                     f"{get_weather_description(weather_code_owm, 'openweathermap')}/" \
                     f"{get_weather_description(weather_code_tomorrow, 'tomorrow')}"

        folium.Marker(
            location=[city['lat'], city['lon']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_weather)

        heat_data.append([city['lat'], city['lon'], avg_temp])
        humidity_data.append([city['country'], avg_humidity])

HeatMap(heat_data).add_to(map_weather)

# Load GeoJSON data (world countries)
geo_json_data = json.load(open('C:\\repos\\lab2-DiegoPMichea\\countries.geojson'))

folium.Choropleth(
    geo_data=geo_json_data,
    name='choropleth',
    data=humidity_data,
    columns=['City', 'Humidity'],
    key_on='feature.properties.ADMIN',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Average Humidity (%)',
).add_to(map_weather)

folium.LayerControl().add_to(map_weather)

map_weather.save("weather_map_combined.html")