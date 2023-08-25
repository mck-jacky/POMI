import pytest
from src.auth import auth_login, auth_register
from src.event import create_event, get_event_database, get_users_of_event, user_events_created, user_tickets_booked
from src.errors import InputError
from test.other import clear
from src.booking import book_ticket, list_available_seats, cancel_booking, get_event_and_seats_by_id_fixed
from src.data import db_state, events

# test book ticket
def test_book_ticket():
    '''
    Test book ticket and cancelling functionality
    '''
    clear()
    # register first user
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]

    # create event with 10 seats
    assert create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")['event_id'] == 1

    event_list = get_event_database()
    assert event_list[0]['event_id'] == 1
    # assert list_available_seats(1) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # book seat 2
    booking = book_ticket(login['token'], 1, 1, [2])
    assert list_available_seats(1) == [1, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # book seat 5, 10
    book_ticket(login['token'], 1, 2, [5, 10])
    # 5 and 10 should not show in list_available_seats
    assert list_available_seats(1) == [1, 3, 4, 6, 7, 8, 9]
    
    # test botan's func
    compare = get_event_and_seats_by_id_fixed(1)['available_seats']
    assert compare == [1, 3, 4, 6, 7, 8, 9]
    
    # cancel booking and see. seat 2 should now be available
    cancel_booking(login['token'], 1, booking[0]['ticket_code'])
    # test botan's func
    compare = get_event_and_seats_by_id_fixed(1)['available_seats']
    assert compare == [1, 2, 3, 4, 6, 7, 8, 9]
    # my func
    assert list_available_seats(1) == [1, 2, 3, 4, 6, 7, 8, 9]
    
    with pytest.raises(InputError):
        # seat 5 is taken and it can no longer be booked
        book_ticket(login['token'], 1, 1, [5])
    
    # create a second user
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")
    
    # create another event with 5 seats
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 5, 5, 0.0, 0.0, 0.0, "church hall photo", 5, 
                 "seats image")
    assert list_available_seats(2) == [1, 2, 3, 4, 5]


def test_user_events_created():
    """
    This tests the user_events_created() function, which should return a list of
    events the user has created
    """
    clear()
    # register first user
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]
    
     # create an event
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")
    # create another event with 5 seats
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 5, 5, 0.0, 0.0, 0.0, "church hall photo", 5, 
                 "seats image")
    events_list = []
    for event in user_events_created("registerme@gmail.com"):
        events_list.append(event['event_id'])
    
    assert events_list == [event1['event_id'], event2['event_id']]

def test_user_tickets_booked():
    """
    This tests the user_tickets_booked() function
    """
    clear()
    # register first user
    register = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("registerme@gmail.com", "1234567")
    assert register['email'] == login["email"]
    
    # create a second user
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")
    
    # create an event
    event1 = create_event(login['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30 12", "2023 09 15 12 39 12", 10, 10, 35.5, 35.5, 40, "concert hall photo", 10, 
                 "seats image")
    # create another event with 5 seats
    event2 = create_event(login['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 00", "2023 12 15 12 20 00", 5, 5, 0.0, 0.0, 0.0, "church hall photo", 5, 
                 "seats image")
    assert register2['email'] == login2["email"]
    
    # test booking 2 customers to both events, their ticket count should be correct and ticket code should also be correct
    booking = book_ticket(login['token'], event1['event_id'], 1, [10])
    booking2 = book_ticket(login['token'], event2['event_id'], 1, [2])
    #booking3 = book_ticket(login2['token'], 1, 1, [3])
    booking3 = book_ticket(login2['token'], event2['event_id'], 1, [5])

    events_and_tickets = user_tickets_booked("registerme@gmail.com")
    
    code_seat_pair = []
    for event_ticket in events_and_tickets:
        code_seat_pair.append((event_ticket['ticket_code'], event_ticket['seat_number']))
    
    # the seat number and ticket code pair should be returned in the dictionary
    assert (booking[0]['ticket_code'], booking[0]['seat_number']) in code_seat_pair
    assert (booking2[0]['ticket_code'], booking2[0]['seat_number']) in code_seat_pair
    
    events_and_tickets = user_tickets_booked("registerme222@gmail.com")
    code_seat_pair = []
    for event_ticket in events_and_tickets:
        code_seat_pair.append((event_ticket['ticket_code'], event_ticket['seat_number']))
    assert (booking3[0]['ticket_code'], booking3[0]['seat_number']) in code_seat_pair

def test_list_customers_single_ticket():
    """
    Test cancel booking with each customer booked to one ticket of an event
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
    
    assert list_available_seats(event1['event_id']) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    booking = book_ticket(login['token'], event1['event_id'], 1, [2])
    assert list_available_seats(event1['event_id']) == [1, 3, 4, 5, 6, 7, 8, 9, 10]
    
    cust_list = []
    if db_state == False:
        for event in events:
            if event['event_id'] == event1['event_id']:
                cust_list = event['booked_customers']
    
    else:
        cust_list = get_users_of_event(event1['event_id'])
    
    assert cust_list == ["registerme@gmail.com"]
    
    # create a second user
    register2 = auth_register("registerme222@gmail.com", "1234567", "someone", "else",
                                 "someone else", "1111222233334444", 12, 2023, "123")
    login2 = auth_login("registerme222@gmail.com", "1234567")
    
    booking = book_ticket(login2['token'], event1['event_id'], 1, [10])
    assert list_available_seats(event1['event_id']) == [1, 3, 4, 5, 6, 7, 8, 9]

    if db_state == False:
        for event in events:
            if event['event_id'] == event1['event_id']:
                cust_list = event['booked_customers']
    
    else:
        cust_list = get_users_of_event(event1['event_id'])
    
    customers = ["registerme@gmail.com", "registerme222@gmail.com"]
    for cust in customers:
        assert cust in cust_list

    # cancel booking for the second customer
    cancel_booking(login2['token'], event1['event_id'], booking[0]['ticket_code'])
    customers = ["registerme@gmail.com"]
    
    # the second user is removed from the customer list
    if db_state == False:
        for event in events:
            if event['event_id'] == event1['event_id']:
                cust_list = event['booked_customers']
    
    else:
        cust_list = get_users_of_event(event1['event_id'])
    
    assert cust_list == customers

def test_list_customers_two_tickets():
    """
    Test cancel booking with a customer booked to two tickets of an event
    When the first ticket is cancelled, the customer should remain on the
    customer list of that event
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
    
    booking = book_ticket(login['token'], event1['event_id'], 1, [2])
    booking2 = book_ticket(login['token'], event1['event_id'], 1, [10])
    assert list_available_seats(event1['event_id']) == [1, 3, 4, 5, 6, 7, 8, 9]
    
    cancel_booking(login['token'], event1['event_id'], booking[0]['ticket_code'])
    # seat 2 is freed
    assert list_available_seats(event1['event_id']) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    # but since this customer has another ticket with for event, customer email should not get removed from the customer list
    cust_list = []
    if db_state == False:
        for event in events:
            if event['event_id'] == event1['event_id']:
                cust_list = event['booked_customers']
    
    else:
        cust_list = get_users_of_event(event1['event_id'])
    
    assert cust_list == ["registerme@gmail.com"]
    
    cancel_booking(login['token'], event1['event_id'], booking2[0]['ticket_code'])
    # seat 10 is freed 
    assert list_available_seats(event1['event_id']) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    cust_list = []
    if db_state == False:
        for event in events:
            if event['event_id'] == event1['event_id']:
                cust_list = event['booked_customers']
    
    else:
        cust_list = get_users_of_event(event1['event_id'])
    
    # this customer has no more tickets associated with this event, hence the email should be removed
    assert cust_list == []



