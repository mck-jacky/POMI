import pytest
from src.auth import auth_login, auth_register
from src.event import create_event, get_event_list, search_event, cancel_event, get_event_database, \
                        get_tickets_from_user, get_past_events, get_future_events, user_events_created, \
                            get_user_events_created_past, attended_events_list, has_event_passed, user_tickets_booked,\
                            user_tickets_booked_past
from src.errors import InputError, AccessError
from test.other import clear
from src.analytics import retrieve_search_history
from src.booking import book_ticket
from src.data import db_state, users

def test_create_event():
    """
    Tests creating an event successfully, also tests if the get_event_list() function is working properly
    """
    clear()
    # REGISTER a user called Jack Citizen, with email and password
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]

    # this event should be created successfully
    assert create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id'] == 1

    event_list = get_event_database()
    
    # event with id 1 should be created and stored in the event list
    assert event_list[0]['event_id'] == 1
    
    # Create another event 
    # Create second event. This should have event id of 2
    assert create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, 
                 "seats image")['event_id'] == 2
    event_list = get_event_database()
    # event with id 2 should be created and stored in the event list
    assert event_list[1]['event_id'] == 2
    
    # raise an error if  invalid token is passed in to create an event
    with pytest.raises(AccessError):
        create_event("invalid token haha", "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                    "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, 
                    "seats image")

def test_search_result():
    """
    This tests if the search_event() function returns the correct list of events given 
    a search string
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # create 3 events
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    # Create second event. This should have event id of 2
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 12", "2023 12 15 12 20 12", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, "seats image")

    # Create third event, should have event id of 3
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2023 09 15 16 30 12", "2023 09 15 16 35 12", 100, 100, 35.5, 35.5, 45, "concert hall photo", 100, "seats image")

    # search should return event 1 and event 3
    search_result = search_event(login['token'], "chopin", "")
    search_result_event_id = []
    for event in search_result:
        search_result_event_id.append(event['event_id'])
    
    assert search_result_event_id == [event1['event_id'], event3['event_id']]


def test_search_result2():
    """
    This tests if the search_event() function returns the correct list of events given 
    a search string, but with a different test case
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # create 3 events
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    # Create second event. This should have event id of 2
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 12", "2023 12 15 12 20 12", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, "seats image")

    # Create third event, should have event id of 3
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2023 09 15 16 30 12", "2023 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    search_result = search_event(login['token'], "presented by", "")
    search_result_event_id = []
    for event in search_result:
        search_result_event_id.append(event['event_id'])
    
    assert search_result_event_id == [event2['event_id'], event3['event_id']]
    
    search_result = search_event(login['token'], "presented by", "seasonal")
    search_result_event_id = []
    for event in search_result:
        search_result_event_id.append(event['event_id'])
    
    assert search_result_event_id == [event2['event_id']]


def test_search_history():
    """
    Test for testing search history implementation and the retrieve search history in analytics.py
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # create 3 events
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    # Create second event. This should have event id of 2
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 12", "2023 12 15 12 20 12", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, "seats image")

    # Create third event, should have event id of 3
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2023 09 15 16 30 12", "2023 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    search_result = search_event(login['token'], "chopin", "")
    
    history = ["chopin"]
    assert retrieve_search_history(login['token']) == history
    
    search_event(login['token'], "presented by", "seasonal")
    
    history = ["chopin", "presented by"]
    assert retrieve_search_history(login['token']) == history


def test_search_history_empty():
    """
    Test for testing search history implementation and the retrieve search history in analytics.py, but empty
    strings should not be appended to user search history
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    
    # create 3 events
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    # Create second event. This should have event id of 2
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 12", "2023 12 15 12 20 12", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, "seats image")

    # Create third event, should have event id of 3
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2023 09 15 16 30 12", "2023 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    search_event(login['token'], "chopin", "")
    assert retrieve_search_history(login['token']) == ["chopin"]
    
    search_event(login['token'], "presented by", "seasonal")
    assert retrieve_search_history(login['token']) == ["chopin", "presented by"]
    
    # empty strings or spaces should not get appended
    search_event(login['token'], "", "")
    assert retrieve_search_history(login['token']) == ["chopin", "presented by"]
    
    search_event(login['token'], " ", "")
    assert retrieve_search_history(login['token']) == ["chopin", "presented by"]


def test_cancel_event():
    """
    This tests the cancel_event function
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]
    
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")

    # this event should be created successfully
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")

    event_list = get_event_list()
    
    # event with id 1 should be created and stored in the event list
    assert len(event_list) == 1
    
    # Create another event 
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, 
                 "seats image")
    event_list = get_event_list()
    # we now have 2 events
    assert len(event_list) == 2
    
    # cancel event 1
    cancel_event(login['token'], event1['event_id'])
    
    event_list = get_event_list()
    # only event 2 should remain
    assert event_list[0]['event_id'] == event2['event_id']
    assert len(event_list) == 1
    
    # a non host trying to cancel and event should raise an error
    with pytest.raises(AccessError):
        cancel_event(login2['token'], event2['event_id'])
        
    # cancel event 2
    cancel_event(login['token'], event2['event_id'])
    event_list = get_event_database()
    
    # all events are now cancelled
    assert len(event_list) == 0

def test_cancel_event_check_ticket():
    """
    This tests the cancel_event function by checking tickets of customers to events
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, 
                 "seats image")
    event_list = get_event_database()
    # we now have 2 events
    assert len(event_list) == 2

    # book a user to event 1
    book_ticket(login['token'], event1['event_id'], 1, [10])
    # book the user to event 2
    book_ticket(login['token'], event2['event_id'], 1, [2])
    
    # check user 1 has 1 event 1 ticket, and 1 event 2 ticket
    ticket_list = []
    ticket_code_list = []
    if db_state == False:
        for user in users:
            if user['login']['email'] == "registerme@gmail.com":
                ticket_list = user['tickets']
                for ticket in ticket_list:
                    ticket_code_list.append(ticket['ticket_code'])
        assert len(ticket_list) == 2
        for ticket in ticket_list:
            assert ticket['ticket_code'] in ticket_code_list
            
    else:
        ticket_list = get_tickets_from_user("registerme@gmail.com")
        for ticket in ticket_list:
            ticket_code_list.append(ticket['ticket_code'])
        assert len(ticket_list) == 2
        for ticket in ticket_list:
            assert ticket['ticket_code'] in ticket_code_list

    # cancel event 1
    cancel_event(login['token'], event1['event_id'])
    
    if db_state == False:
        for user in users:
            if user['login']['email'] == "registerme@gmail.com":
                ticket_list = user['tickets']
                for ticket in ticket_list:
                    ticket_code_list.append(ticket['ticket_code'])
                    # only ticket for event 2 is left, because event 1 is cancelled
                    assert ticket['event_id'] == event2['event_id']
        assert len(ticket_list) == 1
    else: 
        ticket_list = get_tickets_from_user("registerme@gmail.com")
        for ticket in ticket_list:
            ticket_code_list.append(ticket['ticket_code'])
        for ticket in ticket_list:
            assert ticket['ticket_code'] in ticket_code_list
            assert ticket['event_id'] == event2['event_id']
        assert len(ticket_list) == 1

def test_past_event_list():
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    # events 2 and 3 are in the past
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2000 12 15 12 15 00", "2000 12 15 12 20 00", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, 
                 "seats image")
    
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    event_list = get_event_database()
    # there are 3 events. one's happening in the future, two are already passed. so get_past_events() should return events 2 and 3
    assert len(event_list) == 3
    
    future_events = get_future_events()
    
    future_events_id = []
    for event in future_events:
        future_events_id.append(event['event_id'])
    
    assert event1['event_id'] in future_events_id
    
    
    past_events = get_past_events()
    past_events_id = []
    for event in past_events:
        past_events_id.append(event['event_id'])
    
    assert event2['event_id'] in past_events_id
    assert event3['event_id'] in past_events_id

def test_get_event_list():
    """
    Tests the get_event_list() function
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")
    # event in the past
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2000 12 15 12 15 00", "2000 12 15 12 20 00", 8, 8, 0.0, 0.0, 0.0, "church hall photo", 8, 
                 "seats image")
    
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2023 09 15 16 30 12", "2023 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    event4 = create_event(login['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")
    
    event_list = get_event_list()
    # event 2 is in the past so it should not display event 2. later event 4 tickets will be sold and event 4 won't be shown
    assert len(event_list) == 3
    
    future_events = get_event_list()
    
    future_events_id = []
    for event in future_events:
        future_events_id.append(event['event_id'])
    
    assert event1['event_id'] in future_events_id
    # event 2 is in the past so it should not get picked up by get_event_list()
    assert event2['event_id'] not in future_events_id
    assert event3['event_id'] in future_events_id
    assert event4['event_id'] in future_events_id
    
    # sell all tickets of event 4
    book_ticket(login['token'], event4['event_id'], 3, [1, 2, 3])
    
    future_events = get_event_list()
    
    future_events_id = []
    for event in future_events:
        future_events_id.append(event['event_id'])
    
    assert event1['event_id'] in future_events_id
    assert event3['event_id'] in future_events_id
    # tickets of event 4 are sold out so it shouldn't be picked up by get_event_list()
    assert event4['event_id'] not in future_events_id


def test_get_future_events():
    """
    Tests the get_future_events() function
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]
    
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")
    # event in the past
    event2 = create_event(login2['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2000 12 15 12 15 00", "2000 12 15 12 20 00", 8, 8, 0.0, 0.0, 0.0, "church hall photo", 8, 
                 "seats image")
    
    event3 = create_event(login['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2023 09 15 16 30 12", "2023 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    event4 = create_event(login['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")
    
    event_list = get_future_events()
    # event 2 is in the past so it should not display event 2.
    assert len(event_list) == 3
    
    future_events = get_future_events()
    
    future_events_id = []
    for event in future_events:
        future_events_id.append(event['event_id'])
    
    assert event1['event_id'] in future_events_id
    # event 2 is in the past so it should not get picked up by get_event_list()
    assert event2['event_id'] not in future_events_id
    assert event3['event_id'] in future_events_id
    assert event4['event_id'] in future_events_id
    
    # sell all tickets of event 4
    book_ticket(login['token'], event4['event_id'], 3, [1, 2, 3])
    
    future_events = get_future_events()
    
    future_events_id = []
    for event in future_events:
        future_events_id.append(event['event_id'])
    
    assert event1['event_id'] in future_events_id
    assert event3['event_id'] in future_events_id
    # tickets of event 4 are sold out but it should still be displayed as get_future_events() 
    # function is not for the landing page so number of tickets left doesn't matter
    assert event4['event_id'] in future_events_id

def test_user_events_created():
    """
    Tests user_events_created() function
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]
    
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 2, 2, 35.5, 35.5, 40, "concert hall photo", 2, 
                 "seats image")
    # event in the past
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2000 12 15 12 15 00", "2000 12 15 12 20 00", 20, 20, 0.0, 0.0, 0.0, "church hall photo", 20, 
                 "seats image")
    
    event3 = create_event(login2['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    event4 = create_event(login2['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")
    
    # testing events created by user 1
    event_shown_1 = user_events_created("registerme@gmail.com")
    # == 1 because past events are not displayed (past events are displayed using another function)
    assert len(event_shown_1) == 1
    assert event_shown_1[0]['event_id'] == event1['event_id']
    
    # sell all tickets of event 1, event 1 should still get displayed
    book_ticket(login2['token'], event1['event_id'], 2, [1, 2])
    
    event_shown_1 = user_events_created("registerme@gmail.com")
    assert len(event_shown_1) == 1
    assert event_shown_1[0]['event_id'] == event1['event_id']
    
    # testing events created by user 2
    event_shown_2 = user_events_created("registerme222@gmail.com")
    assert len(event_shown_2) == 1
    assert event_shown_2[0]['event_id'] == event4['event_id']
    # sell all tickets of event 4, event 4 should still get displayed
    book_ticket(login2['token'], event4['event_id'], 3, [1, 2, 3])
    
    event_shown_2 = user_events_created("registerme222@gmail.com")
    assert len(event_shown_2) == 1
    assert event_shown_2[0]['event_id'] == event4['event_id']


def test_get_user_events_created_past():
    """
    Tests the get_user_events_created_past() function
    """
    clear()
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]
    
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")

    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2019 09 15 12 30 12", "2019 09 15 12 39 12", 2, 2, 35.5, 35.5, 40, "concert hall photo", 2, 
                 "seats image")
    # event in the past
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2000 12 15 12 15 00", "2000 12 15 12 20 00", 20, 20, 0.0, 0.0, 0.0, "church hall photo", 20, 
                 "seats image")
    
    event3 = create_event(login2['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 50, "concert hall photo", 100, "seats image")
    
    event4 = create_event(login['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")

    past_events_user1 = get_user_events_created_past("registerme@gmail.com")
    # event 4 is in the future so it shouldn't be displayed in past_events_user1
    assert len(past_events_user1) == 2
    past_event_id_1 = []
    for event in past_events_user1:
        past_event_id_1.append(event['event_id'])
    
    assert event1['event_id'] in past_event_id_1
    assert event2['event_id'] in past_event_id_1
    # event 3 is created by another user
    assert event3['event_id'] not in past_event_id_1
    # event 4 is in the future
    assert event4['event_id'] not in past_event_id_1
    
    past_events_user2 = get_user_events_created_past("registerme222@gmail.com")
    assert len(past_events_user2) == 1
    assert past_events_user2[0]['event_id'] == event3['event_id']

def test_attended_events_list():
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    # Create second user
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")

    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2018 09 15 12 30 12", "2018 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    # Create second event. This should have event id of 2
    event2_id = create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    # event 3
    event3_id = create_event(login_success['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    
    # event 4 is happening in the future
    event4_id = create_event(login_success['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")['event_id']
    
    # user 1 books for events 1, 2, 4. attended events should be 1, 2
    book_ticket(login_success['token'], event1_id, 1, [3])
    book_ticket(login_success['token'], event2_id, 1, [10])
    book_ticket(login_success['token'], event4_id, 1, [1])

    # user 2 books for events 2, 3, 4. attended events should be 2, 3. 
    book_ticket(login_success2['token'], event2_id, 1, [9])
    book_ticket(login_success2['token'], event3_id, 1, [20])
    book_ticket(login_success2['token'], event4_id, 1, [3])
    
    # for user 1: 
    # event 4 is in the past, so only events 1 and 2 are the attended events
    assert len(attended_events_list(login_success['token'])) == 2
    
    attended_event_id_1 = []
    
    for event in attended_events_list(login_success['token']):
        attended_event_id_1.append(event['event_id'])
    
    attended_event_id_1.sort()
    
    event_ids_1 = [event1_id, event2_id]
    event_ids_1.sort()
    
    assert attended_event_id_1 == event_ids_1
    
    # for user 2:
    attended_event_id_2 = []
    
    for event in attended_events_list(login_success2['token']):
        attended_event_id_2.append(event['event_id'])
    
    attended_event_id_2.sort()
    event_ids_2 = [event2_id, event3_id] # !!!!
    event_ids_2.sort()
    
    assert attended_event_id_2 == event_ids_2


def test_has_event_passed():
    """
    Tests the has_event_passed() function
    """
    clear()
    
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    # Create first event. This should have event id of 1
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2018 09 15 12 30 12", "2018 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    event2_id = create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event3_id = create_event(login_success['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", 
                 "Face to face", "POMI orchestra", "2029 09 15 16 30 12", "2029 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 
                 100, "seats image")['event_id']
    
    event4_id = create_event(login_success['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")['event_id']

    assert has_event_passed(event1_id) == True
    assert has_event_passed(event2_id) == True
    assert has_event_passed(event3_id) == False
    assert has_event_passed(event4_id) == False

def test_user_tickets_past_present():
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    # Create second user
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")

    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2018 09 15 12 30 12", "2018 09 15 12 45 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id']

    event2_id = create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']
    
    event3_id = create_event(login_success['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                  "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                  "seats image")['event_id']
    
    event4_id = create_event(login_success['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, 
                 "seats image 2")['event_id']
    
    # user 1 books for events 1, 2, 4
    book_ticket(login_success['token'], event1_id, 1, [3])
    book_ticket(login_success['token'], event2_id, 1, [10])
    book_ticket(login_success['token'], event4_id, 1, [2])

    # user 2 books for events 2, 3, 4
    book_ticket(login_success2['token'], event2_id, 1, [9])
    book_ticket(login_success2['token'], event3_id, 1, [20])
    book_ticket(login_success2['token'], event4_id, 1, [3])

    user1_future_ticket_events = []
    event_booked = user_tickets_booked("luyapan1202@gmail.com")
    for dictionary in event_booked:
        user1_future_ticket_events.append(dictionary['event_id'])
    
    assert event4_id in user1_future_ticket_events
    
    user1_past_ticket_events = []
    event_booked_past = user_tickets_booked_past("luyapan1202@gmail.com")
    
    for dictionary in event_booked_past:
        user1_past_ticket_events.append(dictionary['event_id'])

    assert event1_id in user1_past_ticket_events
    assert event2_id in user1_past_ticket_events
    
    # test user 2
    user2_future_ticket_events = []
    event_booked = user_tickets_booked("scanlulu@gmail.com")
    for dictionary in event_booked:
        user2_future_ticket_events.append(dictionary['event_id'])
    
    assert event4_id in user2_future_ticket_events
    
    user2_past_ticket_events = []
    event_booked = user_tickets_booked_past("scanlulu@gmail.com")
    for dictionary in event_booked:
        user2_past_ticket_events.append(dictionary['event_id'])
    
    assert event2_id in user2_past_ticket_events
    assert event3_id in user2_past_ticket_events