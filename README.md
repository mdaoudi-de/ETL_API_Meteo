# ETL-API-Meteo 🌦️  
ETL « API → Parquet partitionné → SQLite » pour des données météo quotidiennes.

## 1. Objectif du projet

Construire un petit pipeline Data Engineering de bout en bout :

- interroger l’API **Open-Meteo** (prévisions) et l’API **ERA5** (archives)  
- normaliser les réponses JSON en tableaux propres  
- stocker les données en **Parquet partitionné** (`date`, `city`) dans un mini *data lake* local  
- alimenter une base **SQLite** pour faire quelques requêtes analytiques de démo  
- exécuter le tout via un **Makefile** ou une **CLI Python**.

Projet pensé pour servir de **portfolio Data Engineer** (structure propre, bonnes pratiques, extensible vers Docker / Airflow / GCP).

---

## 2. Architecture technique

### 2.1. Stack utilisée

- **Python** (3.11)
  - `requests` – appels API
  - `pandas` – normalisation tabulaire
  - `pyarrow` / `parquet` – écriture Parquet
  - `duckdb` – lecture globale des Parquet
  - `sqlite3` – base analytique locale
- **Format de stockage**
  - JSONL brut (ingestion)
  - CSV (staging)
  - **Parquet** partitionné (`date`, `city`)
  - SQLite (`data/warehouse/weather.sqlite`)
- **Outils**
  - `make` – orchestration simple
  - (optionnel) `pre-commit`, `black`, `flake8`

---

## 3. Arborescence du projet

```text
ETL-API-Meteo/
├── .github/workflows/ci.yml          # CI GitHub (tests / lint à compléter)
├── airflow/                          # futur DAG Airflow (optionnel)
├── apps/
│   └── streamlit_dashboard/          # futur dashboard Streamlit (optionnel)
├── config/
│   ├── cities.csv                    # ville, latitude, longitude
│   ├── config.yaml                   # config générique (optionnel)
│   └── logging.yaml                  # config logs (optionnel)
├── data/
│   ├── raw/
│   │   ├── forecast/                 # JSONL bruts (API forecast)
│   │   └── archive/                  # JSONL bruts (API archives ERA5)
│   ├── staging/
│   │   ├── forecast/                 # CSV normalisés
│   │   └── archive/
│   ├── parquet/                      # data lake local Parquet (date/city)
│   └── warehouse/
│       └── weather.sqlite            # base SQLite analytique
├── docker/                           # Dockerfile / compose (à compléter)
├── src/
│   └── etl_weather/
│       ├── ingest/
│       │   ├── open_meteo_client.py  # client API générique
│       │   ├── fetch_forecast.py     # ingestion forecast multi-villes
│       │   └── fetch_archive.py      # ingestion archives multi-villes
│       ├── transform/
│       │   ├── normalize_forecast.py # JSON → CSV (forecast)
│       │   └── normalize_archive.py  # JSON → CSV (archives)
│       ├── load/
│       │   ├── to_parquet.py         # CSV → Parquet partitionné
│       │   └── to_sqlite.py          # Parquet → SQLite + requêtes de démo
│       └── cli.py                    # pipeline complet en 1 commande
├── tests/                            # tests unitaires (à compléter)
├── Makefile                          # commandes make (pull / transform / load / all)
├── pyproject.toml                    # config projet / pytest
├── requirements.txt                  # dépendances Python
└── README.md  
```

---

## 4. Données manipulées

### 4.1 Sources de données

- API Open-Meteo Forecast : https://api.open-meteo.com/v1/forecast  
- API Open-Meteo ERA5 Archive : https://archive-api.open-meteo.com/v1/era5  
- Coordonnées des villes dans `config/cities.csv`

### 4.2 Variables météo utilisées

Le pipeline utilise principalement les champs suivants :

- temperature_2m_max : température maximale quotidienne
- temperature_2m_min : température minimale quotidienne
- precipitation_sum : cumul des précipitations
- time : date du jour
- city : nom de la ville
- source : "forecast" ou "archive"

### 4.3 Format des données

- Étape ingestion : JSONL bruts
- Étape staging : CSV normalisés
- Étape data lake : Parquet partitionné
- Étape analyse : SQLite

---

## 5. Data Lake local (Parquet)

Les données normalisées sont stockées en Parquet avec un partitionnement :

```text
data/parquet/
└── date=YYYY-MM-DD/
└── city=nom-ville/
└── part-0000.parquet
```


Chaque fichier contient :

- date : string
- city : string
- temperature_2m_max : float
- temperature_2m_min : float
- precipitation_sum : float
- source : forecast ou archive

Le format Parquet permet :

- compression importante
- lecture rapide colonne par colonne
- compatibilité directe avec Spark, DuckDB, BigQuery, etc.
- filtrage efficace par partitions (date, ville)

---

## 6. Installation

### 6.1 Clonage du dépôt

git clone <URL_DU_REPO>
cd ETL-API-Meteo


### 6.2 Création de l'environnement

python -m venv .venv


Activation :

- Windows :
.venv\Scripts\activate


- Linux / macOS :
source .venv/bin/activate


### 6.3 Installation des dépendances
pip install -r requirements.txt

Ou :
make install


---

## 7. Exécution du pipeline

Le pipeline suit les étapes suivantes :

1. ingestion (API → JSONL)
2. transformation (JSONL → CSV)
3. chargement Parquet
4. chargement SQLite

### 7.1 Exécution via Makefile

make pull
make transform
make load
make sqlite
make etl
make all

### 7.2 Exécution via la CLI Python

python -m src.etl_weather.cli

Pour charger dans SQLite :
python -m etl_weather.load.to_sqlite

## 8. Entrepôt SQLite

La base SQLite est enregistrée ici :
data/warehouse/weather.sqlite

Elle contient une table :
weather(date, city, temperature_2m_max, temperature_2m_min, precipitation_sum)

Exemples de requêtes exécutées automatiquement :

### 1) Top 5 des jours les plus chauds

SELECT date, city, temperature_2m_max
FROM weather
ORDER BY temperature_2m_max DESC
LIMIT 5;

### 2) Moyenne pluie par ville

SELECT city, AVG(precipitation_sum)
FROM weather
GROUP BY city
ORDER BY AVG(precipitation_sum) DESC;

### 3) Température max moyenne par ville

SELECT city, AVG(temperature_2m_max)
FROM weather
GROUP BY city
ORDER BY AVG(temperature_2m_max) DESC;


---

## 9. Qualité et tests (à compléter)

### 9.1 Pré-commit (optionnel)

pip install pre-commit
pre-commit install
pre-commit run --all-files


### 9.2 Tests unitaires possibles

- test client API
- test normalisation
- test écriture Parquet
- test partitions date/city

### 9.3 CI GitHub (optionnel)

Le fichier `.github/workflows/ci.yml` peut effectuer :

- installation Python
- pytest
- black --check
- flake8

---

## 10. Extensions possibles

- Dockerisation du pipeline
- Mini DAG Airflow
- Export du data lake sur Google Cloud Storage
- Table externe BigQuery sur le bucket GCS
- Dashboard Streamlit
- Validation des données (Pandera / Great Expectations)

---

## 11. Résumé

Ce projet implémente un pipeline complet :

API → JSONL → CSV → Parquet partitionné → SQLite.

Il suit une architecture professionnelle et extensible.
