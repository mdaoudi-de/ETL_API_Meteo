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
        return pd.DataFrame()
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
    dates = df["date"].astype(str).unique().tolist()
    cities = df["city"].astype(str).unique().tolist()
    # Supprimer les partitions existantes
    for d in dates:
        for c in cities:
            part_dir = OUT / f"date={d}" / f"city={c}"
            if part_dir.exists():
                shutil.rmtree(part_dir)

def main():
    # Lire staging du jour et archiver
    df_forecast = _read_today("forecast")
    df_archive = _read_today("archive")

    # Contact + priorité à l'archive' sur les  doublons (même date/ville)
    df = pd.concat([df_archive,df_forecast],ignore_index=True)
    if df.empty:
        raise SystemExit("Aucune donnée à traiter aujourd'hui.")
    df.drop_duplicates(subset=["time","city"],keep="first",inplace=True)

    # Normaliser les colonnes
    expected = {"time","temperature_2m_max","temperature_2m_min","precipitation_sum","city"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans les données : {missing}")
    df["time"] = pd.to_datetime(df["time"]).dt.date.astype(str)
    df = df.astype({
        "temperature_2m_max": "float64",    
        "temperature_2m_min": "float64",
        "precipitation_sum": "float64",
        "city": "string",
    }, errors="ignore")

    # Partition (Hive style)
    df = df.rename(columns={"time": "date"})
    _cleanup_partitions(df)

    # Ecriture en Parquet partitionné
    table = pa.Table.from_pandas(df)
    pq.write_to_dataset(
        table,
        root_path=str(OUT),
        partition_cols=["date","city"],
        use_dictionary=True,
        compression="snappy",
    )
    print(f"Données écrites dans {OUT} au format Parquet partitionné.")

if __name__ == "__main__":
    main()