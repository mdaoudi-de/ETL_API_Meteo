from pathlib import Path
from datetime import date
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import shutil

STAGING = Path("data/staging")
OUT = Path("data/parket")

OUT.mkdir(parents=True, exist_ok=True)

def _read_today(kind : str) -> pd.DataFrame:
    """Lit les données normalisées du jour depuis le répertoire de staging.
    param kind: Le type de données à lire ('forecast' ou 'archive')."""
    root = STAGING / kind / f"date={date.today().isoformat()}"
    if not root.exists():
        return pd.DataFrame
    dfs = []
    for city_dir in sorted(root.glob("city=*")):
        src = city_dir / "part-0000.csv"
    if src.exists():
        df = pd.read_csv(src)
        df["city"] = city_dir.name.split("=",1)[1]
        df["source"] = kind
        dfs.append(df)
    return pd.concat(dfs,ignore_index=True) if dfs else pd.DataFrame()

def _cleanup_partitions(df: pd.DataFrame) -> None:
    """Supprime les partitions date=.../ city=... avant d'écrire.
     param df: Le DataFrame contenant les données à écrire."""
    if df.empty:
        return
    dates = df["time"].astype(str).unique().tolist()
    cities = df["city"].astype(str).unique().tolist()
    # 
    for d in dates:
        print(d)
        for c in cities:
            print(c)
            part_dir = OUT / f"date={d}" / f"city={c}"
            if part_dir.exists():
                shutil.rmtree(part_dir)

def main():
    #test _cleanup_partitions
    _cleanup_partitions(pd.DataFrame({
        "time": ["2024-06-01","2024-06-01","2024-06-02"],
        "city": ["city1","city2","city1"]
    }))


if __name__ == "__main__":
    main()