from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import csv

app = FastAPI()


class RequestData(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
def home():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/generate")
def generate(data: RequestData):

    project = {
        "group_addresses": [
            {
                "name": "motion_sensor",
                "address": "1/0/1"
            },
            {
                "name": "light",
                "address": "1/0/2"
            }
        ],
        "links": [
            {
                "from": "motion_sensor",
                "to": "light",
                "group_address": "1/0/1"
            }
        ]
    }

    with open("group_addresses.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Address"])

        for addr in project["group_addresses"]:
            writer.writerow([addr["name"], addr["address"]])

    return {
        "status": "ok",
        "project": project
    }


@app.get("/download")
def download():
    return FileResponse(
        "group_addresses.csv",
        filename="group_addresses.csv"
    )