'''
This file stores some python data locally
'''

import pandas as pd

db_state = True

users = []

valid_token_list = []

events = []

event_types = ["Music", "Performing & Visual Arts", "Seasonal",
               "Health", "Hobbies", "Business", "Food & Drink", "Sports & Fitness"]

event_seats_list = []

dataframes = pd.DataFrame(columns=["event_id", "time_id", "total_num_tickets", "num_tickets_sold", "tickets_left", "creation_time", "prediction"])