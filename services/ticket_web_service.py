import json

import requests

import models
from config.settings import API_URL, AUTH_TOKEN


def get_ticket_by_id(ticket_id):
    url = API_URL + f"/requests/{ticket_id}"
    method = "GET"
    headers = {"authtoken": AUTH_TOKEN}
    response = requests.request(method, url, headers=headers, verify=False)
    ticket = response.json().get("request")
    return models.Ticket(**ticket)


def get_all_tickets_service(skip=0, limit=100):
    url = API_URL + "/requests"
    method = "GET"
    headers = {"authtoken": AUTH_TOKEN}
    input_data = {
        "list_info": {
            "row_count": limit,
            "start_index": skip,
            "get_total_count": True,
        }
    }
    params = {"input_data": json.dumps(input_data)}
    response = requests.request(method, url, headers=headers, params=params, verify=False)
    response_status = response.json().get("response_status", {})
    list_info = response.json().get("list_info", {})
    tickets = response.json().get("requests", [])
    return (response_status,
            list_info,
            [models.Ticket(**ticket) for ticket in tickets])


def get_tickets_by_technician_id(technician_id, skip=0, limit=10):
    url = API_URL + "/requests"
    method = "GET"
    headers = {"authtoken": AUTH_TOKEN}
    input_data = {
        "list_info": {
            "row_count": limit,
            "start_index": skip,
            "get_total_count": True,
            "search_fields": {
                "technician.id": technician_id,
            }
        },
    }
    params = {"input_data": json.dumps(input_data)}
    response = requests.request(method, url, headers=headers, params=params, verify=False)
    response_status = response.json().get("response_status", {})
    list_info = response.json().get("list_info", {})
    tickets = response.json().get("requests", [])
    return (response_status,
            list_info,
            [models.Ticket(**ticket) for ticket in tickets])