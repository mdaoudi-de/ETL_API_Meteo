from pathlib import Path
import sqlite3
import pandas as pd
import duckdb

PARQUET_ROOT = Path("data/parquet")
DB_PATH = Path("data/warehouse/weather.sqlite")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_parquet_into_sqlite():
    """Charge tous le data lakes Parquet dans une base de données SQLite."""

    # Connexion DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creer les tables si elles n'existent pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather (
            date TEXT,
            city TEXT,
            temperature_2m_max REAL,
            temperature_2m_min REAL,
            precipitation_sum REAL
        );
    """)

    # Nettoyage avant rechargement
    cursor.execute("DELETE FROM weather;")

    # Charger les fichiers Parquet avec DuckDB
    df = duckdb.query(f"""
        SELECT
            date,
            city,
            temperature_2m_max,
            temperature_2m_min,
            precipitation_sum
        FROM parquet_scan('{PARQUET_ROOT}/**/*.parquet')
    """).to_df()

    # Insérer les données dans SQLite
    df.to_sql('weather', conn, if_exists='append', index=False)

    # Commit et fermer la connexion
    conn.commit()
    conn.close()

    print(f"✅ SQLite mis à jour dans -> {DB_PATH}")

def demo_queries():
    """Quelques requêtes d'exemple utiles pour ton README."""

    conn = sqlite3.connect(DB_PATH)

    print("\n 1️⃣ Top 5 jours les plus chauds")
    q1 = conn.execute("""
        SELECT date, city, temperature_2m_max
        FROM weather
        ORDER BY temperature_2m_max DESC
        LIMIT 5;
    """).fetchall()
    print(q1)

    print("\n 2️⃣ Moyenne de la pluie par ville")
    q2 = conn.execute("""
        SELECT city, AVG(precipitation_sum)
        FROM weather
        GROUP BY city
        ORDER BY AVG(precipitation_sum) DESC;
    """).fetchall()
    print(q2)

    print("\n 3️⃣ Température max moyenne sur 7 jours par ville")
    q3 = conn.execute("""
        SELECT city, AVG(temperature_2m_max)
        FROM weather
        GROUP BY city
        ORDER BY AVG(temperature_2m_max) DESC;
    """).fetchall()
    print(q3)

    conn.close()

def main():
    load_parquet_into_sqlite()
    demo_queries() 

if __name__ == "__main__":
    main()

