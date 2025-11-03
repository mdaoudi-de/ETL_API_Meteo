# Appel à l'API Open Meteo pour obtenir les prévisions météorologiques

from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import json
from src.etl_weather.ingest.open_meteo_client import fetch_forecast

CITIES_FILE = Path("config/cities.csv")
RAW_ROOT = Path("data/raw/forecast")
RAW_ROOT.mkdir(parents=True, exist_ok=True)

def _slug(name: str) -> str:
    """Convertit un nom de ville en une version adptée pour les noms de fichiers."""
    return name.lower().replace(" ", "_")

def main():
    """Récupère les prévisions météorologiques pour les villes listées dans le fichier de configuration."""
    cities = pd.read_csv(CITIES_FILE)
    today = date.today()
    start = today
    end = today + timedelta(days=7)

    for _, row in cities.iterrows():
        city , lat, lon = row["city"], row["lat"], row["lon"]
        slug = _slug(city)
        out_dir = RAW_ROOT / f"date={today.isoformat()}" / f"city={slug}"
        out_dir.mkdir(parents=True, exist_ok=True)

        data = fetch_forecast(lat, lon, str(start), str(end))
        (out_dir / "part-0000.jsonl").write_text(json.dumps(data) + "\n", encoding="utf-8")
        print(f"✅ forecast → {out_dir}/part-0000.jsonl")

if __name__ == "__main__":
    main()