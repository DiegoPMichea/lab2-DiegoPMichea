import requests
import folium
from folium.plugins import HeatMap
import json
import geonamescache

API_KEY = "l7aDY42v0zgyzC0C4wq1GV8KNQcYclf0"

def get_weather(lat, lon):
    # Hämta väderdata från Tomorrow.io API
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def load_countries_and_cities():
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    cities_dict = gc.get_cities()

    # Lista över de 30 största länderna efter BNP med deras ISO 3166-1 alpha-2 koder
    top_30_countries = [
        'US', 'CN', 'JP', 'DE', 'GB', 'IN', 'FR', 'IT', 'CA', 'BR',
        'RU', 'KR', 'AU', 'MX', 'ES', 'ID', 'NL', 'CH', 'SA', 'TR',
        'TW', 'PL', 'SE', 'BE', 'TH', 'IE', 'AR', 'NO', 'IL', 'SG'
    ]

    cities = []
    for country_code in top_30_countries:
        if country_code in countries:
            country_name = countries[country_code]['name']
            
            # Hämta städer för detta land
            country_cities = [city for city in cities_dict.values() if city['countrycode'] == country_code]
            
            # Sortera städer efter befolkning och ta den största
            if country_cities:
                largest_city = max(country_cities, key=lambda x: x['population'])
                
                cities.append({
                    "name": largest_city['name'],
                    "lat": largest_city['latitude'],
                    "lon": largest_city['longitude'],
                    "country": country_name
                })
    
    return cities

# Ladda städer från de 30 största länderna
cities = load_countries_and_cities()

# Skapa en karta med folium
map_weather = folium.Map(location=[0, 0], zoom_start=2)
heat_data = []
humidity_data = []

for city in cities:
    # Hämta väderdata för varje stad
    weather_data = get_weather(city['lat'], city['lon'])
    if weather_data:
        current = weather_data['timelines']['minutely'][0]['values']
        temp = current['temperature']
        humidity = current['humidity']
        weather_code = current['weatherCode']

        # Bestäm väderbeskrivning baserat på väderkoden
        weather_desc = "Clear" if weather_code < 1000 else "Cloudy" if weather_code < 4000 else "Rainy"

        # Skapa popup-text för varje stad
        popup_text = f"{city['name']}:<br>Temperature: {temp:.1f} °C<br>Humidity: {humidity:.1f}%<br>Condition: {weather_desc}"

        # Lägg till en markör för varje stad på kartan
        folium.Marker(
            location=[city['lat'], city['lon']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_weather)

        # Lägg till data för värmekarta och fuktighetskarta
        heat_data.append([city['lat'], city['lon'], temp])
        humidity_data.append([city['country'], humidity])

# Lägg till värmekarta till folium-kartan
HeatMap(heat_data).add_to(map_weather)

# Ladda GeoJSON-data (världens länder)
geo_json_data = json.load(open('C:\\repos\\lab2-DiegoPMichea\\countries.geojson'))

# Skapa en koropletkarta för fuktighet
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

# Lägg till lagerkontroll till kartan
folium.LayerControl().add_to(map_weather)

# Spara kartan som en HTML-fil
map_weather.save("weather_map_tomorrow.html")
