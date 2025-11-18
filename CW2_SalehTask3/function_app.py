import azure.functions as func
import logging
import pyodbc
import datetime
import sys
import json

app = func.FunctionApp() 

@app.function_name(name="Task3_Stats")
@app.sql_trigger(
              arg_name="changes",
              table_name = "dbo.Sensor_Data",
              connection_string_setting = "SqlConnectionString")
def task3_stats(changes: str) -> None:
    logging.info(f"Task 3 triggered at {datetime.datetime.now(datetime.timezone.utc)}")

    try:
        change_list = json.loads(changes)
        logging.info(f"{len(change_list)} change(s) detected in Sensor_Data.")
    except Exception as e:
        logging.error(f"Failed to parse SQL trigger changes: {e}")
        return

    server = 'matarsqldbserver.database.windows.net'
    database = 'MyDataBase'
    username = 'dawa3isqi'
    password = 'Ma*5929525'
    driver= '{ODBC Driver 18 for SQL Server}'

    # Connect to DB
    try:
        connection = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        )
        cursor = connection.cursor()
        logging.info("Connected to the database successfully.")
    except pyodbc.Error as e:
        logging.error("Error connecting to database: %s", e)
        return

    # Fetch all sensor readings
    try:
        cursor.execute("SELECT SensorID, Temperature, Wind_speed, Relative_humidity, CO2 FROM Sensor_Data")
        rows = cursor.fetchall()
        logging.info(f"Fetched {len(rows)} rows from Sensor_Data.")
    except pyodbc.Error as e:
        logging.error("Error fetching data: %s", e)
        return

    # Aggregate readings per sensor
    sensor_data = {}
    for row in rows:
        sid = row.SensorID
        if sid not in sensor_data:
            sensor_data[sid] = {
                "temperature": [],
                "wind": [],
                "humidity": [],
                "co2": []
            }
        sensor_data[sid]["temperature"].append(row.Temperature)
        sensor_data[sid]["wind"].append(row.Wind_speed)
        sensor_data[sid]["humidity"].append(row.Relative_humidity)
        sensor_data[sid]["co2"].append(row.CO2)

    # Compute stats per sensor
    stats_data = []
    for sid, readings in sensor_data.items():
        stats = {
            "SensorID": sid,
            "temperature": {
                "min": min(readings["temperature"]),
                "max": max(readings["temperature"]),
                "avg": round(sum(readings["temperature"]) / len(readings["temperature"]), 2)
            },
            "wind": {
                "min": min(readings["wind"]),
                "max": max(readings["wind"]),
                "avg": round(sum(readings["wind"]) / len(readings["wind"]), 2)
            },
            "humidity": {
                "min": min(readings["humidity"]),
                "max": max(readings["humidity"]),
                "avg": round(sum(readings["humidity"]) / len(readings["humidity"]), 2)
            },
            "co2": {
                "min": min(readings["co2"]),
                "max": max(readings["co2"]),
                "avg": round(sum(readings["co2"]) / len(readings["co2"]), 2)
            }
        }
        stats_data.append(stats)

    # Insert stats into Task3Stats table
    total = len(stats_data)
    for idx, stats in enumerate(stats_data, start=1):
        try:
            cursor.execute("""
                MERGE INTO Task3Stats AS target
                USING (SELECT ? AS SensorID, ? AS TempMin, ? AS TempMax, ? AS TempAvg,
                            ? AS WindMin, ? AS WindMax, ? AS WindAvg,
                            ? AS HumMin, ? AS HumMax, ? AS HumAvg,
                            ? AS CO2Min, ? AS CO2Max, ? AS CO2Avg) AS source
                ON target.SensorID = source.SensorID
                WHEN MATCHED THEN
                    UPDATE SET
                        TemperatureMin = source.TempMin,
                        TemperatureMax = source.TempMax,
                        TemperatureAvg = source.TempAvg,
                        WindMin = source.WindMin,
                        WindMax = source.WindMax,
                        WindAvg = source.WindAvg,
                        HumidityMin = source.HumMin,
                        HumidityMax = source.HumMax,
                        HumidityAvg = source.HumAvg,
                        CO2Min = source.CO2Min,
                        CO2Max = source.CO2Max,
                        CO2Avg = source.CO2Avg
                WHEN NOT MATCHED THEN
                    INSERT (SensorID, TemperatureMin, TemperatureMax, TemperatureAvg,
                            WindMin, WindMax, WindAvg,
                            HumidityMin, HumidityMax, HumidityAvg,
                            CO2Min, CO2Max, CO2Avg)
                    VALUES (source.SensorID, source.TempMin, source.TempMax, source.TempAvg,
                            source.WindMin, source.WindMax, source.WindAvg,
                            source.HumMin, source.HumMax, source.HumAvg,
                            source.CO2Min, source.CO2Max, source.CO2Avg);
            """, (
                stats["SensorID"],
                stats["temperature"]["min"], stats["temperature"]["max"], stats["temperature"]["avg"],
                stats["wind"]["min"], stats["wind"]["max"], stats["wind"]["avg"],
                stats["humidity"]["min"], stats["humidity"]["max"], stats["humidity"]["avg"],
                stats["co2"]["min"], stats["co2"]["max"], stats["co2"]["avg"]
            ))
            connection.commit()
            print(f"\rProcessed {idx}/{total} sensor stats", end="")
            sys.stdout.flush()
        except pyodbc.Error as e:
            logging.error("Error processing stats for SensorID %s: %s", stats["SensorID"], e)

    logging.info("\nTask 3 stats insertion complete.")