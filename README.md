# ETL Pipeline with Python, FastAPI, PostgreSQL and Docker

### About
Code when run reads csv files from `/data` folder, derives features from the data and writes them to a PostgreSQL DB.

Data stored in DB can be read using the provided API


### Steps to run
1. Clone the repo.
2. Run the bash script with cmd `sh run.sh`, this will build and create docker containers for postgresql and the python application, it will also start the application; verify using API [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
3. ETL process can be triggered by accessing API [`http://127.0.0.1:8000/etl`](http://127.0.0.1:8000/)
4. Loaded results in the DB can be viewed with API [`http://127.0.0.1:8000/read`](http://127.0.0.1:8000/read)