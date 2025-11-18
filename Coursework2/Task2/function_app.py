import azure.functions as func
import logging
import json
import pyodbc

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

#The Serverless Azure function
@app.route(route="Task2")
def task2_statssou(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Task 2 Generating Statistics')

    statsData = [] #create the array to store the data

    #Try to read JSON from request
    try: 
        sensor_data = req.get_json()
    except Exception as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )

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

    return func.HttpResponse( #return the results
        json.dumps(statsData, indent=4),
        mimetype="application/json",
        status_code=200
    )