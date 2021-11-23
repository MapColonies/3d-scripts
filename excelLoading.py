# python ./excelLoading.py
from os import wait
import pandas
import json
import requests
from datetime import datetime
import time
import json


EXCEL = './models.xlsx'
URL = 'http://localhost:8082/models'
URL_Model_Ingestion_Service = 'http://ingestion-3d-model-ingestion-service-3d-dev.apps.v0h0bdx6.eastus.aroapp.io/models'
URL_JobService = 'https://job-manager-dev-job-manager-route-raster-dev.apps.v0h0bdx6.eastus.aroapp.io/jobs'
HEADERS = {'Content-Type': 'application/json'}

CSV = './models_update.csv'

#excel_data = pandas.read_excel(EXCEL)
excel_data = pandas.read_csv(CSV)
excel_json = excel_data.to_json(orient='records')
excel_array = json.loads(excel_json)
num_of_models = 0
index = 1
list_fails = []
in_progress = "In-Progress"
failed = "Failed"
completed = "Completed"
list_nulls = []


def classification(x):
    if x == "a":
        return 1
    if x == "b":
        return 2


for row in excel_array:

    model = {}
    model["modelPath"] = row["modelPath"]
    model["tilesetFilename"] = row["tilesetFilename"]
    row.pop("modelPath")
    row.pop("tilesetFilename")
    for p in row:
        if row[p]:
            if row[p] == '-':
                list_nulls.insert(0, p)
        else:
            list_nulls.insert(0, p)
    try:
        row["footprint"] = json.loads(row["footprint"])
    except:
        row["footprint"] = row["footprint"]
    for l in list_nulls:
        row.pop(l)

    row["classification"] = str(row["classification"])

    model["metadata"] = row

    response_Model_Ingestion = requests.post(
        url=URL_Model_Ingestion_Service, json=model, headers=HEADERS)

    if response_Model_Ingestion.status_code > 201:
        model["message"] = response_Model_Ingestion.json()["message"]
        list_fails.append([str(index), model["message"]])
    else:
        model["message"] = "Problem with Nifi. Maybe wrong model path?"

        url_with_jobId = URL_JobService + "/" + \
            response_Model_Ingestion.json()["jobId"]
        response_Job = requests.get(url=url_with_jobId)
        while response_Job.json()["status"] == in_progress:
            time.sleep(5)
            response_Job = requests.get(url=url_with_jobId)
        if response_Job.json()["status"] == failed:
            list_fails.append([str(index), model["message"]])

    num_of_models = num_of_models + 1
    index = index + 1
    break

# Report part
print("Finished!\nNumbers of models: " + str(num_of_models) +
      "\nCompleted models: " + str(num_of_models - len(list_fails)) + "/" + str(num_of_models) +
      "\nFailed models: " + str(len(list_fails)) + "/" + str(num_of_models) + "\nThe Failed Models:")
for item in list_fails:
    print(item[0] + "Error: " + item[1])
