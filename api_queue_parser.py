import requests
from config import BASE_API_URL


def get_schedule(group, date):
    response = requests.get(BASE_API_URL + f"schedule/{group}/{date}")
    return response.json()


def get_subject_by_id(id: str):
    response = requests.get(BASE_API_URL + f"subject/get/{id}")
    return response.json()


def get_queue_by_id(id: str):
    response = requests.get(BASE_API_URL + f"queue/get/{id}")
    return response.json()


def get_groups():
    return {"921701", "921702", "921703", "921704"}
