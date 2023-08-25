import pytest
import time
from src.auth import auth_login, auth_register
from src.event import create_event, get_event_database, get_past_events
from src.errors import InputError, AccessError
from test.other import clear
from src.booking import book_ticket
from src.data import events, db_state
from src.analytics import user_analytics, forecast_demand
from datetime import datetime, timedelta

def test_demand_general():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 1, [2])
    time.sleep(65)
    assert forecast_demand(event1_id) == 4
    
    # book 3 tickets in the second hour
    booking = book_ticket(login_success['token'], event1_id, 3, [1, 3, 5])
    time.sleep(65)
    assert forecast_demand(event1_id) == 9
   
    # book 3 tickets in the second hour
    booking = book_ticket(login_success['token'], event1_id, 3, [10, 7, 9])
    time.sleep(65)
    assert forecast_demand(event1_id) == 11

def test_demand_same_num_ticket_every_hour():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 2, [1, 2])
    time.sleep(65)
    assert forecast_demand(event1_id) == 8
    
    booking = book_ticket(login_success['token'], event1_id, 2, [3, 5])
    time.sleep(65)
    assert forecast_demand(event1_id) == 8
   
    booking = book_ticket(login_success['token'], event1_id, 2, [7, 9])
    time.sleep(65)
    assert forecast_demand(event1_id) == 8

def test_demand_max_demand():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 20, 20, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 3, [1, 2, 3])
    time.sleep(65)
    assert forecast_demand(event1_id) == 12
    
    book_ticket(login_success['token'], event1_id, 5, [4, 5, 6, 7, 8])
    time.sleep(65)
    assert forecast_demand(event1_id) == 17
   
    book_ticket(login_success['token'], event1_id, 8, [9, 10, 11, 12, 13, 14, 15, 16])
    time.sleep(65)
    # capped at max num tickets
    assert forecast_demand(event1_id) == 20 

def test_decreasing_demand():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    assert forecast_demand(event1_id) == 40
    
    book_ticket(login_success['token'], event1_id, 3, [11, 12, 13])
    time.sleep(65)
    assert forecast_demand(event1_id) == 24
   
    book_ticket(login_success['token'], event1_id, 1, [14])
    time.sleep(65)
    # capped at max num tickets
    assert forecast_demand(event1_id) == 14

def test_only_purchase_first_hour():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    assert forecast_demand(event1_id) == 40
    
    # no ticket purchase in the second hour
    time.sleep(65)
    assert forecast_demand(event1_id) == 16
   
    # no ticket purchase in the third hour
    time.sleep(65)
    # capped at max num tickets
    assert forecast_demand(event1_id) == 10


def test_few_last_hour():
    """
    Purchase a lot of tickets in the first hour but not so many in later hours
    """
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    assert forecast_demand(event1_id) == 40
    
    # booking 2 tickets in second hour
    book_ticket(login_success['token'], event1_id, 2, [11, 12])
    time.sleep(65)
    assert forecast_demand(event1_id) == 21
   
    # booking just 1 ticket in the third hour
    book_ticket(login_success['token'], event1_id, 1, [15])
    time.sleep(65)
    # capped at max num tickets
    assert forecast_demand(event1_id) == 13

def test_first_few_hours():
    """
    Purchase no tickets in the first hour but many in later hours
    """
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    # book no ticket in the first hour
    time.sleep(65)
    assert forecast_demand(event1_id) == 0
    
    # book no ticket in the second hour
    time.sleep(65)
    assert forecast_demand(event1_id) == 0
   
    # book 10 tickets in the last hour
    book_ticket(login_success['token'], event1_id, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    # capped at max num tickets
    assert forecast_demand(event1_id) == 20

def test_no_data():
    """
    Purchase no tickets in the first hour but many in later hours
    """
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, 0, 100, "concert hall photo", 50, 
                 "seats image")['event_id']
    
    # no data for first hour
    time.sleep(65)
    
    # no data for second hour
    time.sleep(65)
   
    # book 10 tickets in the last hour
    book_ticket(login_success['token'], event1_id, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    # capped at max num tickets
    assert forecast_demand(event1_id) == 20