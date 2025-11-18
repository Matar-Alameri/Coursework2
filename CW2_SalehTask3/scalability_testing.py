import requests
import time
import matplotlib.pyplot as plt
import random

url = "http://localhost:7071/api/Task2"

requestScalingTestData = [{
    "SensorID": [1],
    "temperature": [12],
    "wind" : [14],
    "humidity": [42],
    "co2": [569]
}]

responseTimesLoad = []
#for i in range(1,21):
    #NumRequests = i*10
    #start = time.time()
    #for j in range(NumRequests):
    #    r = requests.post(url, json=requestScalingTestData)
    #end = time.time()
    #responseTimesLoad.append(end-start)
    #time.sleep(2)


responseTimesSize = []
for i in range(1,21):
    sizeScalingTestData = []
    for j in range(0,i*10):
        sizeScalingTestData.append({
        "SensorID":j,
        "temperature": [random.randint(5,18) for j in range(10)],
        "wind": [random.randint(12,24) for j in range(10)],
        "humidity": [random.randint(30,60) for j in range(10)],
        "co2": [random.randint(400,1600) for j in range(10)]
        })
    start = time.time()
    r = requests.post(url, json=sizeScalingTestData)
    end = time.time()
    print(r.text)
    responseTimesSize.append(end-start)
    time.sleep(0.1)

XLabels = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
#conveniently they are the same

#plt.figure(figsize=(12,5))

#first subplot:
#plt.subplot(1,2,1)
#plt.plot(XLabels, responseTimesLoad, marker = 'o')
#plt.xlabel("Number of Requests")
#plt.ylabel("Response time (s)")
#plt.title("Scaling the number of web requests")

#plt.subplot(1,2,1)
plt.plot(XLabels, responseTimesSize, marker = 'o')
plt.xlabel("Number of sensors in data set")
plt.ylabel("Response time (s)")
plt.title("Scaling the number of sensors")

plt.tight_layout()
plt.savefig("scalability_plots.png")