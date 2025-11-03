# Appel  à l'API Open Meteo pour obtenir les données météorologiques archivées

from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import json
import shutil
from src.etl_weather.ingest.open_meteo_client import fetch_archive

CITIES_FILE = Path("config/cities.csv")
RAW_ROOT = Path("data/raw/archive")
RAW_ROOT.mkdir(parents=True, exist_ok=True)

def _slug(name: str) -> str:
    """Convertit un nom de ville en une version adptée pour les noms de fichiers.
    param name: Nom de la ville"""
    return name.lower().replace(" ", "_")

def main():
    """Récupère les données météorologiques archivées pour les villes listées dans le fichier de configuration."""
    cities = pd.read_csv(CITIES_FILE)
    today = date.today()
    start = today - timedelta(days=30)
    end = today - timedelta(days=1)

    # Suppression des dossiers plus ancien que la date du jour
    for old_dir in RAW_ROOT.glob("date=*"):
        folder_date = old_dir.name.split("=")[1]
        if folder_date < today.isoformat():
            shutil.rmtree(old_dir)
            print(f"🗑️  Ancien dossier supprimé : {old_dir}")

    for _, row in cities.iterrows():
        city , lat, lon = row["city"], row["lat"], row["lon"]
        slug = _slug(city)
        out_dir = RAW_ROOT / f"date={today.isoformat()}" / f"city={slug}"
        out_dir.mkdir(parents=True, exist_ok=True)

        data = fetch_archive(lat, lon, str(start), str(end))
        (out_dir / "part-0000.jsonl").write_text(json.dumps(data) + "\n", encoding="utf-8")
        print(f"✅ archive → {out_dir}/part-0000.jsonl")

if __name__ == "__main__":
    main()




