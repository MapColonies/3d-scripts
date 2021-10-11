# python ./excelLoading.py
from os import wait
import pandas
import json
import requests
from datetime import datetime
import time

EXCEL = './models.xlsx'
URL = 'http://localhost:8082/models'
URL_Model_Ingestion_Service = 'http://ingestion-stack-3d-model-ingestion-service-route-3d.apps.v0h0bdx6.eastus.aroapp.io/models'
URL_JobService = 'http://ingestion-stack-discrete-ingestion-db-route-3d.apps.v0h0bdx6.eastus.aroapp.io/jobs'
HEADERS = {'Content-Type': 'application/json'}

CSV = './models.csv'

#excel_data = pandas.read_excel(EXCEL)
excel_data = pandas.read_csv(CSV)
excel_json = excel_data.to_json(orient='records')
excel_array = json.loads(excel_json)
num_of_models = 0
list_fails = []
in_progress = "In-Progress"
failed = "Failed"
completed = "Completed"

for row in excel_array:
    # if row["modelPath"] == "":
    #     break
    model = {}
    model["modelPath"] = row["modelPath"]
    model["tilesetFilename"] = row["tilesetFilename"]
    row.pop("modelPath")
    row.pop("tilesetFilename")
    model["metadata"] = row
    # print(model["metadata"])
    response_Model_Ingestion = requests.post(
        url=URL_Model_Ingestion_Service, json=model, headers=HEADERS)
    print(row["identifier"] + " -> " +
          str(response_Model_Ingestion.status_code))
    if response_Model_Ingestion.status_code > 201:
        print(response_Model_Ingestion.json()["message"] + "\n")
        model["message"] = response_Model_Ingestion.json()["message"]
    else:
        model["message"] = "Problem with Nifi. Maybe wrong model path?"
        url_with_jobId = URL_JobService + "/" + \
            response_Model_Ingestion.json()["jobId"]
        response_Job = requests.get(url=url_with_jobId)
        while response_Job.json()["status"] == in_progress:
            time.sleep(5)
            # print("Sleeped")
            response_Job = requests.get(url=url_with_jobId)
        print(url_with_jobId)
        print("\n")
    if response_Job.json()["status"] == failed:
        list_fails.append([row["identifier"], model["message"]])
    num_of_models = num_of_models + 1

# Report part
print("Finished!\nNumbers of models: " + str(num_of_models) +
      "\nCompleted models: " + str(num_of_models - len(list_fails)) + "/" + str(num_of_models) +
      "\nFailed models: " + str(len(list_fails)) + "/" + str(num_of_models) + "\nThe Failed Models:")
for item in list_fails:
    print(item[0] + "Error: " + item[1])
