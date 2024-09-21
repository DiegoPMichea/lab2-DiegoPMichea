import openmeteo_requests
from openmeteo_sdk.Variable import Variable
import geonamescache
import folium
from folium.plugins import HeatMap
import json

def load_countries_and_cities():
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    cities_dict = gc.get_cities()

    top_30_countries = [
        'US', 'CN', 'JP', 'DE', 'GB', 'IN', 'FR', 'IT', 'CA', 'BR',
        'RU', 'KR', 'AU', 'MX', 'ES', 'ID', 'NL', 'CH', 'SA', 'TR',
        'TW', 'PL', 'SE', 'BE', 'TH', 'IE', 'AR', 'NO', 'IL', 'SG'
    ]

    cities = []
    for country_code in top_30_countries:
        if country_code in countries:
            country_name = countries[country_code]['name']
            country_cities = [city for city in cities_dict.values() if city['countrycode'] == country_code]
            if country_cities:
                largest_city = max(country_cities, key=lambda x: x['population'])
                cities.append({
                    "name": largest_city['name'],
                    "lat": largest_city['latitude'],
                    "lon": largest_city['longitude'],
                    "country": country_name
                })
    return cities

cities = load_countries_and_cities()

om = openmeteo_requests.Client()
map_weather = folium.Map(location=[0, 0], zoom_start=2)
heat_data = []
humidity_data = []

for city in cities:
    params = {
        "latitude": city['lat'],
        "longitude": city['lon'],
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"]
    }

    responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]
    
    current = response.Current()
    current_variables = list(map(lambda i: current.Variables(i), range(0, current.VariablesLength())))
    current_temperature_2m = next(filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, current_variables))
    current_relative_humidity_2m = next(filter(lambda x: x.Variable() == Variable.relative_humidity and x.Altitude() == 2, current_variables))
    current_weather_code = next(filter(lambda x: x.Variable() == Variable.weather_code, current_variables))

    temp = current_temperature_2m.Value()
    humidity = current_relative_humidity_2m.Value()
    weather_code = current_weather_code.Value()

    weather_desc = "Clear" if weather_code == 0 else "Cloudy" if weather_code < 50 else "Rainy"

    popup_text = f"{city['name']}:<br>Temperature: {temp:.1f} °C<br>Humidity: {humidity:.1f}%<br>Condition: {weather_desc}"

    folium.Marker(
        location=[city['lat'], city['lon']],
        popup=popup_text,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(map_weather)

    heat_data.append([city['lat'], city['lon'], temp])
    humidity_data.append([city['country'], humidity])

HeatMap(heat_data).add_to(map_weather)

# Load GeoJSON data (world countries)
geo_json_data = json.load(open('C:\\repos\\lab2-DiegoPMichea\\countries.geojson'))  # Replace with your GeoJSON file path

folium.Choropleth(
    geo_data=geo_json_data,
    name='choropleth',
    data=humidity_data,
    columns=['City', 'Humidity'],
    key_on='feature.properties.ADMIN',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Humidity (%)',
).add_to(map_weather)

folium.LayerControl().add_to(map_weather)

map_weather.save("weather_map_meteo.html")