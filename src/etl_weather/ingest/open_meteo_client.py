# Ouvrir un client pour l'API Open Meteo
import requests
import os

# Charger les variables d'environnement
API_BASE_FORECAST = os.getenv(
    "OPEN_METEO_BASE", "https://api.open-meteo.com/v1/forecast"
)

API_BASE_ARCHIVE = os.getenv(
    "OPEN_METEO_ARCHIVE_BASE", "https://archive-api.open-meteo.com/v1/archive"
)

DAILY_VARS = "temperature_2m_max,temperature_2m_min,precipitation_sum"


# Appel à l'API Open Meteo pour obtenir les prévisions météorologiques
def fetch_forecast(lat, lon, start_date, end_date, timezone="Europe/Paris", timeout=15):
    """Appel à l'API Open Meteo pour obtenir les prévisions météorologiques."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_VARS,
        "timezone": timezone,
    }
    response = requests.get(API_BASE_FORECAST, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


# Appel à l'API Open Meteo pour obtenir les données météorologiques archivées
def fetch_archive(lat, lon, start_date, end_date, timezone="Europe/Paris", timeout=15):
    """Appel à l'API Open Meteo pour obtenir les données météorologiques archivées."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_VARS,
        "timezone": timezone,
    }
    response = requests.get(API_BASE_ARCHIVE, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()
