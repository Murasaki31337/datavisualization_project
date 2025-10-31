from prometheus_client import start_http_server, Gauge
import requests, time
from dotenv import load_dotenv
import os
load_dotenv()


API_KEY = os.getenv("OPENWEATHER_KEY")
CITY = "Astana"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# 10 metrics
temp = Gauge('weather_temperature_celsius', 'Current temperature in Celsius')
feels_like = Gauge('weather_feels_like_celsius', 'Feels-like temperature in Celsius')
humidity = Gauge('weather_humidity_percent', 'Humidity in percent')
pressure = Gauge('weather_pressure_hpa', 'Atmospheric pressure in hPa')
wind_speed = Gauge('weather_wind_speed_mps', 'Wind speed in meters per second')
wind_deg = Gauge('weather_wind_direction_deg', 'Wind direction in degrees')
clouds = Gauge('weather_cloudiness_percent', 'Cloudiness percentage')
visibility = Gauge('weather_visibility_m', 'Visibility in meters')
sunrise = Gauge('weather_sunrise_unix', 'Sunrise time (UNIX)')
sunset = Gauge('weather_sunset_unix', 'Sunset time (UNIX)')

def collect_weather():
    try:
        data = requests.get(URL).json()
        if "main" not in data:
            print("⚠️ Unexpected API response:", data)
            return
        main = data['main']
        wind = data.get('wind', {})
        sys = data.get('sys', {})
        clouds_data = data.get('clouds', {})

        temp.set(main['temp'])
        feels_like.set(main['feels_like'])
        humidity.set(main['humidity'])
        pressure.set(main['pressure'])
        wind_speed.set(wind.get('speed', 0))
        wind_deg.set(wind.get('deg', 0))
        clouds.set(clouds_data.get('all', 0))
        visibility.set(data.get('visibility', 0))
        sunrise.set(sys.get('sunrise', 0))
        sunset.set(sys.get('sunset', 0))

        print(f"✅ Updated metrics for {CITY}")
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    start_http_server(8000)
    print("🚀 Custom Exporter running at http://localhost:8000/metrics")
    while True:
        collect_weather()
        time.sleep(20)
