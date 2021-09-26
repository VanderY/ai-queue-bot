import requests

BASE_API_URL = "http://localhost:8080/api/"


def get_schedule(group, date):
    response = requests.get(BASE_API_URL + f"schedule/{group}/{date}")
    return response.json()


def get_groups():
    return {"921701", "921702", "921703", "921704"}
