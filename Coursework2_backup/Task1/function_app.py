# ------------------------------------------------------------
# REFERENCES / SOURCES USED
#
# 1. Azure Function structure and SQL integration guidance:
#    https://youtu.be/7tEx8C6iW2I?si=vTRCE39PX-28EHID
#
# 2. General reference for inserting Python data into SQL Server
#    using pyodbc:
#    https://learn.microsoft.com/en-us/sql/machine-learning/data-exploration/python-dataframe-sql-server?view=sql-server-ver17
#
# Note:
# The DataFrame in this coursework is inserted row-by-row using
# a pyodbc cursor. Both sources were adapted and extended to meet
# the specific requirements of the sensor simulation, pandas
# processing, Azure Function logic, and JMeter scalability testing.
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
# Generating random sensor data
def Sensor_info(i):
    return {
        'Sensor ID' : int(i),
        'Temperature' : float(rnd.randint(5,18)),
        'Wind speed' : float(rnd.randint(12,24)),
        'Relative Humidity' : float(rnd.randint(30, 60)),
        'CO2' : float(rnd.randint(400, 1600))
    }


@app.route(route="SimFunction", auth_level=func.AuthLevel.ANONYMOUS)
def SimFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
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
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
                return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )