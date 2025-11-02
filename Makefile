install:
	pip install -r requirements.txt

pull:
	python -m etl_weather.ingest.fetch_forecast
	python -m etl_weather.ingest.fetch_archive

transform:
	python -m etl_weather.transform.normalize_forecast
	python -m etl_weather.transform.normalize_archive

load:
	python -m etl_weather.load.to_parquet

all: pull transform load
