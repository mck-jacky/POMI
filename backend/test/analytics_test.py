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

def test_raise_error():
    """
    If a user has not booked tickets for any events, there's no analytics data to display
    """
    clear()
    
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    with pytest.raises(AccessError):
        user_analytics(login['token'])

def test_num_events_attended():
    """
    This tests if the analytics function is picking up only events in the past. Events that have
    not taken place cannot be used in the analytics as users may cancel ticket
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # event 1 is in the future
    event1_id = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2028 09 15 12 30 12", "2028 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    # event 2 has passed
    event2_id = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    # event 3 has passed
    event3_id = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    
    # event 4 is happening in the future
    event4_id = create_event(login['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")['event_id']

    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    book_ticket(login['token'], event3_id, 1, [4])
    book_ticket(login['token'], event4_id, 1, [3])
    
    # number of events participated must only be 2
    assert user_analytics(login['token'])['num_events_participated'] == 2

def test_fav_event_type():
    """
    Tests favourite type of the user_analytics function
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # event 1 is in the future
    event1_id = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    # event 2 has passed
    event2_id = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    # event 3 has passed
    event3_id = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    
    # event 4 is happening in the future
    event4_id = create_event(login['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI something team", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    book_ticket(login['token'], event3_id, 1, [100])
    book_ticket(login['token'], event4_id, 1, [3])
    
    assert user_analytics(login['token'])['favourite_event_type'] == 'Music'


def test_num_events_all_future():
    """
    Tests the user_analytics function when all events are happening in the future, even
    when they have booked tickets
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # event 1 is in the future
    event1_id = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2028 09 15 12 30 12", "2028 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    # event 2 has passed
    event2_id = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2028 09 15 16 30 12", "2028 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    # event 3 has passed
    event3_id = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2029 09 15 16 30 12", "2029 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    
    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    book_ticket(login['token'], event3_id, 1, [100])
    
    with pytest.raises(AccessError):
        assert user_analytics(login['token'])['num_events_participated'] == 0


def test_fav_event_type2():
    """
    Tests favourite type of the user_analytics function, when there are 3 music events but
    haven't started
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    event1_id = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2029 09 15 12 30 12", "2029 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    # only event 2 has passed
    event2_id = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event3_id = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2029 09 15 16 30 12", "2029 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    

    event4_id = create_event(login['token'], "another event", "one more event", "Music", "Olympic Park", "Olympic Park",
                 "POMI something team", "2028 09 15 16 30 12", "2028 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    book_ticket(login['token'], event3_id, 1, [100])
    book_ticket(login['token'], event4_id, 1, [3])
    
    assert user_analytics(login['token'])['num_events_participated'] == 1
    assert user_analytics(login['token'])['favourite_event_type'] == 'Seasonal'

def test_fav_event_type3():
    """
    Tests favourite type of the user_analytics function, when two event types are tied
    haven't started
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    event1_id = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Seasonal", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    event2_id = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event3_id = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2019 09 15 16 30 12", "2019 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    

    event4_id = create_event(login['token'], "another event", "one more event", "Music", "Olympic Park", "Olympic Park",
                 "POMI something team", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    book_ticket(login['token'], event3_id, 1, [100])
    book_ticket(login['token'], event4_id, 1, [3])
    
    assert user_analytics(login['token'])['num_events_participated'] == 4
    assert user_analytics(login['token'])['favourite_event_type'] == 'Seasonal'

def test_fav_host():
    """
    Tests favourite host of the user_analytics function
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    event1_id = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event2_id = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Seasonal", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    event3_id = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2019 09 15 16 30 12", "2019 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    

    event4_id = create_event(login['token'], "another event", "one more event", "Music", "Olympic Park", "Olympic Park",
                 "POMI something team", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    book_ticket(login['token'], event3_id, 1, [100])
    book_ticket(login['token'], event4_id, 1, [3])
    
    assert user_analytics(login['token'])['num_events_participated'] == 4
    assert user_analytics(login['token'])['favourite_host'] == 'POMI orchestra'

def test_fav_host2():
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    event1_id = create_event(login_success2['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event2_id = create_event(login_success2['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Seasonal", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2025 09 15 12 30 12", "2025 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    event3_id = create_event(login_success2['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2029 09 15 16 30 12", "2029 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    

    event4_id = create_event(login_success2['token'], "another event", "one more event", "Music", "Olympic Park", "Olympic Park",
                 "POMI something team", "2028 09 15 16 30 12", "2028 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    book_ticket(login_success2['token'], event1_id, 1, [1])
    book_ticket(login_success2['token'], event2_id, 1, [2])
    book_ticket(login_success2['token'], event3_id, 1, [100])
    book_ticket(login_success2['token'], event4_id, 1, [3])
    
    assert user_analytics(login_success2['token'])['num_events_participated'] == 1
    assert user_analytics(login_success2['token'])['favourite_host'] == 'POMI church'

def test_analytics_two_users():
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    event1_id = create_event(login_success2['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event2_id = create_event(login_success2['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Seasonal", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2015 09 15 12 30 12", "2015 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    event3_id = create_event(login_success2['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2019 09 15 16 30 12", "2019 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    

    event4_id = create_event(login_success2['token'], "another event", "one more event", "Music", "Olympic Park", "Olympic Park",
                 "POMI something team", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    # user 1 only books for seasonal events
    book_ticket(login['token'], event1_id, 1, [1])
    book_ticket(login['token'], event2_id, 1, [2])
    
    # user 2 books ticket for events 2, 3, 4
    book_ticket(login_success2['token'], event2_id, 1, [3])
    book_ticket(login_success2['token'], event3_id, 1, [100])
    book_ticket(login_success2['token'], event4_id, 1, [3])
    
    # user 2 participated in 3 events, user 1 participated in 2 events
    assert user_analytics(login['token'])['num_events_participated'] == 2
    assert user_analytics(login_success2['token'])['num_events_participated'] == 3
    
    # fav host of user 2 is pomi orchestra
    assert user_analytics(login_success2['token'])['favourite_host'] == 'POMI orchestra'
    
    # fav event type of user 2 is music
    assert user_analytics(login_success2['token'])['favourite_event_type'] == 'Music'
    
    # fav host of user 1 is pomi church
    assert user_analytics(login['token'])['favourite_host'] == 'POMI church'
    
    # fav event type of user 1 is seasonal
    assert user_analytics(login['token'])['favourite_event_type'] == 'Seasonal'


def test_demand_general():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # need to change the 
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 50, 50, 35.5, "concert hall photo", 50, 
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
