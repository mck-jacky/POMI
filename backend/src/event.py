'''
This file contains functions that create, cancel, manage, fetch and search events
'''

import jwt
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from .errors import InputError, AccessError
from .data import events, event_seats_list, users, db_state, dataframes
from .helper_functions import check_valid_token, is_valid_type, standardise_type, createList, send_email_helper, get_email_from_token
from .auth import auth_register, auth_login
from .data_helper import add_event_to_database, fetch_events, get_event_with_seats, get_tickets_from_user, get_users_of_event, get_num_rows_seats, \
                            commit_search, check_creator, get_info_event, cancel_event_database, return_events_of_user, read_csv_into_database, \
                            get_reviews_database, new_sales_stats

SECRET = "HelloWorld2023"
GENERATE_EVENT_ID = 1


def create_event(token, event_title, event_description, event_type, venue, venue_type, organiser,
                 start_date_time, end_date_time, num_tickets_available, tickets_left, ticket_price, 
                 price_min, price_max, image, number_of_seats=None, seating_plan_image=None):
    '''
    Hosts, once registered, can create and advertise a new event with details on the 
    event title, description, type, venue, event start/end date/time,
    number of tickets available, ticket price, min price and price, images, etc
    '''

    global events, GENERATE_EVENT_ID, event_seats_list

    success = False

    # online events do not have seats
    if venue_type.lower() == "online":
        number_of_seats = num_tickets_available
        seating_plan_image = ""

    return_info = {
        'is_success': False,
        'event_id': GENERATE_EVENT_ID
    }

    # Only registered users can create events
    if not check_valid_token(token):
        raise AccessError(description='Invalid token')

    # hosts must choose from a list of pre-defined types
    if not is_valid_type(event_type):
        raise InputError(description='Sorry, your event type is invalid.')

    # initially, number of tickets available is equal to number of tickets left
    if num_tickets_available != tickets_left:
        raise InputError(
            description='Your number of available tickets should be the same as the number of tickets left initially')

    reset_code_bytes = token.encode()

    # decode the jwt token to get user's email
    decoded_token = jwt.decode(reset_code_bytes, SECRET, algorithms=['HS256'])

    # obtain user email from the decoded jwt string
    user_email = decoded_token['email']

    # fill in details for the new event
    new_event = {
        'event_id': GENERATE_EVENT_ID,
        'creator_id': user_email,
        'host': organiser,
        'event_title': event_title,
        'event_description': event_description,
        'event_type': standardise_type(event_type),
        'event_details': {
            'venue': venue,
            'start_date_time': start_date_time,
            'end_date_time': end_date_time,
            'venue_type': venue_type,
        },
        'num_tickets_available': num_tickets_available,
        'num_tickets_left': tickets_left,
        'ticket_price': ticket_price,
        'price_min': price_min,
        'price_max': price_max,
        'image': image,
        # initially, an event doesn't have any customers. Later it will be populated by customer emails,
        # e.g. booked_customers = [xxx@gmail.com, yyy@gmail.com, zzz@gmail.com]
        'booked_customers': [],
        'number_of_seats': int(number_of_seats),
        'seating_plan_image': seating_plan_image,
        'reviews': [],
    }

    # Create seats for the event
    seats = createList(1, int(number_of_seats))
    event_seats = {
        'event_id': GENERATE_EVENT_ID,
        'event_seats': seats
    }

    event_seats_list.append(event_seats)

    # Then add the new event to the database 
    events.append(new_event)

    if db_state == True:
        add_event_to_database(GENERATE_EVENT_ID, user_email, event_title, event_description, event_type, venue, venue_type,
                              organiser, start_date_time, end_date_time,
                              num_tickets_available, tickets_left, price_min, price_max, image, number_of_seats, seating_plan_image)

    # create a sales data table in the database for data analysis that is to come later
    create_sales_data(GENERATE_EVENT_ID, num_tickets_available)
    
    if db_state == True:
        new_sales_stats(GENERATE_EVENT_ID, str(datetime.now().timestamp()))

    success = True
    
    GENERATE_EVENT_ID += 1

    return_info['is_success'] = success

    return return_info

def create_sales_data(event_id, num_tickets):
    '''
    This function initialises a sales table for an event. This table stores the 
    ticket sales data which will be constantly updated to reflect the new
    ticket sales data. This function will later be called by the demand 
    analysis function to give a prediction on the number of people that will
    end up purchasing tickets for this event
    '''
    
    global dataframes
    
    # initially, num tickets sold is negative infinity
    time_stamp = str(datetime.now().timestamp())
    data1 = [event_id, 1, num_tickets, -999999, num_tickets, time_stamp, -999999]
    data2 = [event_id, 2, num_tickets, -999999, num_tickets, time_stamp, -999999]
    data3 = [event_id, 3, num_tickets, -999999, num_tickets, time_stamp, -999999]

    dataframes.loc[len(dataframes)] = data1
    dataframes.loc[len(dataframes)] = data2
    dataframes.loc[len(dataframes)] = data3
    

def decrement_num_tickets(event_id, num_tickets_bought):
    '''
    This function decrements the number of tickets for an event. The parameter num_tickets_bought
    is an integer
    '''

    event_valid = False

    # decrement the number of tickets for this event
    for event in events:
        if event['event_id'] == event_id:
            event['num_tickets_left'] = event['num_tickets_left'] - \
                num_tickets_bought
            event_valid = True

    if not event_valid:
        raise AccessError(description='Event does not exist!')

    return {}


def get_event_database():
    '''
    This function fetches all the events, regardless of whether they are active
    '''
    
    if db_state == True:
        # db_events is a list of tuples
        db_events = fetch_events()
        list_of_dicts = []

        for event in db_events:
            new_event = {
                'event_id': event[0],
                'creator_id': event[1],
                'host': event[7],
                'event_title': event[2],
                'event_description': event[3],
                'event_type': event[4],
                'event_details': {
                    'venue': event[5],
                    'start_date_time': event[8],
                    'end_date_time': event[9],
                    'venue_type': event[6],
                    # datetime object
                    'start_date_time': event[8],
                    # datetime object
                    'end_date_time': event[9],
                },
                'num_tickets_available': event[10],
                'num_tickets_left': event[11],
                'ticket_price': event[16],
                'price_min': event[12],
                'price_max': event[13],
                'image': event[14],
                'booked_customers': get_users_of_event(event[0]),
                'number_of_seats': get_num_rows_seats(event[0]),
                'seating_plan_image': event[15],
                'reviews': get_reviews_database(event[0])
            }

            list_of_dicts.append(new_event)

        return list_of_dicts
    
    else:
        return events


def get_event_list():
    '''
    This function is called to display all future events that have not had all their tickets 
    sold out. The function returns a list of event dictionaries
    '''

    if db_state == True:
        all_events = get_event_database()
    
    else:
        all_events = events
    
    from .analytics import data_collection
    
    # When the event listing page is refreshed, do a data collection of the events that have
    # just passed
    if db_state: 
        read_csv_into_database()
        data_collection()

    return_events = []

    for event in all_events:
        event_start_datetime = datetime.strptime(
            event['event_details']['start_date_time'], '%Y %m %d %H %M %S')
        if event_start_datetime >= datetime.now() and int(event['num_tickets_left']) > 0:
            # add event to the return list to be displayed if the event has not started
            # and still has remaining tickets
            return_events.append(event)
    
    return return_events

def get_past_events():
    '''
    This function returns a list of events in the past
    '''

    return_events = []
    
    if db_state == True:
        all_events = get_event_database()
    else:
        all_events = events

    for event in all_events:
        event_end_datetime = datetime.strptime(event['event_details']['end_date_time'], '%Y %m %d %H %M %S')
        if event_end_datetime <= datetime.now():
            # add this past event to be returned
            return_events.append(event)
    
    return return_events


def search_event(token, event_keyword, event_type):
    '''
    This function allows users to search events with keyword and/pr event type. Any of the two
    search parameters event_keyword and event_type are allowed to be empty. Say if a customer 
    only searches by title, then the function returns the set of events that are identified by
    this event title, and the events can be any style. If a customer searches by title and 
    wants event type say music, then this function only returns the set of music events that
    are identified by this event title
    '''
    
    all_events = get_event_list()

    return_filtered_events = []

    filter_by_keyword = []
    filter_by_type = []

    for event in all_events:
        # filter by keywords
        if event_keyword != '':
            if event_keyword.lower() == event['event_title'].lower():
                filter_by_keyword.append(event)
            else:
                # the titles don't have to match exactly. they need to match the search
                # string up to a fuzzy matching ratio
                if (fuzz.token_set_ratio(event_keyword, event['event_title']) >= 55
                        or fuzz.token_set_ratio(event_keyword, event['event_description']) >= 55):
                    filter_by_keyword.append(event)

        elif event_keyword == '' or event_keyword == 'All':
            # the customer wants any event without a specific keyword for now
            filter_by_keyword.append(event)

        # filter by type
        if event_type != '' and is_valid_type(event_type):
            if event_type.lower() == event['event_type'].lower():
                filter_by_type.append(event)
        elif event_type == '' or event_type == 'All':
            # customer wants any type
            filter_by_type.append(event)

    # Extract events that satisfy both conditions
    return_filtered_events = [x for x in filter_by_keyword if x in filter_by_type]

    # Only append search history to user if they are logged in
    token_bytes = token.encode()
    decoded_token = jwt.decode(token_bytes, SECRET, algorithms=['HS256'])
    user_email = decoded_token['email']

    is_empty_string = False

    if event_keyword == '' or event_keyword == ' ':
        is_empty_string = True

    # add the search string to user's search history if the search string is not empty
    for user in users:
        if user['login']['email'] == user_email:
            if is_empty_string == False:
                user['search_history'].append(event_keyword)

    if db_state:
        if is_empty_string == False:
            commit_search(user_email, event_keyword)

    return return_filtered_events


def cancel_event(token, event_id):
    '''
    Hosts can cancel an event using this function. This function removes the event from the 
    database, cancels all existing bookings and broadcasts a cancellation message to all the 
    booked customers
    '''
    
    global events

    event_id = int(event_id)
    user_email = get_email_from_token(token)
    
    event_title = ''

    for event in events:
        if event['event_id'] == event_id:
            if event['creator_id'] != user_email:
                raise AccessError(
                    description='Sorry, you do not have the right to manage this event!')

            # continue if it is indeed the host who want to cancel this event

            event_title = event['event_title']
            # need to check if the event is happening in the future - at least half an hr
            event_start_time = event['event_details']['start_date_time']
            start_datetime = datetime.strptime(event_start_time, '%Y %m %d %H %M %S')

            # hosts cannot cancel an event that has started
            if start_datetime <= datetime.now():
                raise AccessError(
                    description='Sorry, you cannot cancel an event that has started!')

            # can only cancel an event if it's happening at least 30 mins from now
            if datetime.now() + timedelta(minutes=29) > start_datetime:
                raise AccessError(
                    description='Sorry, you can only cancel an event that is happening at least 30 minutes away.')

            # Remove ticket from customer's ticket list
            # Get a list of customer emails.
            customer_list = event['booked_customers']

            # Remove event from events list
            events.remove(event)

    # Remove all tickets of this event for all booked customers
    for customer_email in customer_list:
        for user in users:
            if user['login']['email'] == customer_email:
                # Create a copy of the tickets list
                tickets_copy = user['tickets'][:]

                # Iterate over the copy and remove matching tickets
                for ticket in tickets_copy:
                    if ticket['event_id'] == event_id:
                        user['tickets'].remove(ticket)

    if db_state:
        if not check_creator(user_email, event_id):
            raise AccessError(
                description='Sorry, you do not have the right to manage this event!')

        event_info = get_info_event(event_id)
        event_title = event_info["event_title"]
        event_start_time = event_info["event_start_time"]
        start_datetime = datetime.strptime(event_start_time, '%Y %m %d %H %M %S')

        # Remove the event from the database
        cancel_event_database(event_id)

        customer_list = event_info["booked_customers"]

    cancellation_message = "Dear customer:\n\nWe regret to inform you that the event " + \
        event_title + " has been cancelled due to unforeseen circumstances. " + \
        "A full refund will be issued to you within 7 days using the same payment method. " + \
        "We apologize for any inconvenience caused and appreciate your understanding."

    email_subject = "Event Cancellation Notice"

    for customer in customer_list:
        # broadcast a cancellation message to all booked customers
        send_email_helper(customer, cancellation_message, email_subject)

    return {}

def has_event_passed(event_id):
    """
    This function checks if an event has already passed. Returns True if an event has passed
    and returns false if it hasn't
    """
    
    has_passed = False

    events_list = get_event_database()
    for event in events_list:
        if event['event_id'] == event_id:
            event_end_datetime = datetime.strptime(event['event_details']['end_date_time'], '%Y %m %d %H %M %S')
            if event_end_datetime <= datetime.now():
                has_passed = True
    
    return has_passed

def user_tickets_booked(input_email):
    '''
    Given a user's email, return a list of their tickets booked for upcoming events
    '''
    
    user_tickets_info = []
    user_events_id = []
    return_list_with_tickets = []
    processed_ticket_codes = set()
    
    for user in users:
        if user['login']['email'] == input_email:
            user_tickets_info = user['tickets']
    
    # only return tickets for events that are upcoming
    for ticket in user_tickets_info:
        if not has_event_passed(ticket['event_id']):
            user_events_id.append(ticket['event_id']) 

    for event_id in user_events_id:
        for event in events:
            if event['event_id'] == event_id:
                event_dict = event

                for ticket in user_tickets_info:
                    if ticket['event_id'] != event_id:
                        continue
                    ticket_code = ticket['ticket_code']
                    seat_number = ticket['seat_number']

                    if (ticket_code, seat_number) not in processed_ticket_codes:

                        ticket_with_seat = event_dict.copy()
                        ticket_with_seat['ticket_code'] = ticket_code
                        ticket_with_seat['seat_number'] = seat_number

                        # add the ticket to be displayed on the frontend
                        return_list_with_tickets.append(ticket_with_seat)
                        processed_ticket_codes.add((ticket_code, seat_number))

    if db_state == True:
        user_tickets_info = get_tickets_from_user(input_email)
        return_list_with_tickets = []
        user_events = return_events_of_user(input_email)
        user_events_id = []
        processed_ticket_codes = set()

        for event in user_events:
            if not has_event_passed(event[0]):
                user_events_id.append(event[0])

        for event_id in user_events_id:
            event_dict = get_event_with_seats(event_id)
            for ticket in user_tickets_info:
                if ticket['event_id'] != event_id:
                    continue
                ticket_code = ticket['ticket_code']
                seat_number = ticket['seat_number']

                if (ticket_code, seat_number) not in processed_ticket_codes:

                    ticket_with_seat = event_dict.copy()
                    ticket_with_seat['ticket_code'] = ticket_code
                    ticket_with_seat['seat_number'] = seat_number

                    return_list_with_tickets.append(ticket_with_seat)
                    processed_ticket_codes.add((ticket_code, seat_number))

    return return_list_with_tickets

def user_tickets_booked_past(input_email):
    '''
    Given a user's email, return a list of their tickets booked for past events
    '''
    
    user_tickets_info = []
    user_events_id = []
    return_list_with_tickets = []
    processed_ticket_codes = set()
    
    for user in users:
        if user['login']['email'] == input_email:
            user_tickets_info = user['tickets']
    
    # only return tickets for events that have passed
    for ticket in user_tickets_info:
        if has_event_passed(ticket['event_id']):
            user_events_id.append(ticket['event_id']) 

    for event_id in user_events_id:
        for event in events:
            if event['event_id'] == event_id:
                event_dict = event

                for ticket in user_tickets_info:
                    if ticket['event_id'] != event_id:
                        continue
                    ticket_code = ticket['ticket_code']
                    seat_number = ticket['seat_number']

                    if (ticket_code, seat_number) not in processed_ticket_codes:

                        ticket_with_seat = event_dict.copy()
                        ticket_with_seat['ticket_code'] = ticket_code
                        ticket_with_seat['seat_number'] = seat_number

                        return_list_with_tickets.append(ticket_with_seat)
                        processed_ticket_codes.add((ticket_code, seat_number))

    if db_state == True:
        user_tickets_info = get_tickets_from_user(input_email)
        return_list_with_tickets = []
        user_events = return_events_of_user(input_email)
        user_events_id = []
        processed_ticket_codes = set()

        for event in user_events:
            if has_event_passed(event[0]):
                user_events_id.append(event[0])

        for event_id in user_events_id:
            event_dict = get_event_with_seats(event_id)
            for ticket in user_tickets_info:
                if ticket['event_id'] != event_id:
                    continue
                ticket_code = ticket['ticket_code']
                seat_number = ticket['seat_number']

                if (ticket_code, seat_number) not in processed_ticket_codes:

                    ticket_with_seat = event_dict.copy()
                    ticket_with_seat['ticket_code'] = ticket_code
                    ticket_with_seat['seat_number'] = seat_number

                    # add the ticket to be displayed on the frontend
                    return_list_with_tickets.append(ticket_with_seat)
                    processed_ticket_codes.add((ticket_code, seat_number))

    return return_list_with_tickets


def get_future_events():
    '''
    This function is called to display all future events regardless of whether the tickets 
    are sold out. Returns the events as a list of dictionaries
    '''

    if db_state == True:
        all_events = get_event_database()
    else:
        all_events = events

    return_events = []

    for event in all_events:
        event_start_datetime = datetime.strptime(
            event['event_details']['start_date_time'], '%Y %m %d %H %M %S')
        # still return events even if tickets are sold out because this function
        # fetches all future events
        if event_start_datetime >= datetime.now():
            return_events.append(event)
    
    return return_events

def user_events_created(input_email):
    '''
    Given an user email, return a list of events they have created, only if the event's 
    happening in the future, regardless of whether tickets are sold out
    '''

    # get the list of all future events
    all_events = get_future_events()
    
    return_events = []

    for event in all_events:
        # add the future event this user created to the list to be returned
        if (event['creator_id'] == input_email):
            return_events.append(event)

    return return_events

def get_user_events_created_past(input_email):
    '''
    Given user email, returns a list of past events created by this user
    '''

    # get the list of all past events
    past_events = get_past_events()
    
    return_events = []
    
    for event in past_events:
        # add the past event this user created to the list to be returned
        if (event['creator_id'] == input_email):
            return_events.append(event)

    return return_events

def attended_events_list(token):
    '''
    This function returns a list of events that the user has attended. User is the account
    holding the token passed in
    '''
    
    user_email = get_email_from_token(token)
    
    attended_events = []
    
    # get all past events
    past_events = get_past_events()
    
    
    # return all past events which this user is a customer of 
    for event in past_events:
        for customer_email in event['booked_customers']:
            if customer_email == user_email:
                attended_events.append(event)

    return attended_events


def get_current_event_id():
    """
    Returns the current event ID. Used for naming images sequentially for local storage.

    Parameters:
        None
    Returns:
        An event ID as a string.
    """

    return str(GENERATE_EVENT_ID)


if __name__ == '__main__':
    # some driver code for testing purpose
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    registration2 = auth_register("luya.pan@student.unsw.edu.au", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("luya.pan@student.unsw.edu.au", "hahaha")

    # Create first event. This should have event id of 1
    create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")

    

    # # Create second event. This should have event id of 2
    create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15 12", "2023 12 15 12 20 12", 80, 80, 0.0, 0.0, 0.0, "church hall photo", 80, "seats image")

    # booking = book_ticket(login_success['token'], 1, 2, [1, 2])
    print(dataframes)
    # # Create third event, should have event id of 3
    create_event(login_success['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                  "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    print("future events:")
    print(get_event_list())
    print("past events:")
    print(get_past_events())
    print("==========")
    print(get_user_events_created_past("luyapan1202@gmail.com"))
    #print(user_tickets_booked_past())


    # search_event(login_success['token'], "PRESENTED BY", "MUSIC")
    # search_event(login_success['token'], "chopin", "")

    '''
    print("----> user search history:")
    for user in users:
        print(user['search_history'])
    '''
    # print(event_seats_list)

    """print("list of all events:")
    print(get_event_database())
    # print(get_event_list())

    cancel_event(login_success['token'], 1)
    print('after cancelling event 1')
    print(get_event_database())"""

    # booking = book_ticket(login_success['token'], 1, 2, [1, 2])
    # booking2 = book_ticket(login_success2['token'], 1, 1, [10])
    # booking3 = book_ticket(login_success['token'], 2, 1, [3])
    # booking4 = book_ticket(login_success2['token'], 2, 1, [7])

    # search by title
    # Note that search_event() is implemented using fuzzy matching. So the names don't need to match exactly
    # should only return event 3
    # print("SOMETHING OBVIOUS")
    # for fuzzy matching, case should not matter
    # search_event(login_success['token'], "PRESENTED BY", "MUSIC")
    # print(search_event(login_success['token'], "chopin", ""))
    '''
    print("----> user search history:")
    for user in users:
        print(user['search_history'])
    '''
    # print(event_seats_list)

    # # returns both chopin's and debussy's nocturnes
    # print(search_event("nocturne", "", ""))

    # # should return all events
    # print(search_event("", "", ""))

    # should return event 2
    # print("SOMETHING OBVIOUS")
    # print(search_event("", "", "seasonal"))

    # 6 checks in total:
    # 1. invalid token error should be raised
    """create_event("hahaha", "Debussy's Nocturnes", "Presented by POMI Symphony Orchestra", 
                    "Music", "Concert Hall, Sydney Opera House", datetime(2023, 9,15, 5, 20, 6), 
                    datetime(2023, 9,15, 8, 20, 6), 1000, 35.5)"""

    # 2. invalid event type
    """print(create_event(login_success['token'], "Debussy's Nocturnes", "Presented by POMI Symphony Orchestra", 
                    "hahaha", "Concert Hall, Sydney Opera House", datetime(2023, 9,15, 5, 20, 6), 
                    datetime(2023, 9,15, 8, 20, 6), 1000, 35.5))"""

    # 3, 4. wrong format for event datetime
    """print(create_event(login_success['token'], "Debussy's Nocturnes", "Presented by POMI Symphony Orchestra", 
                    "Music", "Concert Hall, Sydney Opera House", 2023, 
                    datetime(2023, 9,15, 8, 20, 6), 1000, 35.5))"""

    # 5. end date cannot be before the start date
    """print(create_event(login_success['token'], "Debussy's Nocturnes", "Presented by POMI Symphony Orchestra", 
                    "Music", "Concert Hall, Sydney Opera House", datetime(2023, 9,15, 5, 20, 6), 
                    datetime(2022, 9,15, 8, 20, 6), 1000, 35.5))"""

    # 6. if start_date_time < now, raise an error
    """print(create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", 
                    "Seasonal", "POMI Church, Randwick", datetime(2022, 6,15, 6, 30, 6), 
                    datetime(2023, 12,15, 8, 30, 6), 80, 0.0))"""
