import pandas as pd
import pandasql as psql
from sqlalchemy import create_engine
import uvicorn
from fastapi import FastAPI
import json
from os import environ

app = FastAPI()
DB_URL = environ.get("DB_URL")

def extract():
    # Load CSV files
    users = pd.read_csv("./data/users.csv", delimiter=",\t")
    users= users.set_index("user_id")

    user_experiments = pd.read_csv("./data/user_experiments.csv", delimiter=",\t")
    user_experiments = user_experiments.set_index("experiment_id")

    compounds = pd.read_csv("./data/compounds.csv", delimiter=",\t")
    compounds = compounds.set_index("compound_id")
    print("extract complete, csv files are loaded as dataframes")
    # Process files to derive features
    transform(users, user_experiments, compounds)
  

def transform(users, user_experiments, compounds):   

    #1. Total experiments a user ran.
    #2. Average experiments amount per user. -> not clear what amount means here assuming it means runtime
    sql_query_1 = "SELECT u.user_id, name, \
                    COUNT(experiment_id) AS total_experiments, \
                    AVG(experiment_run_time) AS avg_experiment_amount \
                    FROM users u JOIN user_experiments ue \
                    ON u.user_id = ue.user_id \
                    GROUP BY u.user_id"
    per_user_exp_count_avg_runtime = psql.sqldf(sql_query_1)

    #3. User's most commonly experimented compound.
    # split the semi-colon separated column values into separate rows
    user_experiments_split = user_experiments.assign(experiment_compound_ids = user_experiments['experiment_compound_ids'].str.split(';')).explode('experiment_compound_ids')
  
    sql_query_2 = " SELECT user_id, experiment_compound_ids, MAX(compound_use) \
                    FROM \
                    (SELECT user_id, experiment_compound_ids, \
                    COUNT (experiment_compound_ids) as compound_use \
                    FROM user_experiments_split  \
                    GROUP BY user_id,experiment_compound_ids) \
                    GROUP BY user_id"
    
    compound_use_frequency = psql.sqldf(sql_query_2)

    sql_query_3 = "SELECT u.user_id, name, compound_name \
                   FROM compound_use_frequency cf \
                   JOIN users u ON cf.user_id = u.user_id \
                   JOIN compounds c ON cf.experiment_compound_ids = c.compound_id"
    per_user_common_compound = psql.sqldf(sql_query_3)

    final_sql_query = "SELECT t1.user_id, t1.name, t1.total_experiments, t1.avg_experiment_amount, \
                       t2.compound_name AS commonly_experimented_compound \
                       FROM per_user_exp_count_avg_runtime t1 \
                            JOIN  per_user_common_compound t2 \
                            ON t1.user_id = t2.user_id"
    
    result_df = psql.sqldf(final_sql_query)
    print("transform complete, dataframes queried to generate result dataframe")
    # Upload processed data into a database
    load(result_df)


def load(processed_data):
    engine = create_engine(DB_URL)
    processed_data.to_sql("user_experiment_data", engine, if_exists="replace", index=False)
    print("load complete, result dataframe loaded into postgres DB")


@app.get("/read")
def read_stored_data():
    engine = create_engine(DB_URL)
    stored_data_df = pd.read_sql_query("SELECT * FROM user_experiment_data", engine)
    print("successful read from DB")
    
    result_json_str = stored_data_df.to_json(orient="records")
    print(json.dumps(json.loads(result_json_str), indent = 4))
    return {json.dumps(json.loads(result_json_str))}, 200
    

# API that can be called to trigger your ETL process
@app.get("/etl")
def trigger_etl():
    # Trigger ETL process
    print("beginning ETL")
    extract()
    return {"message": "Primary ETL process complete, go to http://127.0.0.1:8000/read to view the result"}, 200

# welcome API
@app.get("/")
def welcome():
    print("application start successful...")
    extract()
    return {"message": "Welcome, go to http://127.0.0.1:8000/etl to trigger the ETL process"}, 200


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")

