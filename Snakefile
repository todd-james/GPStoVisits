# Snakefile
# BW GPS Data Visit Detection 
# From Raw Data To Cleaned Visit Locations 
# James Todd - May '23

import glob
import os

# Environment Variables 
envvars: 
    "rawdata_path",
    "cleandata_path",
    "pg_host",
    "pg_port",
    "pg_user"

# Params 
dists = ['200']
times = ['300']
dates_uudis = [f"{x.split('/')[4]}_{x.split('/')[5].replace('.csv', '')}" for x in glob.glob(f"{os.environ['rawdata_path']}/*/*.csv")]

# Rules
rule all: 
    input: 
        "db_done.txt"

rule clean_raw: 
    input: 
        "clean_input.py",
        f"{os.environ['rawdata_path']}/{{date}}/{{uuid}}.csv"
    output: 
        temporary(f"{os.environ['cleandata_path']}/InputData_Clean/{{date}}_{{uuid}}.csv")
    shell: 
        "python {input} {output}"

rule run_lachesis: 
    input: 
        f"{os.environ['cleandata_path']}/InputData_Clean/{{date}}_{{uuid}}.csv",
    output: 
        temporary(f"{os.environ['cleandata_path']}/OutputData_Visits/{{date}}_{{uuid}}_d{{dist}}_t{{time}}.csv")
    shell: 
        "cat {input} | lachesis -d {wildcards.dist} -t {wildcards.time} -f '%Y-%m-%d %H:%M:%S' > {output}"

rule clean_visits:
    input: 
        "clean_visits.py",
        f"{os.environ['cleandata_path']}/OutputData_Visits/{{date}}_{{uuid}}_d{{dist}}_t{{time}}.csv"
    output: 
        f"{os.environ['cleandata_path']}/OutputData_Visits_Clean/{{date}}_{{uuid}}_d{{dist}}_t{{time}}.csv",
        temporary(f"{os.environ['cleandata_path']}/Dashboard_HUM/{{date}}_{{uuid}}_d{{dist}}_t{{time}}.csv")
    shell: 
        "python {input} {output}"
    
rule vists2db: 
    input: 
        f"{os.environ['cleandata_path']}/Dashboard_HUM/{{date}}_{{uuid}}_d{{dist}}_t{{time}}.csv"
    output: 
        temporary(f"{os.environ['cleandata_path']}/Dashboard_HUM/{{date}}_{{uuid}}_d{{dist}}_t{{time}}.txt")
    params:
        host=os.environ['pg_host'],
        port=os.environ['pg_port'],
        user=os.environ['pg_user']
    shell: 
        "cat {input} | psql -h {params.host} -p {params.port} -U {params.user} -c \"COPY mesh6_visits FROM stdin with CSV;\" && touch {output}"

rule db_done: 
    input: 
        expand(f"{os.environ['cleandata_path']}/Dashboard_HUM/{{date_uuid}}_d{{dist}}_t{{time}}.txt", date_uuid = dates_uudis, dist = dists, time = times) 
    output: 
        "db_done.txt"
    shell: 
        "touch {output}"