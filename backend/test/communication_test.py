import pytest
from src.auth import auth_login, auth_register
from src.event import create_event
from src.errors import InputError, AccessError
from test.other import clear
from src.booking import book_ticket, list_available_seats
from src.communication import broadcast_to_customer
from src.data import events, db_state
from src.data_helper import get_users_of_event

def test_empty_email():
    """
    This tests the functionality of broadcast_to_customer when an empty message 
    and/or empty email subject is passed in
    """
    clear()
    # register first user
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")
    
    assert list_available_seats(1) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    booking = book_ticket(login['token'], 1, 1, [2])
    assert list_available_seats(1) == [1, 3, 4, 5, 6, 7, 8, 9, 10]
    
    cust_list = []
    if db_state == False:
        for event in events:
            if event['event_id'] == event1['event_id']:
                cust_list = event['booked_customers']
    
    else:
        cust_list = get_users_of_event(event1['event_id'])
    
    assert cust_list == ["registerme@gmail.com"]
    
    
    with pytest.raises(InputError):
        # empty broadcast message
        broadcast_to_customer(login['token'], event1['event_id'], "", "subject")
    
    with pytest.raises(InputError):
        # empty email subject
        broadcast_to_customer(login['token'], event1['event_id'], "a creepy message from your host haha", "")