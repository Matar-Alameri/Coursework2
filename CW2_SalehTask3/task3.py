import azure.functions as func
import logging
import json
import pyodbc
import datetime

app = func.FunctionApp() 

#The Serverless Azure function
@app.function_name(name="Task3_Stats")
@app.schedule(schedule="*/10 * * * * *",  # every 10 seconds
              arg_name="mytimer",
              run_on_startup=True,
              use_monitor=True)


def task3_stats(myTimer: func.TimerRequest) -> None: #runs on a timer
    logging.info(f"Task 3 triggered at {datetime.datetime.now(datetime.timezone.utc)}")

    statsData = [] #create the array to store the data

    server = 'matarsqldbserver.database.windows.net' #Matar DB info
    database = 'MyDataBase'
    username = 'dawa3isqi'
    password = 'Ma*5929525'
    driver= '{ODBC Driver 18 for SQL Server}'

    #Try to read JSON arrays from DB
    try:
        connection = pyodbc.connect( #connect to DB
            'DRIVER=' + driver +
            ';SERVER=' + server +
            ';PORT=1433;DATABASE=' + database +
            ';UID=' + username +
            ';PWD=' + password +
            ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        cursor = connection.cursor()
        logging.info("Connected to the database successfully.")
    except pyodbc.Error as e:
        logging.error("Error connecting to database: %s", e)
        return

    cursor.execute("SELECT SensorID, temperature, wind, humidity, co2 FROM SensorReadings")
    rows = cursor.fetchall()

    sensor_data = []
    for row in rows:
        sensor_data.append({
            "SensorID": row.SensorID,
            "temperature": json.loads(row.temperature),
            "wind": json.loads(row.wind),
            "humidity": json.loads(row.humidity),
            "co2": json.loads(row.co2)
        })

    for sensor in sensor_data : #iterate over every sensor
        stats = { #create a dictionary of the stats
            "SensorID": sensor["SensorID"],
            "temperature": {
                "min": min(sensor["temperature"]),
                "max": max(sensor["temperature"]),
                "avg": sum(sensor["temperature"])/len(sensor["temperature"])
            },
            "wind": {
                "min": min(sensor["wind"]),
                "max": max(sensor["wind"]),
                "avg": sum(sensor["wind"])/len(sensor["wind"])
            },
            "humidity": {
                "min": min(sensor["humidity"]),
                "max": max(sensor["humidity"]),
                "avg": sum(sensor["humidity"])/len(sensor["humidity"])
            },
            "co2": {
                "min": min(sensor["co2"]),
                "max": max(sensor["co2"]),
                "avg": sum(sensor["co2"])/len(sensor["co2"])
            }
        }
        statsData.append(stats)

    for stats in statsData:
        cursor.execute("""
            INSERT INTO Task3Stats
            (SensorID, TemperatureMin, TemperatureMax, TemperatureAvg,
            WindMin, WindMax, WindAvg,
             HumidityMin, HumidityMax, HumidityAvg,
             CO2Min, CO2Max, CO2Avg, RecordedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats["SensorID"],
            stats["temperature"]["min"], stats["temperature"]["max"], stats["temperature"]["avg"],
            stats["wind"]["min"], stats["wind"]["max"], stats["wind"]["avg"],
            stats["humidity"]["min"], stats["humidity"]["max"], stats["humidity"]["avg"],
            stats["co2"]["min"], stats["co2"]["max"], stats["co2"]["avg"],
            datetime.datetime.now(datetime.timezone.utc)
    ))

    connection.commit()
    logging.info("Task 3 stats inserted into Task3Stats table.")