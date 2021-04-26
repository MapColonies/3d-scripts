#python ./excelLoading.py
import pandas
import json
import requests
from datetime import datetime

EXCEL = '/tmp/3dtiles/models.xlsx'
URL = 'http://localhost:8082/models'
HEADERS = { 'Content-Type': 'application/json' }

excel_data = pandas.read_excel(EXCEL)

excel_json = excel_data.to_json(orient='records')

excel_array = json.loads(excel_json)

for row in excel_array:
  model = {}
  model["modelPath"] = row["modelPath"]
  row.pop("modelPath")
  model["metadata"] = row
  print(model["metadata"])
  model["metadata"]["links"] = json.loads(model["metadata"]["links"])
  response = requests.post(url = URL, json = model, headers = HEADERS)
  print(row["identifier"] + " -> " + str(response.status_code))
  if response.status_code > 201:
    print(response.json()["message"])
  print("\n")
