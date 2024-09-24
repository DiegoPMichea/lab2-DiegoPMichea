import requests
import folium
from folium.plugins import HeatMap
import json
import geonamescache

api_key = "52b5154533fcf3d1cfb8f475e69bc48c"

# Funktion för att hämta väderdata för en given stad
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Funktion för att ladda länder och städer
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

# Ersätt den befintliga städer listan med den nya funktionen
cities = load_countries_and_cities()

# Skapa en karta centrerad runt Europa
map_weather = folium.Map(location=[0, 0], zoom_start=2)

# Samla data för värmekarta och luftfuktighet
heat_data = []
humidity_data = []

# Lägg till markörer för varje stad
for city in cities:
    weather_data = get_weather(city['name'])
    if weather_data:
        # Extrahera relevant väderinformation
        temp = weather_data['main']['temp']
        weather_desc = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        
        # Skapa ett popup-meddelande
        popup_text = f"{city['name']}:<br>Temperature: {temp} °C<br>Humidity: {humidity}%<br>Condition: {weather_desc}"
        
        # Lägg till en markör på kartan
        folium.Marker(
            location=[city['lat'], city['lon']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_weather)
        
        # Lägg till data för värmekarta (använder temperatur som intensitet)
        heat_data.append([city['lat'], city['lon'], temp])

        # Lägg till luftfuktighetsdata för choropleth (nyckel: stadens namn)
        humidity_data.append([city['country'], humidity])

# Lägg till värmekartlager för temperatur
HeatMap(heat_data).add_to(map_weather)

# Ladda GeoJSON-data (världens länder)
geo_json_data = json.load(open('C:\\repos\\lab2-DiegoPMichea\\countries.geojson'))  # Ersätt med din GeoJSON-filväg

# Choropleth för luftfuktighet
folium.Choropleth(
    geo_data=geo_json_data,
    name='choropleth',
    data=humidity_data,
    columns=['City', 'Humidity'],  # Choropleth förväntar sig 'kolumner' av data, som ska matcha din humidity_data
    key_on='feature.properties.ADMIN',  # Justera detta för att matcha hur din GeoJSON lagrar landnamn
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Humidity (%)',
).add_to(map_weather)

# Lägg till lagerkontroll för att växla mellan choropleth och värmekarta
folium.LayerControl().add_to(map_weather)

# Spara kartan till en HTML-fil
map_weather.save("weather_map_openweathermap.html")