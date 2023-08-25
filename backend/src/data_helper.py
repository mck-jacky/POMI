'''
This file contains the database helper functions to store data into and fetch data from the database
'''

import psycopg2
import sys
import jwt
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
import pandas as shiong_mao
import os

SECRET = "HelloWorld2023"
db = None



def establish_connection():
    '''
    Establish connection to the database
    '''
    # changes global db variable to hold the connection object
    global db

    try:
        db = psycopg2.connect(dbname="COMP3900")
    except psycopg2.Error as err:
        print("DB error: ", err)
    except Exception as err:
        print("Internal Error: ", err)
        raise err
    '''
    finally:
        if db is not None:
        db.close()
        sys.exit(0)
    '''


accounts = []

# Precondition: enter all details of a new account
# Postcondition: returns None
def add_account_to_database(email, password, first_name, last_name,
                            card_number, cvv, card_name, exp_month, exp_year):
    '''
    This function adds the new user to the database
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT u.email
        FROM Users u
        WHERE u.email = %s
    """, [str(email)])

    result = cur.fetchall()

    if result:
        return

    cur = db.cursor()
    cur.execute("""
        INSERT INTO Users VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s)
    """, [email, str(password), first_name, last_name, str(card_number),
          str(cvv), str(card_name), str(exp_month), str(exp_year)])

    db.commit()

    # if db is not None:
    #    db.close()


# precondition: add all details of a newly created event

# postcondition: returns None
def add_event_to_database(event_id, email, title, description, type_, venue, venue_type, organizer, start_datetime, end_datetime,
                          tickets_available, tickets_left, price_min, price_max, image, num_seats, seat_plan, num_rows=1):
    '''
    This function creates and stores a new event in the database, and creates new 
    seats in the Seats table
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        INSERT INTO Events VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [str(event_id), str(email), str(title), str(description), str(type_), venue, venue_type, str(organizer), str(start_datetime),
          str(end_datetime), str(tickets_available), str(tickets_left), str(price_min),
          str(price_max), str(image), str(seat_plan), str(price_min)])

    db.commit()

    create_seats(num_rows, num_seats, event_id)

    # if db is not None:
    #    db.close()


# precondition: enter an email and new password
# postconditions: returns None
def change_password_in_database(email, new_password):
    '''
    This function updates the database so that the account with inserted email is linked
    to the new password
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        UPDATE Users
        SET password_ = %s
        WHERE email = %s
    """, [str(new_password), email])

    db.commit()

    # if db is not None:
    #    db.close()


# preconditions: None
# postconditions: returns a list with all informations of each event,
#                 stored as a tuple
def fetch_events():
    '''
    This function fetches all the events from the database
    '''
    
    global db

    update_prices()

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT * 
        FROM Events e
    """)

    events = cur.fetchall()

    if not events:
        return []

    return events


# preconditions: enter email and password
# postconditions: returns True if email and password match,
#                 otherwise, returns False (including if email does not exist)
def password_match(email, password):
    '''
    This function checks if users' login credentials match the ones stored in the database.
    If email and password match, return true, else return false
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT u.password_ 
        FROM Users u
        WHERE u.email = %s
    """, [email])

    result = cur.fetchall()

    if len(result) != 1:
        return False

    if str(result[0][0]) == str(password):
        return True
    return False


# precondtions: enter event_id and the number that tickets left should
#               be decremented by
# postcondtions: returns False if tickets_left would have become negative,
#                otherwise, returns True
def decrement_tickets(event_id, tickets_sold):
    '''
    Decreases tickets left by tickets_sold amount if tickets left does not become negative
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT e.id, e.tickets_available, e.tickets_left
        FROM Events e
        WHERE e.id = %s
    """, [str(event_id)])

    event = cur.fetchall()

    if (int(event[0][2]) - tickets_sold) < 0:
        return False

    num_tickets_left = int(event[0][2]) - tickets_sold
    cur.execute("""
        UPDATE Events
        SET tickets_left = %s
        WHERE id = %s
    """, [str(num_tickets_left), event_id])

    db.commit()

    return True

# postconditions: give event_id and amount of tickets that tickets left should
#                 be incremented by
# postconditions: returns False if tickets left would have become greater than
#                 tickets available; otherwise, returns True
def increment_tickets(event_id, tickets_refunded):
    '''
    Increments tickets left if tickets left would not have become larger than tickets available
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT e.id, e.tickets_available, e.tickets_left
        FROM Events e
        WHERE e.id = %s
    """, [str(event_id)])

    event = cur.fetchall()

    if (int(event[0][2]) + tickets_refunded) > int(event[0][1]):
        return False

    num_tickets_left = int(event[0][2]) + tickets_refunded
    cur.execute("""
        UPDATE Events
        SET tickets_left = %s
        WHERE id = %s
    """, [str(num_tickets_left), event_id])

    db.commit()

    return True


def create_seats(rows, seat_num, event_id):
    '''
    Create seats for the event in the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    if int(seat_num) == 0:
        return
    else:
        query = "INSERT INTO Seats VALUES "

        for row in range(rows):
            for seat in range(int(seat_num)):
                query += f"({row+1}, {seat+1}, {event_id}, Null)"
                query += ", "

        query = query[:-2]
        query += ";"

        cur.execute(query)

        db.commit()


# preconditions: give event_id
# postcondtions: returns True if event with that id exists; otherwise, returns False
def find_event(event_id):
    '''
    Given an event id, check if the event is in the database
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT e.id
        FROM Events e
        WHERE e.id = %s
    """, [str(event_id)])

    result = cur.fetchall()

    if not result:
        return False
    if int(result[0][0]) == int(event_id):
        return True
    else:
        return False


# preconditions: give email
# postconditions: returns True if user with this email exists; otherwise, returns False
def find_user(email):
    '''
    Given an email, check if an account associated with this email exists
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT u.email
        FROM Users u
        WHERE u.email = %s
    """, [str(email)])

    result = cur.fetchall()

    if not result:
        return False
    if str(result[0][0]) == str(email):
        return True
    else:
        return False


def give_free_seats(event_id):
    '''
    Given an event id, return all availible seat numbers of this event as a list
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.row_, s.seat_num
        FROM Seats s
        WHERE s.event_ = %s AND s.user_ IS NULL
    """, [str(event_id)])

    result = cur.fetchall()

    # this line eliminates the row in the return value
    result = [x[1] for x in result]

    return result


# preconditions: give an email, an event_id and a list of seat numbers
# postconditions: returns True if all seats could be reserved; otherwise, returns False
def is_seat_available(email, event_id, seat_num, row=1):
    '''
    Only reserves the seats if all of the seat numbers in the requested seats list are 
    available; otherwise, does not reserve any seats
    '''
    
    global db

    if not isinstance(seat_num, list):
        return False

    if db is None:
        establish_connection()

    ticket_query = "("
    query_arguments = [str(event_id), str(row)]
    for seat in seat_num:
        ticket_query += " seat_num = %s OR"
        query_arguments.append(str(seat))

    ticket_query = ticket_query[:-2]
    ticket_query += ")"

    query_start = """
        SELECT s.user_
        FROM Seats s
        WHERE event_ = %s AND row_ = %s AND """

    query = query_start + ticket_query

    cur = db.cursor()
    cur.execute(query, query_arguments)
    result = cur.fetchall()

    if len(seat_num) != len(result):
        return False

    for reservation in result:
        if reservation[0] is not None:
            return False

    cur = db.cursor()
    for seat in seat_num:

        cur.execute("""
            UPDATE Seats
            SET user_ = %s
            WHERE event_ = %s AND row_ = %s AND seat_num = %s
        """, [str(email), str(event_id), str(row), str(seat)])

    db.commit()

    return True


# preconditions: give email
# postconditions: returns a list of tuples in which the first element is
#                 the event_id and the second element is the seat number
#                 of all events that the user booked
def return_events_of_user(email):
    '''
    This function returns a list of events created by user with this email
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.event_, s.row_, s.seat_num
        FROM Seats s
        WHERE user_ = %s
    """, [str(email)])

    result = cur.fetchall()

    if result:
        # this line modifies output to forego row
        result = [(x[0], x[2]) for x in result]

        return result

    else:
        return []


def get_users_of_event(event_id):
    '''
    This function returns a list of customer emails of an event
    '''

    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.user_
        FROM Seats s
        WHERE event_ = %s AND user_ IS NOT NULL
    """, [str(event_id)])

    result = cur.fetchall()

    if result:
        result = [x[0] for x in result]
        result = list(dict.fromkeys(result))
        # result = [*set(result)]
        return result
    else:
        return []


# preconditions: give event_id
# postconditions: returns an int that is the total number of seats for the event
def get_num_rows_seats(event_id):
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT row_, seat_num
        FROM Seats s
        WHERE event_ = %s
    """, [str(event_id)])

    result = cur.fetchall()

    if result:
        max_row = max([int(x[0]) for x in result])
        max_seat = max([int(x[1]) for x in result])
        # change return value to (max_row, max_seat) if rows are implemented

        return max_seat
    else:
        # change return value to (0, 0) if rows are implemented
        return 0


# preconditions: give email, event_id and seat number
# postcondtions: returns True if booking was successfully canceled;
#                returns False if the input was invalid
def cancel_booking(email, event_id, seat_num, row=1):
    '''
    This function deletes a reservation/booking
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.user_
        FROM Seats s
        WHERE event_ = %s AND row_ = %s AND seat_num = %s
    """, [str(event_id), str(row), str(seat_num)])

    result = cur.fetchall()

    if result[0][0] != email:
        return False

    cur = db.cursor()
    cur.execute("""
        UPDATE Seats
        SET user_ = NULL
        WHERE event_ = %s AND row_ = %s AND seat_num = %s
    """, [str(event_id), str(row), str(seat_num)])

    db.commit()

    return True



# preconditions: give email, timestamp and search_term
# postconditions: returns None
def commit_search(email, search_term, timestamp=None):
    '''
    This function saves the search queries of users in the database
    '''
    
    global db

    if search_term == "":
        return

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        INSERT INTO Searches
        VALUES (DEFAULT, %s, %s, %s)
    """, [str(timestamp), str(email), str(search_term)])

    db.commit()



# preconditions: give email
# postconditions: returns a list of tuples; each tuple represents one search attempt;
#                 the first element is the search term, the second is the timestamp
def get_searches(email):
    '''
    This function [ulls the complete search history of this user from the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.search_term, s.timestamp_
        FROM Searches s
        WHERE s.user_ = %s
    """, [str(email)])

    results = cur.fetchall()

    if not results:
        return []

    # uncomment following line if only the search terms need to be returned
    results = [x[0] for x in results]

    # filter out empty search_terms in the list
    results = [x for x in results if x]

    return results


def get_info_from_booked_events(email):
    '''
    This function returns all the information of events that a user has booked
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT DISTINCT e.id, e.creater, e.title, e.description_,
                e.type_, e.venue, e.venue_type, e.organizer
        FROM Seats s
            JOIN Events e ON e.id = s.event_
        WHERE s.user_ = %s
    """, [str(email)])

    result = cur.fetchall()

    if result:
        return result

    else:
        return []


def has_user_reservation(email, event_id):
    '''
    This function checks if the user has anymore bookings to an event (if a user
    is still the customer of an event)
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.user_
        FROM Seats s
        WHERE s.user_ = %s AND s.event_ = %s
    """, [str(email), str(event_id)])

    result = cur.fetchall()

    if result:
        return True

    else:
        return False


def get_email_from_token_copy(token):
    '''
    Given a jwt token, decode to obtain user email
    '''
    
    token_bytes = token.encode()
    decoded_token = jwt.decode(
        token_bytes, SECRET, algorithms=['HS256'])
    user_email = decoded_token['email']

    return user_email


def give_recommendations(email):
    '''
    This function performs event recommendation
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    # pull all required information
    searches = get_searches(email)
    booked_events = get_info_from_booked_events(email)
    all_events = fetch_events()

    # create dictionaries in which you rate all the events accoring to
    # this particular matching
    search_history_rating = {}
    booked_events_rating = {}
    popularity_rating = {}
    total_rating = {}
    popularity_ranking = []

    # initialize all events in the dictionaries with a score of 0
    for event in all_events:
        search_history_rating[event[0]] = 0
        booked_events_rating[event[0]] = 0
        popularity_rating[event[0]] = 0
        total_rating[event[0]] = 0

    # multipliers and cutoffs
    creator_multiplier = 6
    creator_cutoff = 70
    title_multiplier = 7
    title_cutoff = 70
    description_multiplier = 3
    description_cutoff = 15
    type_multiplier = 4
    type_multiplier = 70
    venue_multiplier = 2
    venue_cutoff = 30
    organizer_multiplier = 5
    organizer_cutoff = 70

    # check each field for similar strings and add points if the the match in % is greater than the cutoff point
    for event in all_events:
        # search within the search history
        for search in searches:

            if fuzz.ratio(str(event[1]), search[0]) > creator_cutoff:
                search_history_rating[event[0]] += creator_multiplier

            if fuzz.ratio(str(event[2]), search[0]) > title_cutoff:
                search_history_rating[event[0]] += title_multiplier

            if fuzz.ratio(str(event[3]), search[0]) > description_cutoff:
                search_history_rating[event[0]] += description_multiplier

            if fuzz.ratio(str(event[4]), search[0]) > type_multiplier:
                search_history_rating[event[0]] += type_multiplier

            if fuzz.ratio(str(event[5]) + str(event[6]), search[0]) > venue_cutoff:
                search_history_rating[event[0]] += venue_multiplier

            if fuzz.ratio(str(event[7]), search[0]) > organizer_cutoff:
                search_history_rating[event[0]] += organizer_multiplier

            search_history_rating[event[0]
                                  ] = search_history_rating[event[0]] * 3

        # search among the booked tickets
        for booked_event in booked_events:

            if str(event[1]) == str(booked_event[1]):
                booked_events_rating[event[0]] += creator_multiplier

            if str(event[2]) == str(booked_event[2]):
                booked_events_rating[event[0]] += title_multiplier

            if fuzz.ratio(str(event[3]), str(booked_event[3])) > description_cutoff:
                booked_events_rating[event[0]] += description_multiplier

            if str(event[4]) == str(booked_event[4]):
                booked_events_rating[event[0]] += type_multiplier

            if fuzz.ratio(str(event[5]) + str(event[6]), str(booked_event[5]) + str(booked_event[6])) > venue_cutoff:
                booked_events_rating[event[0]] += venue_multiplier

            if str(event[7]) == str(booked_event[7]):
                booked_events_rating[event[0]] += organizer_multiplier

            booked_events_rating[event[0]] *= 5

        # consider the popularity of the event
        popularity_rating[event[0]] = (
            int(event[10]) - int(event[11])) / float(event[10]) * 3

    # add all the points together
    for key in total_rating.keys():
        total_rating[key] += (search_history_rating[key] +
                              booked_events_rating[key] + popularity_rating[key])
        # if the user already booked the event, remove it from the recommendations
        if has_user_reservation(email, key):
            total_rating[key] = -1

    total_score_list = [(k, v) for k, v in total_rating.items()]

    # sort reversely by score
    total_score_list = sorted(
        total_score_list, key=lambda tup: tup[1], reverse=True)

    cur = db.cursor()

    # get the top 30 scoring events
    result = total_score_list[0:30]
    result = [x[0] for x in result]

    final_result = []

    # filter events that are in the past
    for event_id in result:

        cur.execute("""
        SELECT e.id, e.time_start, e.tickets_left
        FROM Events e
        WHERE e.id = %s
        """, [str(event_id)])

        event = cur.fetchall()

        if not event:
            continue
        elif datetime.strptime(event[0][1], '%Y %m %d %H %M %S') > datetime.now() and int(event[0][2]) > 0:
            final_result.append(event[0][0])

    # return the 2 most recommended events
    final_result = final_result[0:2]

    return final_result


def append_ticket(email, ticket_code, seat_num, event_id, event_title, venue, start_time):
    '''
    This function adds a ticket to the database after a customer has made a booking
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT s.user_
        FROM Seats s
        WHERE s.user_ = %s AND s.seat_num = %s AND s.event_ = %s
    """, [str(email), str(seat_num), str(event_id)])

    result = cur.fetchall()
    if not result:
        is_seat_available(email, event_id, [seat_num])

    cur = db.cursor()
    cur.execute("""
        INSERT INTO Tickets
        VALUES (%s, %s, %s, %s)
    """, [str(ticket_code), str(seat_num), str(event_id), str(email)])

    db.commit()

    cur = db.cursor()

    cur.execute("""
        SELECT t.seat_num, t.event_, e.title, e.venue, e.time_start            
        FROM Tickets t
        JOIN Events e ON e.id = t.event_
        WHERE t.ticket_id = %s
    """, [str(ticket_code)])

    result = cur.fetchall()[0]

    return {
        "ticket_code": ticket_code,
        "seat_number": result[0],
        "event_id": result[1],
        "event_title": result[2],
        "location": result[3],
        "start_time": result[4]
    }


def remove_ticket(ticket_code):
    '''
    This function removes the ticket with ticket code from the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT t.event_, t.seat_num
        FROM Tickets t
        WHERE t.ticket_id = %s
    """, [str(ticket_code)])
    result = cur.fetchall()

    if not result:
        return

    event_id = result[0][0]
    seat_num = result[0][1]

    cur = db.cursor()
    cur.execute("""
        UPDATE Seats
        SET user_ = NULL
        WHERE event_ = %s AND seat_num = %s
    """, [str(event_id), str(seat_num)])

    db.commit()

    cur = db.cursor()
    cur.execute("""
        DELETE FROM Tickets
        WHERE ticket_id = %s
    """, [str(ticket_code)])

    db.commit()




def get_tickets_from_user(email):
    '''
    This function fetches all the tickets of an user
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT t.ticket_id, t.seat_num, t.event_, e.title, e.venue, e.time_start            
        FROM Tickets t
        JOIN Events e ON e.id = t.event_
        WHERE t.user_ = %s
    """, [str(email)])

    results = cur.fetchall()

    if not results:
        return []

    list_results = []
    for result in results:
        dictionary = {
            "ticket_code": result[0],
            "seat_number": result[1],
            "event_id": result[2],
            "event_title": result[3],
            "location": result[4],
            "start_time": result[5]
        }
        list_results.append(dictionary)

    return list_results



# given an event id, return the event dictionary
def get_event_with_seats(event_id):
    '''
    Given an event id, return all event information with an extra field to show the 
    available seats field for this event at this point in time
    '''

    global db

    update_prices()

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT *
        FROM Events e
        WHERE e.id = %s
    """, [str(event_id)])

    event_info = cur.fetchall()

    if not event_info:
        return {}
    event_info = event_info[0]

    cur = db.cursor()
    cur.execute("""
        SELECT s.seat_num
        FROM Seats s
        WHERE s.event_ = %s AND s.user_ IS NULL
        ORDER BY s.seat_num
    """, [str(event_id)])
    seats = cur.fetchall()

    if not seats:
        seats = []
    else:
        seats = [x[0] for x in seats]

    return {
        'event_id': event_id,
        'creator_id': event_info[1],
        'host': event_info[7],
        'event_title': event_info[2],
        'event_description': event_info[3],
        'event_type': event_info[4],
        'event_details': {
            'venue': event_info[5],
            'start_date_time': event_info[8],
            'end_date_time': event_info[9],
            'venue_type': event_info[6],
        },
        'num_tickets_available': event_info[10],
        'num_tickets_left': event_info[11],
        'ticket_price': event_info[16],
        'price_min': event_info[12],
        'price_max': event_info[13],
        # 'image': str(event_info[14]).decode(),
        'image': str(event_info[14]),
        'booked_customers': get_users_of_event(event_id),
        'available_seats': seats,
        'seating_plan_image': event_info[15],
        'reviews': get_reviews_database(event_id)
    }


def check_creator(email, event_id):
    '''
    Given an event id and an email, check if this user with this email is the 
    creator of this event. If yes, return true, else return false
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT e.creater
        FROM Events e
        WHERE e.id = %s
    """, [str(event_id)])

    result = cur.fetchall()

    if not result:
        return False
    elif result[0][0] == email:
        return True
    else:
        return False


def cancel_event_database(event_id):
    '''
    This function cancels an event with event id, which removes the event from the database
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        DELETE FROM Events
        WHERE id = %s 
    """, [str(event_id)])

    db.commit()


def get_info_event(event_id):
    '''
    This function returns the title, start time and a list of customer emails of an event
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT e.title, e.time_start
        FROM Events e
        WHERE id = %s
    """, [event_id])

    result = cur.fetchone()

    if not result:
        return {}

    return {
        "event_title": result[0],
        "event_start_time": result[1],
        "booked_customers": get_users_of_event(event_id)
    }


def read_csv_into_database():
    '''
    This function reads a csv file into the database
    '''
    
    # Get the directory of the currently executing script
    directory = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(directory, 'generated_data.csv')

    if os.path.exists(csv_path):
        print("File exists")
    else:
        print("File does not exist")
        # Create an empty DataFrame if the file doesn't exist
        df = shiong_mao.DataFrame()  
        # Save the empty DataFrame to create the file
        df.to_csv(csv_path, index=False)  

    # Load the existing generated_data.csv file
    df = shiong_mao.read_csv(csv_path)

    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    # Check if the Historical_Events table already has data
    cur.execute("SELECT COUNT(*) FROM Historical_Events;")
    result = cur.fetchone()
    if result and result[0] > 0:
        print("Historical_Events table already contains data. Skipping CSV import.")
        return

    query_start = "INSERT INTO Historical_Events (id, creator, type_, ticket_price, num_tickets_available, num_tickets_sold, host, is_online, tmp_mid, tmp_min, tmp_max, precipitation, wind_speed, actual_attendance) VALUES "
    append = ""

    for _, row in df.iterrows():
        append += "("
        append += str(row['event_id'])
        append += ", "
        append += ("'" + str(row['creator_id']) + "', ")
        append += ("'" + str(row['event_type']) + "', ")
        append += str(row['ticket_price'])
        append += ", "
        append += str(row['num_tickets_available'])
        append += ", "
        append += str(row['num_tickets_sold'])
        append += ", "
        append += ("'" + str(row['host']) + "', ")
        append += str(row['is_online'])
        append += ", "
        append += str(row['tmp_mid'])
        append += ", "
        append += str(row['tmp_min'])
        append += ", "
        append += str(row['tmp_max'])
        append += ", "
        append += str(row['precipitation'])
        append += ", "
        append += str(row['wind_speed'])
        append += ", "
        append += str(row['actual_attendance'])
        append += "), "

    append = append[:-2]
    append += ";"

    query_start += append

    cur.execute(query_start)

    db.commit()


def get_historical_events():
    '''
    This function fetches a list of events that have passed from the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT id, creator, type_, ticket_price, num_tickets_available, num_tickets_sold,
                host, is_online, tmp_mid, tmp_min, tmp_max, precipitation, wind_speed, actual_attendance                 
        FROM Historical_Events
    """)

    results = cur.fetchall()

    if not results:
        return []
    
    result_list = []
    for result in results:
        dictionary = {
            'event_id': result[0],
            'creator_id': result[1],
            'event_type': result[2],
            'ticket_price': result[3],
            'num_tickets_available': result[4],
            'num_tickets_sold': result[5],
            'host': result[6],
            'is_online': result[7],
            'tmp_mid': result[8],
            'tmp_min': result[9],
            'tmp_max': result[10],
            'precipitation': result[11],
            'wind_speed': result[12],
            'actual_attendance': result[13]
        }
        result_list.append(dictionary)
    
    return result_list


def create_historical_event_data(creator_id, event_id, event_type, ticket_price, 
                                 num_tickets_available, num_tickets_sold, host, is_online, 
                                 tmp_mid, tmp_min, tmp_max, precipitation, wind_speed, actual_attendance):
    '''
    This function stores historical events data into the Historical_Events table in the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        INSERT INTO Historical_Events
        (id, creator, type_, ticket_price, num_tickets_available, num_tickets_sold, host, is_online, tmp_mid, tmp_min, tmp_max, precipitation, wind_speed, actual_attendance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
        creator = EXCLUDED.creator,
        type_ = EXCLUDED.type_,
        ticket_price = EXCLUDED.ticket_price,
        num_tickets_available = EXCLUDED.num_tickets_available,
        num_tickets_sold = EXCLUDED.num_tickets_sold,
        host = EXCLUDED.host,
        is_online = EXCLUDED.is_online,
        tmp_mid = EXCLUDED.tmp_mid,
        tmp_min = EXCLUDED.tmp_min,
        tmp_max = EXCLUDED.tmp_max,
        precipitation = EXCLUDED.precipitation,
        wind_speed = EXCLUDED.wind_speed,
        actual_attendance = EXCLUDED.actual_attendance;
    """, [str(event_id), str(creator_id), str(event_type), str(ticket_price), str(num_tickets_available), str(num_tickets_sold), str(host), str(is_online), str(tmp_mid), str(tmp_min), str(tmp_max), str(precipitation), str(wind_speed), str(actual_attendance)])

    db.commit()

def save_event_database(event):
    '''
    This function updates the attendance data in the Historical_Events table
    '''
    
    # Check if the database connection exists, if not establish it
    if db is None:
        establish_connection()

    # Get a cursor object
    cur = db.cursor()

    # Iterate over all events and update the actual_attendance in the database
    # for event in events:
    # Execute the SQL command to update the actual_attendance for a specific event_id
    cur.execute("""
        UPDATE Historical_Events
        SET actual_attendance = %s
        WHERE id = %s;
    """, [str(event['actual_attendance']), str(event['event_id'])])


    # Commit the changes
    db.commit()


def get_reviews_database(event_id):
    '''
    This function fetches all the reviews of an event
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        SELECT  r.thread_id, r.timestamp_, r.content, r.owned_by, r.host, r.reply, r.reply_timestamp, u.first_name, u.last_name
        FROM    Reviews r
            JOIN Users u ON u.email = r.owned_by
        WHERE   r.event_ = %s
    """, [str(event_id)])

    results = cur.fetchall()

    if not results:
        return []
    
    result_list = []
    for result in results:
        if result[5] is None:
            dictionary = {
            'thread_id': int(result[0]),
            'event_id': int(event_id),
            'customer_email': result[3],
            'customer_name': result[7] + ' ' + result[8],
            'review_content': result[2],
            'time_stamp': result[1],
            'host_name': "",
            'host_reply': "",
            'host_reply_timestamp': ""
        }
        else:
            dictionary = {
                'thread_id': int(result[0]),
                'event_id': int(event_id),
                'customer_email': result[3],
                'customer_name': result[7] + ' ' + result[8],
                'review_content': result[2],
                'time_stamp': result[1],
                'host_name': result[4],
                'host_reply': result[5],
                'host_reply_timestamp': result[6]
            }
        result_list.append(dictionary)
    
    return result_list


def submit_review(thread_id, event_id, customer_email, review_content, time_stamp):
    '''
    This function stores a customer review for an event into the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        INSERT INTO Reviews
        VALUES (%s, %s, %s, %s, %s, Null, Null, Null)
    """, [str(thread_id), str(time_stamp), str(review_content), str(event_id), customer_email])

    db.commit()

def respond_to_review(thread_id, reply, reply_timestamp):
    '''
    This function saves the host reply to a review into the database 
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT u.first_name, u.last_name
        FROM    Reviews r
            JOIN Events e ON e.id = r.event_
            JOIN Users u ON u.email = e.creater
        WHERE   r.thread_id = %s
    """, [thread_id])

    name = cur.fetchone()
    if name[1] is None:
        name = name[0]
    else:
        name = name[0] + " " + name[1]

    cur.execute("""
        UPDATE  Reviews
        SET     host = %s, reply = %s, reply_timestamp = %s
        WHERE   thread_id = %s
    """, [str(name), str(reply), str(reply_timestamp), str(thread_id)])

    db.commit()


def return_user(email):
    '''
    This function fetches the information of an user, given an email
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        SELECT  u.first_name, u.last_name, t.ticket_id, t.seat_num, e.id, e.title,
                e.venue, e.time_start
        FROM    Users u
            JOIN Tickets t ON t.user_ = u.email
            JOIN Events e ON e.id = t.event_
        WHERE u.email = %s
    """, [str(email)])

    results = cur.fetchall()

    ticket_list = []
    search_term_list = []
    for result in results:
        ticket_list.append({
            'ticket_code': result[2],
            'seat_number': result[3], 
            'event_id': result[4],
            'event_title': result[5],
            'location': result[6],
            'start_time': result[7]
        })
    
    cur.execute("""
        SELECT  search_term
        FROM    Searches
        WHERE   user_ = %s
    """, [(email)])

    results1 = cur.fetchall()
    
    if results1:
        search_term_list = [x[0] for x in results1]    

    cur.execute("""
        SELECT  first_name, last_name
        FROM    Users
        WHERE   email = %s
    """, [(email)])

    result2 = cur.fetchone()

    if not result2:
        return {}


    return {
        'email': email,
        'first_name': result2[0],
        'last_name': result2[1],
        'tickets': ticket_list,
        'search_history': search_term_list
    }


def does_review_exist(email, event_id):
    '''
    This function checks whether a user has already left a review for an event. If 
    yes, return true, else return false
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        SELECT r.thread_id
        FROM Reviews r
        WHERE r.owned_by = %s AND r.event_ = %s
    """, [str(email), str(event_id)])

    result = cur.fetchone()
    
    if not result:
        return False
    
    else:
        return True



def is_user_host_db(email, event_id):
    '''
    This function checks if an user with this email is the host of an event. If yes, return
    true, else return false
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        SELECT e.id, e.creater
        FROM Events e
        WHERE creater = %s AND e.id = %s
    """, [email, str(event_id)])

    result = cur.fetchone()

    if not result:
        return False
    
    else: return True


def clean_database():
    '''
    This function clears the data in the database
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        DELETE FROM Events
    """)

    db.commit()

    cur.execute("""
        DELETE FROM Users
    """)

    db.commit()

    cur.execute("""
        DELETE FROM Historical_Events
    """)

    db.commit()


def has_user_attended_the_event_database(email, event_id):
    '''
    Given an email and event id, check if this user has attended this event
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        SELECT e.time_end, t.user_
        FROM    Events e 
            JOIN Tickets t ON t.event_ = e.id
        WHERE  e.id = %s and t.user_ = %s
    """, [event_id, email])

    result = cur.fetchone()

    if not result:
        return False
    elif datetime.strptime(result[0], '%Y %m %d %H %M %S') > datetime.now():
        return False
    elif email == result[1]:
        return True
    
    return False


def does_reply_exist(thread_id):
    '''
    This function checks if the host has already replied to a particular review, given the 
    thread id of that review
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()

    cur.execute("""
        SELECT  r.host, r.reply, r.reply_timestamp
        FROM    Reviews r
        WHERE   r.thread_id = %s
    """, [thread_id])

    result = cur.fetchone()

    if not result:
        return True

    if result[0] is None:
        return False
    elif result[0] is not None:
        return True
    else:
        return True    


def update_prices():
    '''
    This function performs dynamic pricing of events
    '''
    
    global db

    if db is None:
        establish_connection()

    time_now = datetime.now()
    time_now = time_now.strftime("%Y %m %d %H %M %S")

    cur = db.cursor()

    # fetch all events that will happen in the future
    cur.execute("""
        SELECT  id, time_start, tickets_available, tickets_left, min_price, max_price, ticket_price
        FROM    Events
        WHERE   time_start > %s
    """, [str(time_now)])

    results = cur.fetchall()

    if not results:
        return

    new_prices = []

    # calculate the new price for each ticket
    for result in results:
        # depending on how booked out the event is, the price will increase
        booked_out_ratio = (int(result[2]) - int(result[3])) / int(result[2])
        curr_price = float(result[4])
        if booked_out_ratio > 0.9:
            curr_price = float(result[5])
        elif booked_out_ratio > 0.8:
            curr_price = float(result[4]) + 0.85 * (float(result[5]) - float(result[4]))
        elif booked_out_ratio > 0.7:
            curr_price = float(result[4]) + 0.7 * (float(result[5]) - float(result[4]))
        elif booked_out_ratio > 0.5:
            curr_price = float(result[4]) + 0.5 * (float(result[5]) - float(result[4]))
        elif booked_out_ratio > 0.4:
            curr_price = float(result[4]) + 0.4 * (float(result[5]) - float(result[4]))
        else:
            curr_price = float(result[4]) + 0.3 * (float(result[5]) - float(result[4]))

        # if the event is has little demand and starts within the next 24h, apply a discount
        if datetime.strptime(result[1], '%Y %m %d %H %M %S') - datetime.strptime(time_now, '%Y %m %d %H %M %S') < timedelta(days=1) \
           and booked_out_ratio < 0.3:
            curr_price = float(result[4])
        # if the event is has moderate demand and starts within the next 24h, apply a smaller discount
        elif datetime.strptime(result[1], '%Y %m %d %H %M %S') - datetime.strptime(time_now, '%Y %m %d %H %M %S') < timedelta(days=1) \
           and booked_out_ratio < 0.8:
            curr_price = float(result[4]) + 0.3 * (float(result[5]) - float(result[4]))

        # round price
        curr_price = round(curr_price, 2)

        if curr_price != float(result[6]):
            new_prices.append((result[0], curr_price))

    # update all events' prices that changed
    for tuples in new_prices:
        cur.execute("""
            UPDATE Events
            SET ticket_price = %s
            WHERE id = %s
        """, [str(tuples[1]), str(tuples[0])])

        db.commit()


def new_sales_stats(event_id, timestamp):
    '''
    This function creates a new sales stats data table in the database for an event
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT  tickets_available, tickets_left
        FROM    Events
        WHERE   id = %s
    """, [str(event_id)])

    result = cur.fetchone()

    if not result:
        return
    
    cur.execute("""
        INSERT INTO Sales_Stats
        VALUES (%s, 1, %s, -999999, %s, %s, -999999), (%s, 2, %s, -999999, %s, %s, -999999),
               (%s, 3, %s, -999999, %s, %s, -999999)
    """, [str(event_id), str(result[0]), str(result[0]), str(timestamp),
          str(event_id), str(result[0]), str(result[0]), str(timestamp),
          str(event_id), str(result[0]), str(result[0]), str(timestamp)])

    db.commit()


def update_sales_stats(event_id, time_id, tickets_sold, num_tickets_left):
    '''
    This function updates the number of tickets sold and number of tickets left fields
    for an event for a particular time period
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        UPDATE  Sales_Stats
        SET     tickets_sold = %s, num_tickets_left = %s
        WHERE   event_id = %s AND time_id = %s
    """, [str(tickets_sold), str(num_tickets_left), str(event_id), str(time_id)])

    db.commit()


def fetch_sales_stats(event_id):
    '''
    This function fetches data from the sales stats table for an event
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT  s.time_id, s.available_tickets, s.tickets_sold, s.num_tickets_left, s.timestamp_, s.prediction
        FROM    Sales_Stats s
        WHERE   event_id = %s
    """, [str(event_id)])

    results = cur.fetchall()

    if not results:
        return []
    
    stats = []
    for result in results:
        dictionary = {
            'event_id': int(event_id),
            'time_id': int(result[0]),
            'available_tickets': int(result[1]),
            'tickets_sold': int(result[2]),
            'num_tickets_left': int(result[3]),
            'timestamp': result[4],
            'prediction': int(result[5])
        }
        stats.append(dictionary)
    
    return stats


def sales_stats_tickets_sold(event_id, time_id):
    '''
    This function fetches the number of tickets sold for an event during a time period
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT  tickets_sold
        FROM    Sales_Stats
        WHERE   event_id = %s AND time_id = %s
    """, [str(event_id), str(time_id)])

    result = cur.fetchone()

    if not result:
        return -999999
    else:
        return result[0]


def check_num_tickets_sold(event_id, time_id):
    '''
    Given an event id, check in its sales stats table for the number of tickets sold for
    a particular time period
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT  tickets_sold
        FROM    Sales_Stats
        WHERE   event_id = %s AND time_id = %s
    """, [str(event_id), str(time_id)])

    result = cur.fetchone()

    if not result:
        return False
    elif result[0] == -999999:
        return False
    else: return True


def update_prediction_db(event_id, time_id, prediction):
    '''
    This function updates the prediction field in the sales stats table for an event
    for a particular time period
    '''
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        UPDATE  Sales_Stats
        SET     prediction = %s
        WHERE   event_id = %s AND time_id = %s
    """, [str(prediction), str(event_id), str(time_id)])

    db.commit()


def is_prediction_there_db(event_id, time_id):
    '''
    This function checks whether the prediction field in the sales stats table for this event
    has already been updated for a particular time period. if yes, return true, else return
    false
    '''    
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT  prediction
        FROM    Sales_Stats
        WHERE   event_id = %s AND time_id = %s
    """, [str(event_id), str(time_id)])

    result = cur.fetchone()

    if not result:
        return False
    elif result[0] == -999999:
        return False
    else:
        return True


def give_stored_prediction_db(event_id, time_id):
    '''
    This function returns the field prediction for an event in its sales stats table for a
    particular time period
    '''
    
    global db

    if db is None:
        establish_connection()

    cur = db.cursor()
    cur.execute("""
        SELECT  prediction
        FROM    Sales_Stats
        WHERE   event_id = %s AND time_id = %s
    """, [str(event_id), str(time_id)])

    result = cur.fetchone()

    if not result:
        return None
    else:
        return result[0]




if __name__ == '__main__':
    # some test code to test the above functions 
    
    
    add_account_to_database("abc@gmail.com", "1234567890", "John", "Smith", "1234567812345678",
                            "123", "John Smith", "01", "2025")

    add_account_to_database("adc@gmail.com", "1234567890", "John", "Smith", "1234567812345678",
                            "123", "John Smith", "01", "2025")
    add_account_to_database("abc@gmail.com", "1234567890", "John", "Smith", "1234567812345678",
                            "123", "John Smith", "01", "2025")


    #create_data_with_weather("abc@gmail.com", "1", "music", 120, 50, 10, "host", "InPerson", 1, 2.0, 3, 12, 20)
    #create_data_with_weather("abc@gmail.com", "2", "music", 120, 50, 10, "host", "InPerson", 1, 2.0, 3, 12, 20)

    #print(get_events_with_weather()[-10:])
    
    add_event_to_database("1", "abc@gmail.com", "Max Concert", "Chill at a music festival", "music", "Sydney",
                          "InPerson", "abc", "2023 08 23 10 30 12", "2023 08 23 10 32 15", 12, 12, 0, 10, None, 12, None)
    
    add_event_to_database("2", "adc@gmail.com", "Festival of the Decade", "Hard Rock only", "music", "Sydney",
                          "Online", "Max", "2023 08 23 10 30 12", "2023 08 23 10 32 15", 100, 29, 0, 10, None, 100, None)
    add_event_to_database("3", "abc@gmail.com", "Max new Concert", "Chilling", "music", "Melbourne",
                          "Online", "Max", "2023 08 23 10 30 12", "2023 08 23 10 32 15", 5, 5, 0, 11, None, 5, None)
    
    new_sales_stats(1, "2023 08 23 10 30 12")
    new_sales_stats(2, "2023 08 23 10 30 12")

    update_sales_stats(1, 1, 5, 7)
    update_sales_stats(2, 2, 3, 100)

    print(fetch_sales_stats(1))
    print(fetch_sales_stats(2))

    print(sales_stats_tickets_sold(1, 1))
    print(sales_stats_tickets_sold(2, 1))

    print(check_num_tickets_sold(1, 1))
    print(check_num_tickets_sold(1, 2))

    update_prediction(1, 1, 10)
    update_prediction(2, 1, 5)

    print(is_prediction_there(1, 1))
    print(is_prediction_there(1, 2))

    print(give_stored_prediction(1, 1))
    print(give_stored_prediction(1, 2))




    # new_sales_stats(1, 12345678)
    # new_sales_stats(2, 12345678)

    # print(fetch_sales_stats(1))

    # update_sales_stats(1, 1, 10, 2, 11111)
    
    # print(fetch_sales_stats(1))
    # print(fetch_sales_stats(2))

    # update_prices()

    # print(get_info_event(1))
    # is_seat_available("adc@gmail.com", "1", [1, 2])

    # print(get_tickets_from_user("adc@gmail.com"))
    # print(get_event_with_seats(1))


    '''
    print(fetch_events())

    append_ticket("adc@gmail.com", "aaa", 1, 1, None, None, None)
    append_ticket("abc@gmail.com", "bbb", 2, 1, None, None, None)
    decrement_tickets(1, 2)
    # print(get_event_with_seats(1))
    print(fetch_events())
    append_ticket("adc@gmail.com", "ccc", 3, 1, None, None, None)
    append_ticket("adc@gmail.com", "ccd", 4, 1, None, None, None)
    append_ticket("adc@gmail.com", "caa", 5, 1, None, None, None)
    append_ticket("abc@gmail.com", "abb", 6, 1, None, None, None)
    decrement_tickets(1, 4)
    # print(get_event_with_seats(1))
    print(fetch_events())
    append_ticket("adc@gmail.com", "cbc", 7, 1, None, None, None)
    append_ticket("adc@gmail.com", "cbd", 8, 1, None, None, None)
    decrement_tickets(1, 2)
    # print(get_event_with_seats(1))
    print(fetch_events())
    '''
    
    
    '''
    submit_review(1, 1, 'adc@gmail.com', "Great event", None)
    submit_review(2, 1, 'abc@gmail.com', "Shitty event", None)

    respond_to_review(2, "get stuffed", None)

    clean_database()
    '''
    '''
    print(return_user("adc@gmail.com"))

    print(does_review_exist("adc@gmail.com", 1))
    print(does_review_exist("adc@gmail.com", 2))
    print(does_review_exist("aaa", 1))

    print(is_user_host("abc@gmail.com", 1))
    print(is_user_host("abc@gmail.com", 2))
    print(is_user_host("abc@gmail.com", 4))
    print(is_user_host("aaa@gmail.com", 1))

    print(get_reviews_database(1))
    print(get_reviews_database(2))
    print(get_reviews_database(5))
    '''

    # print(get_info_event(1))
    # print(get_event_with_seats(1))
    # cancel_event(1)

    # print(get_tickets_from_user("adc@gmail.com"))

    # remove_ticket("aaa")
    # remove_ticket("ddd")
    # is_seat_available("adc@gmail.com", "1", [3, 2])

    # print(give_recommendations("adc@gmail.com"))
    # return_events_of_user("abc@gmail.com")

    # print(get_num_rows_seats("1"))
    # print(cancel_booking("abc@gmail.com", 1, 1))
    # print(return_events_of_user("abc@gmail.com"))

    # print(cancel_booking("abc@gmail.com", "1", "1", "1"))
    # print(get_users_of_event("1"))
    # print(return_events_of_user("abc@gmail.com"))
    # print(get_searches("abc@gmail.com"))
    # commit_search("adc@gmail.com", "01 01 2001 12 30", "Max Concert")
    # print(get_searches("abc@gmail.com"))
    # commit_search("abc@gmail.com", "01 01 2002 12 30", "Botan Concert")
    # print(get_searches("abc@gmail.com"))
    # print(give_recommendations("adc@gmail.com"))
    # fetch_events()
    '''
    print(password_match("abc@gmail.com", "1234567890"))
    print(password_match("abc@gmail.com", 1234567890))
    print(password_match("abc@gmail.com", "password"))

    change_password_in_database("adc@gmail.com", "0123456789")
    '''
    db.close()
