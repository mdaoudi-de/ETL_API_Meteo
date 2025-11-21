"""
CLI d'orchestration du pipeline météo.

Une seule commande pour tout lancer :
    python -m src.etl_weather.cli
"""

from src.etl_weather.ingest import fetch_forecast, fetch_archive
from src.etl_weather.transform import normalize_forecast, normalize_archive
from src.etl_weather.load import to_parquet


def main() -> None:
    print("🚀 Début du pipeline ETL météo\n")

    # 1) Ingestion
    print("📥 Étape 1/3 : Ingestion (forecast + archive)...")
    fetch_forecast.main()
    fetch_archive.main()
    print("✅ Ingestion terminée.\n")

    # 2) Transformation
    print("🧪 Étape 2/3 : Normalisation (CSV staging)...")
    normalize_forecast.main()
    normalize_archive.main()
    print("✅ Normalisation terminée.\n")

    # 3) Load Parquet
    print("📦 Étape 3/3 : Chargement Parquet partitionné...")
    to_parquet.main()
    print("\n🎉 Pipeline terminé avec succès.")


if __name__ == "__main__":
    main()