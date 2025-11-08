# Normalisation des prévisions météorologiques

from pathlib import Path
import json
import pandas as pd
from datetime import date


RAW_ROOT = Path("data/raw/forecast")
STAGING_ROOT = Path("data/staging/forecast")
STAGING_ROOT.mkdir(parents=True, exist_ok=True)


def main():
    today_dir = RAW_ROOT / f"date={date.today().isoformat()}"
    if not today_dir.exists():
        raise FileNotFoundError(f"Le répertoire {today_dir} n'existe pas.")
    
    for i in sorted(today_dir.glob("city=*")):
        out_dir = STAGING_ROOT / today_dir.name / i.name
        out_dir.mkdir(parents=True,exist_ok=True)

        src = i / "part-0000.jsonl"

        if not src.exists():
            print(f"Fichier Manquant : {src}")
            continue

        obj = json.loads(src.read_text(encoding="utf-8"))
        daily = obj.get("daily", {})

        if not daily:
            print(f"Pas de 'daily' dans {src}")
            continue

        df = pd.DataFrame(daily)
        df["ville"] = i.name.split("=",1)[1]
        df["longitude"] = obj.get("longitude")
        df["latitude"] = obj.get("latitude")
        df["altitude"] = obj.get("elevation")


        df["date"] = df["time"]
        df_f = df[["ville","latitude","longitude","date","temperature_2m_max","temperature_2m_min","precipitation_sum"]]
        print(df_f)
        break




if __name__ == "__main__":
    main()

