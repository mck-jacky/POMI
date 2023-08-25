'''
This file contains a clear function that is used to clear data when running pytests
'''

from src.data import users, events, valid_token_list, db_state
from src.data_helper import clean_database

def clear():
    global users, events, valid_token_list
    global GENERATE_EVENT_ID
    users.clear()
    events.clear()
    valid_token_list.clear()
    GENERATE_EVENT_ID = 1

    if db_state:
        clean_database()

