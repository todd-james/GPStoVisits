# GPStoVisits
This is the pipeline process that will take raw GPS data, clean them, input into the Lachesis visit detection and push data to a DB

# Requirements 
- [Lachesis Visit Detection](https://github.com/hamishgibbs/lachesis) algorithm 
- Environment Variables: 
	- Raw data filepath (rawdata_path)
	- Clean data filepath (cleandata_path)
	- Postgres host (pg_host)
	- Postgres port (pg_port)
	- Postgres user (pg_user)

This should be set up in a local .env file, that may look something like this:
```
rawdata_path="<PATH>"
cleandata_path="<PATH>"
pg_host="<HOST>"
pg_port="<PORT>"
pg_user="<USER>"
```  
and can be initialised by running `export $(cat .env | xargs)`

# Execution

To execute this pipline, run `snakemake -j<No. cores>`

## General Summary 
The Snakefile goes through a series of processes, which are as follows: 
1. Clean the raw GPS data in using the script [clean_input.py](clean_input.py) in rule clean_raw
2. Run the [Lachesis](https://github.com/hamishgibbs/lachesis) visit detection rust API
3. Clean the visit locations using the script [clean_visits.py](clean_visits.py) in rule clean_visits
4. Push vists to database 

This pipeline was created to implement a rigorous data ingestion workflow for a dashboard application which is currently in development. The Dashboard will show population distribution acorss the Kyoto area in Japan using these visit locations. 
