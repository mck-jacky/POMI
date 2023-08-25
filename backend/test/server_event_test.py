import json
import pytest
import signal
import requests
from datetime import datetime
from flask import Flask, request
from flask_cors import CORS
from json import dumps
from src.helper_functions import convert_str_to_datetime, convert_datetime_to_str

# Change Server Port Here
from src import config


# @pytest.fixture
def test_create_a_user():
    """
    1. Registers a new user, John.
    2. Logs the user in.
    """

    res = requests.post(config.url + 'auth/register', json={'input_email': 'john@mail.com',
                                                            'password': 'Password',
                                                            'first_name': 'John',
                                                            'last_name': 'Smith',
                                                            'cardholder_name': 'John Smith',
                                                            'card_number': '1234567812345678',
                                                            'expiry_month': '01',
                                                            'expiry_year': '2025',
                                                            'cvv_num': '123'})

    assert(res.status_code == 200)

    res2 = requests.post(config.url + 'auth/login', json={'email': 'john@mail.com',
                                                          'password': 'Password'})

    assert(res2.status_code == 200)

    token = json.loads(res2.text)['token']

    # date(year, month, day, hour, minute, seconds)
    start_date_time = datetime(2023, 9, 15, 5, 20)
    start_date_time = convert_datetime_to_str(start_date_time)
    end_date_time = datetime(2023, 9, 15, 8, 20, 6)
    end_date_time = convert_datetime_to_str(end_date_time)

    res3 = requests.post(config.url + 'event/create', json={'token': token,
                                                            'event_title': 'ZZZZZZ',
                                                            'event_description': 'My first event.',
                                                            'event_type': 'Music',
                                                            'venue': 'UNSW',
                                                            'venue_type': 'venue',
                                                            'organiser': 'John Smith',
                                                            'start_date_time': start_date_time,
                                                            'end_date_time': end_date_time,
                                                            'num_tickets_available': '100',
                                                            'tickets_left': '100',
                                                            'ticket_price': '10.00',
                                                            'image': 'image'
                                                            })

    assert(res3.status_code == 200)

    res4 = requests.get(config.url + 'event/list/get', params={'': ''})

    # Print for event/list/get
    assert(res4.status_code == 200)
    # print(json.loads(res4.text))
    # print(type(json.loads(res4.text)))
    # assert(False)

    res5 = requests.post(config.url + 'event/create', json={'token': token,
                                                            'event_title': 'Event2',
                                                            'event_description': 'My second event.',
                                                            'event_type': 'Music',
                                                            'venue': 'UNSW',
                                                            'venue_type': 'venue',
                                                            'organiser': 'John Smith',
                                                            'start_date_time': start_date_time,
                                                            'end_date_time': end_date_time,
                                                            'num_tickets_available': '100',
                                                            'tickets_left': '100',
                                                            'ticket_price': '10.00',
                                                            'image': 'image'})

    assert(res5.status_code == 200)

    res6 = requests.get(config.url + 'event/search', params={'event_title': 'Event2',
                                                             'event_description': 'My first event.',
                                                             'event_type': 'Music'})

    assert(res6.status_code == 200)
    print(json.loads(res6.text))
    assert(False)
