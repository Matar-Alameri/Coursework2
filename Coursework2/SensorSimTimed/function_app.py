# ------------------------------------------------------------
# REFERENCES / SOURCES USED
#
# 1. Timer trigger pattern based on Microsoft Azure documentation:
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2,isolated-process,nodejs-v4&pivots=programming-language-python

# 2. Video reference (general overview, not directly used):
# https://www.youtube.com/watch?v=OXnfKYwnoVk&t=701s
# ------------------------------------------------------------
import azure.functions as func
import datetime
import json
import logging
import random as rnd
import pandas as pd
import pyodbc 
app = func.FunctionApp()
Sensor_ids = range(1, 21)
def Sensor_info(i):
    return {
        'Sensor ID' : int(i),
        'Temperature' : float(rnd.randint(5,18)),
        'Wind speed' : float(rnd.randint(12,24)),
        'Relative Humidity' : float(rnd.randint(30, 60)),
        'CO2' : float(rnd.randint(400, 1600))
    }
# Generating random sensor data

app = func.FunctionApp()

@app.function_name(name="mytimer")
@app.timer_trigger(schedule="*/10 * * * * *", 
              arg_name="mytimer",
              run_on_startup=False) 


def test_function(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
     # Creating a DataFrame from the generated sensor data
    info = (Sensor_info(i) for i in Sensor_ids )
    df = pd.DataFrame(info)
    # connecting to sql DB
    server = 'matarsqldbserver.database.windows.net'
    database = 'MyDataBase'
    username = 'dawa3isqi'
    password = 'Ma*5929525'
    driver= '{ODBC Driver 18 for SQL Server}'
    try:
            connection = pyodbc.connect(
                'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password +
                ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            )
            print("Connected to the database successfully.")
    except pyodbc.Error as e:
            print("Error connecting to database: ", e)
    #inserting data into table
    try:
            cursor = connection.cursor()
            for index, row in df.iterrows():
                cursor.execute("INSERT INTO Sensor_Data (SensorID,Temperature,Wind_speed,Relative_Humidity,CO2) values(?,?,?,?,?)", int(row['Sensor ID']), float(row['Temperature']), float(row['Wind speed']), float(row['Relative Humidity']), float(row['CO2']))
            connection.commit()
            cursor.close()
            print("Data inserted successfully.")
    except pyodbc.Error as e:
            print("Error inserting data into database: ", e)
            
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp) 