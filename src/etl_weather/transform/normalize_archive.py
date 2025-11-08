# Normalisation des archives météorologiques

from pathlib import Path
import json
import pandas as pd
from datetime import date

RAW_ROOT = Path("data/raw/archive")
STAGING_ROOT = Path("data/staging/archive")
STAGING_ROOT.mkdir(parents=True, exist_ok=True)

def main():
    """Normalise les fichiers des archives météorologiques quotidiens en CSV."""
    today_dir = RAW_ROOT / f"date={date.today().isoformat()}"
    if not today_dir.exists():
        raise FileNotFoundError(f"Le répertoire {today_dir} n'existe pas.")
    
    for city_dir in sorted(today_dir.glob("city=*")):
        out_dir = STAGING_ROOT / today_dir.name / city_dir.name
        out_dir.mkdir(parents=True,exist_ok=True)

        
        src = city_dir / "part-0000.jsonl"

        # Vérification de l'existence du fichier source
        if not src.exists():
            print(f"Fichier Manquant : {src}")
            continue

        obj = json.loads(src.read_text(encoding="utf-8"))
        daily = obj.get("daily", {})

        # Vérification de la présence des données 'daily'
        if not daily:
            print(f"Pas de 'daily' dans {src}")
            continue

        
        df = pd.DataFrame(daily)
        df["city"] = city_dir.name.split("=",1)[0]
        df["longitude"] = obj.get("longitude")
        df["latitude"] = obj.get("latitude")
        df["altitude"] = obj.get("elevation")

        # Écriture des données normalisées au format CSV
        (out_dir/"part-0000.csv").write_text(df.to_csv(index=False),encoding="utf-8")
        print(f"normalize archive -> {out_dir}/part-0000.csv")


if __name__ == "__main__":
    main()
