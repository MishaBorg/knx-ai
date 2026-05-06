from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from openai import OpenAI

import csv
import json
import os

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class RequestData(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
def home():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/generate")
def generate(data: RequestData):

    user_text = data.text

    prompt = f"""
Analyze this KNX / ETS smart home scenario.

Generate KNX group addresses and logical device links.

Return ONLY valid JSON.

Required JSON format:

{{
  "group_addresses": [
    {{
      "name": "example",
      "address": "1/0/1"
    }}
  ],
  "links": [
    {{
      "from": "device1",
      "to": "device2",
      "group_address": "1/0/1"
    }}
  ]
}}

Scenario:
{user_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
You are an expert KNX and ETS engineer.

You MUST return ONLY valid JSON.

No markdown.
No explanations.
No comments.
No extra text.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    try:
        project = json.loads(content)

    except Exception as e:

        project = {
            "group_addresses": [],
            "links": [],
            "error": str(e),
            "raw_response": content
        }

    with open("group_addresses.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow(["Name", "Address"])

        for addr in project.get("group_addresses", []):

            writer.writerow([
                addr.get("name", ""),
                addr.get("address", "")
            ])

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