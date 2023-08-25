'''
This file contains functions to perform ticket booking, ticket cancellation and seat picking
'''

import random
from datetime import datetime, timedelta
from .auth import auth_register, auth_login
from .event import create_event, get_event_database
from .data import users, events, event_seats_list, db_state
from .errors import InputError, AccessError
from .helper_functions import check_valid_token, send_email_helper, get_email_from_token
from .hash import encode_jwt
from .data_helper import is_seat_available, give_free_seats, append_ticket, decrement_tickets, \
                        get_tickets_from_user, remove_ticket, increment_tickets


SECRET = "HelloWorld2023"
GENERATE_TICKET_ID = 1
SYSTEM_EMAIL = "pomipomi2023@gmail.com"
EMAIL_PASSWORD = "zlpwyjaxbmfgsvfp"
EMAIL_SUBJECT = 'Your tickets for your event booking'


def generate_ticket_code(num_tickets):
    '''
    Given the number of tickets, generate these many unique ticket codes and return
    the ticket codes in as a list
    '''

    ticket_codes = []
    
    i = 1
    # the ticket code is encoded using a randomly generated number and the timestamp
    while i <= num_tickets:
        secret_code = {
            'num': random.random(),
            'timestamp': (datetime.now()).timestamp()
        }
        secret_code = encode_jwt(secret_code, SECRET)
        ticket_codes.append(secret_code[-10:])
        i += 1
    
    return ticket_codes

def book_ticket(token, event_id, num_tickets_to_purchase, requested_seats):
    '''
    Given a token, purchase a certain number of tickets for an event with event_id
    Return a list of tickets with ticket details such as seat number, ticket code, etc
    
    Note: requested_seats is a list of seat numbers desired to be booked
    '''
    
    # Only registered users can buy tickets
    if not check_valid_token(token):
        raise AccessError(description='Invalid token')

    valid_event = False
    event_title = ''
    venue = ''
    start_time = ''

    num_tickets_to_purchase = int(num_tickets_to_purchase)
    event_id = int(event_id)

    # get event details which will be used to populate the ticket dictionary
    for event in events:
        if int(event['event_id']) == int(event_id):
            valid_event = True
            event_title = event['event_title']
            venue = event['event_details']['venue']
            start_time = event['event_details']['start_date_time']
    
    if not valid_event:
        raise InputError(description='Event does not exist!')

    # number of tickets to purchase has to equal the number of seats that the user's picking
    if num_tickets_to_purchase != len(requested_seats):
        raise InputError(description='You are not picking the same number of seats as your number of tickets!')
    
    return_tickets = []
    ticket_codes = []

    user_email = get_email_from_token(token)

    # Book the seats
    if pick_seat(event_id, requested_seats) == True:
         ticket_codes = generate_ticket_code(num_tickets_to_purchase)
    else: 
        raise InputError(description='Sorry, a seat you picked is invalid.')
    
    if db_state:
        if is_seat_available(user_email, event_id, requested_seats):
            # generate tickets and append to return_tickets
            ticket_codes = generate_ticket_code(num_tickets_to_purchase)
        else: 
            raise InputError(description='Sorry, a seat you picked is invalid.')
    
    i = 0
    while i < num_tickets_to_purchase:
        new_ticket = {
            'ticket_code': ticket_codes[i],
            'seat_number': requested_seats[i],
            'event_id': event_id,
            'event_title': event_title,
            'location': venue,
            'start_time': start_time,
        }
        
        return_tickets.append(new_ticket)
        
        # # add the ticket to user account
        if db_state:
            append_ticket(user_email, ticket_codes[i], requested_seats[i], event_id, event_title, venue, start_time)


        for user in users:
            if user['login']['email'] == user_email:
                user['tickets'].append(new_ticket)

        i += 1
    
    # decrement the number of tickets left for the event
    for event in events:
        if event['event_id'] == event_id:
            event['num_tickets_left'] = int(event['num_tickets_left']) - num_tickets_to_purchase
            # add this customer to the event's list of customers
            if user_email not in event['booked_customers']:
                event['booked_customers'].append(user_email)
    
    # check if there are enough tickets left 
    if db_state:
        if not decrement_tickets(event_id, num_tickets_to_purchase):
            raise InputError(description="Not enough tickets")
    
    # send a confirmation email to the user with tickets
    send_confirmation_email(user_email, return_tickets, event_title)

    return return_tickets

def send_confirmation_email(email, tickets, event_title):
    '''
    This function sends a booking confirmation email to the customer. If the 
    booking is successful, the customer will receive an email with ticket
    details
    '''
    
    email_subject = "Your tickets for your event booking"
    confirmation_message = "Thank you for booking an event with us! Your details for your event booking "
    confirmation_message += "is as follows: \n\n"

    i = 0
    while i < len(tickets):
        confirmation_message += "Ticket " + str(i+1) + "\n"
        confirmation_message += "Event title: " + tickets[i]['event_title'] + "\n"
        
        start_time = tickets[i]['start_time']
        start_list = list(start_time)
        start_list[4] = "-"
        start_list[7] = "-"
        start_list[13] = ":"
        start_list[16] = ":"
        start_time = ''.join(start_list)
        confirmation_message += "Start time: " + start_time + "\n"
        
        confirmation_message += "Event location: " + tickets[i]['location'] + "\n"

        confirmation_message += "Ticket code: " + tickets[i]['ticket_code'] + "\n"
        
        confirmation_message += "Seat number: " + str(tickets[i]['seat_number']) + "\n\n"


        i += 1

    confirmation_message += "We hope you enjoy your event!"
    
    # send the confirmation email to the user
    send_email_helper(email, confirmation_message, email_subject)
    

def pick_seat(event_id, requested_seats):
    '''
    Given an event id and a listed of requested seat numbers, book the user in for those
    seats if the seats are available. If multiple seats are picked and one of the seats 
    is not available, the whole book_ticket process is aborted
    
    Note: the parameter requested_seats is a listed of seat numbers
    '''

    global event_seats_list
    
    is_successful = False
    event_found = False
    
    event_list = get_event_database()

    for event in event_list:
        if event['event_id'] == event_id:
            event_found = True
            event_id = event['event_id']

    # can only book for valid events
    if event_found == False:
        raise InputError(description='Event does not exist!')

    # raise error when users try to book an invalid seat number
    for desired_seat in requested_seats:
        for event in events:
            if event['event_id'] == event_id:
                if desired_seat > event['number_of_seats']:
                    raise InputError(description='Sorry, a seat you picked is invalid.')
    
    # check if all of the requested seats are available. if any of them is not available, 
    # raise an error
    for desired_seat in requested_seats:
        for s in event_seats_list:
            if s['event_id'] == event_id:
                if desired_seat not in s['event_seats']:
                    raise InputError(description='Sorry, a seat you picked is already taken.')
    
    # if no error raised, is_successful = true as all requested seats are available
    is_successful = True
    
    # book the user in for this seat:
    # remove this seat from the seat list as it has been booked
    for booked_seat in requested_seats:
        for s in event_seats_list:
            if s['event_id'] == event_id:
                s['event_seats'].remove(booked_seat)
    
    return is_successful

def list_available_seats(event_id):
    '''
    Given an event id, return a list of all available seats (that is, the seat number)
    '''
    
    available_seats = []

    for seat in event_seats_list:
        if int(seat['event_id']) == int(event_id):
            available_seats = seat['event_seats']
    
    if db_state:
        # get the list of available seat numbers
        available_seats_db = give_free_seats(event_id)
        available_seats_db.sort()
        return available_seats_db
    else:
        available_seats.sort()
        sorted_list = available_seats
        return available_seats


def get_event_and_seats_by_id_fixed(event_id):
    '''
    Given an event id, return all the available seats of this event, as well as all 
    the event details
    '''
    
    # fetch all the events
    if db_state == True:
        all_events = get_event_database()
    else:
        all_events = events
    
    return_events = []
    
    for event in all_events:
        event_start_datetime = datetime.strptime(event['event_details']['start_date_time'], '%Y %m %d %H %M %S')

        return_events.append(event)
    
    for_frontend = {}

    # keep the details of this event
    for event in return_events:
        if int(event['event_id']) == int(event_id):
            for_frontend = event
            break

    available_seats = []
    
    for seat in event_seats_list:
        if int(seat['event_id']) == int(event_id):
            # get the list of available seats information
            available_seats = list_available_seats(event_id)

    # add the seats details to the dictionary to be returned
    for_frontend['available_seats'] = available_seats

    return for_frontend


def cancel_booking(token, event_id, ticket_code):
    '''
    Users can cancel their booking for an event by providing the event id and ticket code.
    The booking can only be cancelled if the event is scheduled to occur at least 7 days
    into the future. When a customer cancels an booking, the customer is removed from the
    customer list for the event if the customer has no more tickets booked with this 
    event. Only 1 ticket can be cancelled at a time
    '''
    
    global users, events, event_seats_list
    
    # Only registered and logged-in users can cancel bookings
    if not check_valid_token(token):
        raise AccessError(description='Invalid token')
    
    user_email = get_email_from_token(token)
    
    ticket_found = False
    
    event_start_time = ''
    if db_state:
        user_tickets = get_tickets_from_user(user_email)

    # Verify the validity of ticket code and obtain the event start time
    for user in users:
        if user['login']['email'] == user_email:
            for ticket in user['tickets']:
                if ticket['event_id'] == event_id:
                    event_start_time = ticket['start_time']
                    ticket_found = True

    if db_state:
        for ticket in user_tickets:
            if ticket['event_id'] == event_id:
                event_start_time = ticket['start_time']
                ticket_found = True

    # if user has not booked a ticket for this event, raise error
    if ticket_found == False:
        raise AccessError(description='Sorry, you have not booked a ticket for this event!')
    
    event_start_datetime = datetime.strptime(event_start_time, '%Y %m %d %H %M %S')
    
    # if user tries to cancel booking for an event that has already started, raise error
    if event_start_datetime <= datetime.now():
                raise InputError(description='Sorry, you cannot cancel a booking for an event that has started!')
    
    # users can only cancel an event if it's happening at least 7 days from now
    if datetime.now() + timedelta(days = 7) > event_start_datetime:
        raise InputError(description='Sorry, you can only cancel booking for an event that is happening at least 7 days away.')
    
    # if all checks are passed, cancel the booking for the customer: remove this ticket 
    # with ticket code from user account
    seat_num = -1
    
    any_more_tickets = False
    ticket_list_copy = []
    
    if db_state:
        # cancel booking, free ticket spot
        remove_ticket(ticket_code)
        increment_tickets(event_id, 1)

    for user in users:
        if user['login']['email'] == user_email:
            ticket_list_copy = user['tickets']
            for ticket in user['tickets']:
                if ticket['ticket_code'] == ticket_code:
                    # remove this ticket from users' ticket list
                    user['tickets'].remove(ticket)
                    seat_num = ticket['seat_number']
    
    # since customers can only cancel one ticket at a time, we need to check if this customer 
    # has anymore tickets associated with this event. if yes, then the user is still a customer
    # of the event so should not be removed from the customer list.
    # for example, a customer can book 2 tickets for an event but decides to cancel one ticket
    i = 0
    for ticket in ticket_list_copy:
        if ticket['event_id'] == event_id:
            i += 1
    if i > 0:
        any_more_tickets = True
    
    for ticket in ticket_list_copy:
        if ticket['event_id'] == event_id:
            any_more_tickets = True
    
    for event in events:
        if event['event_id'] == event_id:
            # remove this customer from the customer list, if the customer has no more tickets belonging to this event
            if any_more_tickets == False:
                event['booked_customers'].remove(user_email)
            # increment the number of tickets left
            event['num_tickets_left'] = event['num_tickets_left'] + 1
            for seat in event_seats_list:
                if seat['event_id'] == event_id:
                    # free up the seat for other customers
                    seat['event_seats'].append(seat_num) 
                    
    return {}


if __name__ == '__main__':
    # some code for testing the above functions
    
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    # Create second user
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")

    # Create first event. This should have event id of 1
    create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2018 09 15 12 30 12", "2018 09 15 12 45 12", 10, 10, 10, 10, 40, "concert hall photo", 10, "seats image")

    # Create second event. This should have event id of 2
    create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, "seats image")
    
    # event 3
    create_event(login_success['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                  "POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    # event 4 is happening in the future
    create_event(login_success['token'], "another event", "one more event", "Sports & Fitness", "Olympic Park", "Olympic Park",
                 "POMI soccer team", "2025 09 15 16 30 12", "2025 09 15 16 35 12", 3, 3, 20, 20, 50, "sports hall photo", 3, "seats image 2")
    
    # user 1 books for events 1, 2, 4. attended events should be 1, 2
    booking = book_ticket(login_success['token'], 1, 2, [3, 5])
    #booking2 = book_ticket(login_success['token'], 1, 1, [5])
    booking2_2 = book_ticket(login_success['token'], 1, 2, [1, 2])

    # user 2 books for events 2, 3, 4. attended events should be 2, 3. 
    booking3 = book_ticket(login_success2['token'], 2, 1, [9])
    booking4 = book_ticket(login_success2['token'], 3, 1, [20])
    booking4 = book_ticket(login_success2['token'], 4, 1, [3])
    
    '''
    print("attended events of user 1: ============================")
    print(attended_events_list(login_success['token']))
    
    print("attended events of user 2: ============================")
    print(attended_events_list(login_success2['token']))
    
    

    event_booked = user_tickets_booked("luyapan1202@gmail.com")
    print("FUTURE tickets")
    print(event_booked)
    
    print("PAST tickets")
    print(user_tickets_booked_past("luyapan1202@gmail.com"))
    '''
    # print("list of all events:")
    # print(get_event_database())

    # cancel_event(login_success['token'], 2)
    # print(get_event_database())

    # cancel_event(login_success['token'], 1)
    # print(get_event_database())

    # booking3 = book_ticket(login_success2['token'], 1, 1, [10])
    # booking2 = book_ticket(login_success['token'], 2, 1, [2])

    # booking4 = book_ticket(login_success2['token'], 2, 1, [1])

    # booking3 = book_ticket(login_success2['token'], 1, 1, [2])

    # cancel_event(login_success['token'], 1)
    # cancel_event(login_success['token'], 2)

    # print("Event list after cancellation")
    # print(get_event_list())
    #HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
    
    # print(get_users_of_event(1))
    # print(get_users_of_event(2))
    
    #print(list_available_seats(1))
    
    # print("-------> before: ")
    # for event in events:
    #     print(event['booked_customers'])
    
    #book_ticket(login_success2['token'], 2, 2, [5, 6])
    
    # cancel_booking(login_success['token'], 1, booking[1]['ticket_code'])
    # cancel_booking(login_success['token'], 1, booking[0]['ticket_code'])
    #cancel_booking(login_success['token'], 1, booking3[0]['ticket_code'])
    #cancel_booking(login_success2['token'], 2, booking2[0]['ticket_code'])
    '''
    print("-------> after: ")
    for event in events:
        print(event['booked_customers'])
    
    
    
    # cancel event test code below:
    
    """book_ticket(login_success['token'], 1, 2, [1, 2])    
    # book ticket for event 2 , book seats 1, 2, 20
    print(book_ticket(login_success['token'], 1, 1, [1000]))
    # book_ticket(login_success2['token'], 2, 2, [5, 6])
    
    '''
    '''
    print("----> initial ticket list for users:")
    for user in users:
        print(user['tickets'])

    
    # Host to cancel event 2
    cancel_event(login_success['token'], 2)
    '''
    '''
    #print("---> event list after cancellation:")
    #print(events)
    '''
    '''
    print("----> ticket list for users after cancellation:")
    for user in users:
    print(user['tickets'])
    '''
    
    """# print out all tickets the user has
    for user in users:
        if user['login']['email'] == 'luyapan1202@gmail.com':
            print("all tickets for this user:::")
            print(user['tickets'])
    # for each event, now print their remaining seats
    print(list_available_seats(1))
    print(list_available_seats(2))
    
    for event in events:
        print("customer list:")
        print(event['booked_customers'])
        """
        #if event['event_id'] == 1:
        #print(event['num_tickets_left'])
    
    # this raises an error because seat 1 is already taken
    # book_ticket(login_success['token'], 1, 1, [1])
    
    """
    # book for seat 9 of event 1 should return true
    print(pick_seat(1, [9]))
    # book for seats 1, 10, should return true
    print(pick_seat(1, [1, 10]))
    
    # this should now raise an error because seat 9 is already taken
    # print(pick_seat(1, [9]))
    
    print(generate_ticket_code(5))
    """
    