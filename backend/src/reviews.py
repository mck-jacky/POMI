'''
This file contains functions to post reviews and reply to reviews
'''

from .data import users, events, db_state
from .helper_functions import get_email_from_token
from .event import attended_events_list
from .errors import InputError, AccessError
from datetime import datetime
from .auth import auth_register, auth_login
from .event import create_event, get_event_database
from .booking import book_ticket
from .data_helper import get_users_of_event, has_user_attended_the_event_database, does_review_exist, submit_review, \
                        is_user_host_db, respond_to_review, get_reviews_database, does_reply_exist

GENERATE_THREAD_ID = 1

def post_review(token, event_id, review_content):
    '''
    This function is called by customers to review an event only. Given a token, event_id and
    the review string, append the review to the event
    
    This function does not have a return value
    '''
    global GENERATE_THREAD_ID, events, users
    
    event_id = int(event_id)

    user_email = get_email_from_token(token)
    
    # Only customers are able to leave reviews for an event
    if not is_user_customer(user_email, event_id):
        raise AccessError(description='Sorry, you do not have the permission to leave a review for this event.')

    # Can only post the review if the user has already attended the event
    if has_user_attended_event(token, event_id) == True:
        
        # each user can only comment once
        if has_commented(user_email, event_id) == True:
            raise AccessError(description='Sorry, you can only leave one review for an event.')
        
        else: 
            # get event id, host name
            # get customer first and last name
            host_name = ''
            
            cust_first_name = ''
            cust_last_name = ''
            
            for event in events:
                if event['event_id'] == event_id:
                    host_name = event['host']
            
            for user in users:
                if user['login']['email'] == user_email:
                    cust_first_name = user['name_first']
                    cust_last_name = user['name_last']
            
            user_name = cust_first_name + ' ' + cust_last_name
            
            time_stamp = str(datetime.now().timestamp())
            
            # populate the reviews dictionary with available data
            review = {
                'thread_id': GENERATE_THREAD_ID,
                'event_id': event_id,
                'customer_email': user_email,
                'customer_name': user_name,
                'review_content': review_content,
                'time_stamp': time_stamp,
                'host_name': host_name,
                'host_reply': "",
                'host_reply_timestamp': "",
            }

            # post the review
            for event in events:
                if event['event_id'] == event_id:
                    event['reviews'].append(review)

            if db_state:
                submit_review(GENERATE_THREAD_ID, event_id, user_email, review_content, time_stamp)

            GENERATE_THREAD_ID += 1
        
    else:
        # if an event has not started, no one can post reviews to it
        raise AccessError(description='Sorry, you cannot post reviews to an unstarted event!')
    
    return {
        'thread_id': review['thread_id'],
        'event_id': event_id
    }


def has_user_attended_event(token, event_id):
    '''
    Given an event id, return a boolean to tell if the user has attended this event.
    If the user has attended the event, return true. Otherwise return false
    '''
    
    attended = False
    
    if not db_state:
        attended_events = attended_events_list(token)
        for event in attended_events:
            if event['event_id'] == event_id:
                attended = True

    else:
        user_email = get_email_from_token(token)
        attended = has_user_attended_the_event_database(user_email, event_id)
    
    return attended


def is_user_customer(email, event_id):
    '''
    Given an event id, check if the user with this email is a customer of the event
    '''

    is_customer = False
    customer_list = []
    
    if db_state == False:
        for event in events:
            if event['event_id'] == event_id:
                customer_list = event['booked_customers']
    
    else:
        customer_list = get_users_of_event(event_id)
    
    # find this user in the list of customers. if not found, return false, 
    # if found, return true
    for customer_email in customer_list:
            if customer_email == email:
                is_customer = True
    
    return is_customer

def has_commented(email, event_id):
    '''
    Given user email and event_id, return true if user has already left a review for this event
    '''
    
    has_commented = False
    
    review_list = []
    
    if not db_state:
        for event in events:
            if event['event_id'] == event_id:
                review_list = event['reviews']
        
        for review in review_list:
            if review['customer_email'] == email:
                has_commented = True
    
    else:
        # check if the user has already left a review for this event
        has_commented = does_review_exist(email, event_id)

    return has_commented

def reply_review(thread_id, email, event_id, reply_content):
    '''
    Given a thread id, event id, email of user and reply content string, reply to a review.
    Only the host of an event can call this function to reply to customer reviews
    '''
    
    event_id = int(event_id)

    # check if user is the host of this event. if not, raise error
    if is_host_of_event(email, event_id) == False:
        raise AccessError(description='Sorry, only hosts can reply to reviews!')
    
    reply_timestamp = str(datetime.now().timestamp())


    # if user is the host of this event, post their reply
    if db_state:
        # host can only reply to each once. if host already replied to a review, raise error
        if does_reply_exist(thread_id) == True:
            raise InputError(description='Sorry, you can only reply once!')
        respond_to_review(thread_id, reply_content, reply_timestamp)
    
    else: 
        for event in events:
            if event['event_id'] == event_id:
                for thread in event['reviews']:
                    if thread['thread_id'] == thread_id:
                        # hosts cannot reply a second time
                        if thread['host_reply'] != '':
                            raise InputError(description='Sorry, you can only reply once!')

                        thread['host_reply'] = reply_content
                        thread['host_reply_timestamp'] = reply_timestamp

    return {}

def is_host_of_event(email, event_id):
    '''
    Returns true if user with this email is a host of the event
    '''
    
    is_host_of_event = False
    
    if db_state:
        is_host_of_event = is_user_host_db(email, event_id)
    
    else:
        for event in events:
            if int(event['event_id']) == int(event_id):
                if event['creator_id'] == email:
                    is_host_of_event = True
                    
    return is_host_of_event

def get_reviews_of_event(event_id):
    '''
    Given an event id, return all reviews of this event
    '''
    # return reviews from the db as a list of dictionaries
    reviews_list = []

    event_id = int(event_id)

    if db_state:
        reviews_list = get_reviews_database(event_id)
    else: 
        for event in events:
            if event['event_id'] == event_id:
                reviews_list = event['reviews']
    
    return reviews_list




if __name__ == '__main__':
    # some driver code to test the above functions
    
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    # Create first event
    create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    create_event(login_success2['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, "seats image")
    
    book_ticket(login_success['token'], 1, 1, [3])
    book_ticket(login_success2['token'], 2, 1, [10])
    book_ticket(login_success2['token'], 1, 1, [1])
    
    print("has user attended event:")
    print(has_user_attended_event(login_success['token'], 1))
    print(has_user_attended_event(login_success2['token'], 1))
    print(has_user_attended_event(login_success2['token'], 2))
    
    # test post review function
    # before posting reviews:   
    print("Before any reviews:")
    print(get_event_database())
    
    # post a review
    
    post_review(login_success['token'], 1, "Really loved the repertoire")
    print("post first review: =======")
    print(get_event_database())
    
    post_review(login_success2['token'], 2, "Lah lah lah")
    print("post second review: =======")
    print(get_event_database())
    
    # user 2 comments on event 1
    thread_3 = post_review(login_success2['token'], 1, "3333333333")['thread_id']
    print("post third review: =======")
    print(get_event_database())
    
    # try testing host reply to event 1
    reply_review(1, "luyapan1202@gmail.com", 1, "Thank you!!!------")
    print("post reply: =======")
    print(get_event_database())
    
    # try testing host reply to event 2
    reply_review(2, "scanlulu@gmail.com", 2, "--->>> host's reply here")
    print("post reply 2: =======")
    print(get_event_database())
    
    reply_review(thread_3, "luyapan1202@gmail.com", 1, ">>>>>>>>> the reply")
    print("post reply 3: =======")
    print(get_event_database())
    
    print("Reviews of event 1: <><><><><><><><><><><><><><><><><><><><><><>")
    print(get_reviews_of_event(1))
    
    print("Reviews of event 2: <><><><><><><><><><><><><><><><><><><><><><>")
    print(get_reviews_of_event(2))
    
    
    # test case: 1. not host of event but trying to reply to a review
    # 2. host successfully replying to a review
    