'''
This file contains a function to communicate with customer through broadcasts
'''

from .helper_functions import get_email_from_token, send_email_helper
from .data import events, db_state
from .errors import InputError, AccessError
from .auth import auth_register, auth_login
from .event import create_event
from .booking import book_ticket
from .data_helper import get_users_of_event, check_creator


def broadcast_to_customer(token, event_id, message, email_subject):
    '''
    This function allows the host to broadcast a message to all of its booked 
    customers for an event. The host needs to enter a message and email subject. 
    None of these two fields can be empty. Only the host of an event is allowed
    to use this function
    '''
    
    # extract user email from the token
    user_email = get_email_from_token(token)
    
    success = False
    
    event_valid = False
    
    my_event = {}
    
    # check if the user is a host. only a host can broadcast a message to all
    # the customers
    for event in events:
        if int(event['event_id']) == int(event_id):
            event_valid = True
            my_event = event
            if event['creator_id'] != user_email:
                raise AccessError(description='Sorry, you do not have the right to make changes to the event.')
    
    if event_valid == False:
        raise InputError(description='Sorry, the event you are looking for is invalid.')
    
    # obtain the email list of all booked customers
    customer_email_list = my_event['booked_customers']

    if db_state:
        if not check_creator(user_email, event_id):
            raise AccessError(
                description='Sorry, you do not have the right to manage this event!')

        customer_email_list = get_users_of_event(event_id)

    # None of the email subjects and messages can be empty
    if email_subject == '' or email_subject == ' ':
        raise InputError(
                description='Sorry, email subject cannot be empty!')

    if message == '' or message == ' ':
        raise InputError(
                description='Sorry, email body cannot be empty!')

    # broadcast the message to all booked customers
    for cust_email in customer_email_list:
        send_email_helper(cust_email, message, email_subject)
    
    success = True
    return_broadcast_msg = "Broadcast message sent successfully."
    
    return {"success": success, "message": str(return_broadcast_msg)}


if __name__ == '__main__':
    # some driver code to test the above function
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    # Create second user
    registration2 = auth_register("luya.pan@student.unsw.edu.au", "hahaha", "Peter", "Pan",
                                 "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("luya.pan@student.unsw.edu.au", "hahaha")

    # Create first event. This should have event id of 1
    create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2023 09 15 12 30", "2023 09 15 12 45", 10, 10, 35.5, "concert hall photo", 10, "seats image")

    create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2023 12 15 12 15", "2023 12 15 12 20", 80, 80, 0.0, "church hall photo", 80, "seats image")

    book_ticket(login_success['token'], 1, 2, [1, 5])
    book_ticket(login_success2['token'], 1, 2, [2, 3])
    
    book_ticket(login_success['token'], 2, 3, [9, 7, 10])
    
    # book_ticket(login_success2['token'], 2, 1, [80])
    
    broadcast_to_customer(login_success['token'], 1, "hi here's a creepy message from your host", "HELLO")
    broadcast_to_customer(login_success['token'], 2, "haahahahahhahha merry xmas", "HAHAHA email subject")