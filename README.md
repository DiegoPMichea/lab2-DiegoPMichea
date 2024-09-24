# Väderkarta Projekt

Projektet är skapat av:
- Diego Pino, Data Engineering student på Nackademin.

Tack till alla free API:er som används i projektet
- OpenWeatherMap
- Tomorrow.io
- Open-Meteo

och till Natural Earth, Lexman och Open Knowledge Foundation för de free kartor som används i projektet.

## Översikt
Detta projekt syftar till att skapa en interaktiv väderkarta med hjälp av olika väder-API:er. Projektet använder Python för att hämta väderdata från OpenWeatherMap, Tomorrow.io och Open-Meteo, och visualiserar denna data på en karta med hjälp av Folium.

## Filer

### 1. `Runthisfirst.cmd`
Denna fil är ett batch-skript som installerar alla nödvändiga Python-paket för projektet. Skriptet:
- Installerar beroenden som `requests`, `folium`, `geonamescache`, `openmeteo-requests` och `openmeteo-sdk`.

### 2. `OpenWeatherMapAPI.py`
Denna fil innehåller ett Python-skript som hämtar väderdata från OpenWeatherMap API och visualiserar den på en karta. Skriptet:
- Hämtar väderdata för de största städerna i de 30 största länderna efter BNP.
- Skapar en karta med markörer som visar temperatur, luftfuktighet och väderförhållanden för varje stad.
- Lägger till en värmekarta baserad på temperatur och en koropletkarta baserad på luftfuktighet.

### 3. `Tomorrow.ioAPI.py`
Denna fil innehåller ett Python-skript som hämtar väderdata från Tomorrow.io API och visualiserar den på en karta. Skriptet:
- Hämtar väderdata för de största städerna i de 30 största länderna efter BNP.
- Skapar en karta med markörer som visar temperatur, luftfuktighet och väderförhållanden för varje stad.
- Lägger till en värmekarta baserad på temperatur och en koropletkarta baserad på luftfuktighet.

### 4. `MeteoAPI.py`
Denna fil innehåller ett Python-skript som hämtar väderdata från Open-Meteo API och visualiserar den på en karta. Skriptet:
- Hämtar väderdata för de största städerna i de 30 största länderna efter BNP.
- Skapar en karta med markörer som visar temperatur, luftfuktighet och väderförhållanden för varje stad.
- Lägger till en värmekarta baserad på temperatur och en koropletkarta baserad på luftfuktighet.

### 5. `FinalWeather.py`
Denna fil kombinerar data från OpenWeatherMap, Tomorrow.io och Open-Meteo API:er. Skriptet:
- Hämtar väderdata från alla tre källor för de största städerna i de 30 största länderna efter BNP.
- Beräknar genomsnittliga värden för temperatur och luftfuktighet.
- Skapar en karta med markörer som visar genomsnittlig temperatur, luftfuktighet och väderförhållanden för varje stad.
- Lägger till en värmekarta baserad på genomsnittlig temperatur och en koropletkarta baserad på genomsnittlig luftfuktighet.

### 6. `html filer`
Dessa filer är de html filer som visar kartorna. De heter:
- `weather_map_openweather.html`
- `weather_map_tomorrow.html`
- `weather_map_meteo.html`
- `weather_map_combined.html`

For att visa kartorna, kör `FinalWeather.py` och öppna den html fil som visas i din default webbläsare (om du kör filen i Pycharm, VS code eller liknande, du kan högerklicka på filen och välja "Open with live server" för att öppna den i din default webbläsare).
