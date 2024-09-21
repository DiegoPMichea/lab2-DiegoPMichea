import requests
import folium
from folium.plugins import HeatMap
import json
import geonamescache

api_key = "52b5154533fcf3d1cfb8f475e69bc48c"


# Function to fetch weather data for a given city
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

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

# Replace the existing cities list with the new function
cities = load_countries_and_cities()

# Create a map centered around Europe
map_weather = folium.Map(location=[0, 0], zoom_start=2)

# Collect data for heatmap and humidity
heat_data = []
humidity_data = []

# Add markers for each city
for city in cities:
    weather_data = get_weather(city['name'])
    if weather_data:
        # Extract relevant weather information
        temp = weather_data['main']['temp']
        weather_desc = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        
        # Create a popup message
        popup_text = f"{city['name']}:<br>Temperature: {temp} °C<br>Humidity: {humidity}%<br>Condition: {weather_desc}"
        
        # Add a marker to the map
        folium.Marker(
            location=[city['lat'], city['lon']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_weather)
        
        # Append data for heatmap (using temperature as intensity)
        heat_data.append([city['lat'], city['lon'], temp])

        # Add humidity data for choropleth (key: city name)
        humidity_data.append([city['country'], humidity])

# Add heatmap layer for temperature
HeatMap(heat_data).add_to(map_weather)

# Load GeoJSON data (world countries)
geo_json_data = json.load(open('C:\\repos\\lab2-DiegoPMichea\\countries.geojson'))  # Replace with your GeoJSON file path

# Choropleth for humidity
folium.Choropleth(
    geo_data=geo_json_data,
    name='choropleth',
    data=humidity_data,
    columns=['City', 'Humidity'],  # Choropleth expects 'columns' of data, which should match your humidity_data
    key_on='feature.properties.ADMIN',  # Adjust this to match how your GeoJSON stores country names
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Humidity (%)',
).add_to(map_weather)

# Add layer control to toggle between choropleth and heatmap
folium.LayerControl().add_to(map_weather)

# Save the map to an HTML file
map_weather.save("weather_map_openweathermap.html")



#url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

#response = requests.get(url)
#data = response.json()

#if response.status_code == 200:
#    print(f"City: {data['name']}")
#    print(f"Temperature: {data['main']['temp']} °C")
#    print(f"Weather: {data['weather'][0]['description']}")
#    print(f"Humidity: {data['main']['humidity']}%")
#    print(f"Wind Speed: {data['wind']['speed']} m/s")
#else:
#    print(f"Error fetching data: {data['message']}")