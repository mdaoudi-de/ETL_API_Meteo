install:
	pip install -r requirements.txt

pull:
	python -m src.etl_weather.ingest.fetch_forecast
	python -m src.etl_weather.ingest.fetch_archive

transform:
	python -m src.etl_weather.transform.normalize_forecast
	python -m src.etl_weather.transform.normalize_archive

load:
	python -m src.etl_weather.load.to_parquet

sqlite:
	python -m src.etl_weather.load.to_sqlite

etl: pull transform load 

all: install pull transform load sqlite
