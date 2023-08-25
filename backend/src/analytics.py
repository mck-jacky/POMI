'''
This file contains functions to do the analytics for users, for events and for hosts
'''

from .data import users, db_state, dataframes
from .auth import auth_register, auth_login
from .event import create_event, get_event_database, attended_events_list
from .helper_functions import get_weather, get_email_from_token
import time
import math
from .errors import AccessError
from .booking import book_ticket
from datetime import datetime, timedelta
from .data_helper import get_searches, get_historical_events, create_historical_event_data, save_event_database, fetch_events, return_user, update_sales_stats, sales_stats_tickets_sold, get_event_with_seats, fetch_sales_stats, check_num_tickets_sold, update_prediction_db, is_prediction_there_db, give_stored_prediction_db
import os
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from statistics import mode


SECRET = "HelloWorld2023"


def retrieve_search_history(token):
    '''
    This function retrieves the search history of a registered user
    '''
    
    search_history = []

    user_email = get_email_from_token(token)

    for user in users:
        if user['login']['email'] == user_email:
            search_history = user['search_history']

    if db_state:
        search_history = get_searches(user_email)

    return search_history


def data_collection():
    '''
    Once an event has passed, collect the data of this past event and store it into the database
    for future data analysis
    '''
    
    all_event = get_event_database()
    historical_events = get_historical_events()

    for event in all_event:
        end_datetime = datetime.strptime(event['event_details']['end_date_time'], '%Y %m %d %H %M %S')
        if end_datetime < datetime.now():
            # Check if the event ID already exists in the DataFrame
            if event['event_id'] in [event['event_id'] for event in historical_events]:
                continue

            # for every past event, collect some data
            weather_data = get_weather(event['event_details']['start_date_time'])
            past_event_stats = {
                'creator_id': event['creator_id'],
                'event_id': event['event_id'],
                'event_type': event['event_type'],
                'ticket_price': event['ticket_price'],
                'num_tickets_available': event['num_tickets_available'],
                'num_tickets_sold': int(event['num_tickets_available']) - int(event['num_tickets_left']),
                'host': event['host'],
                'is_online': event['event_details']['venue_type'].lower() == 'online',
                'tmp_mid': weather_data[0][0],
                'tmp_min': weather_data[0][1],
                'tmp_max': weather_data[0][2],
                'precipitation': weather_data[0][3],
                'wind_speed': weather_data[0][6],
                
                # actual attendance will be updated by another function called actual attendance, 
                # once the event has passed. 
                # this is a placeholder as we need to create a data table for every event. once the
                # event has passed, the host can enter the actual attendance figure from the frontend
                # and the figure will be stored into the database in place of this 0
                'actual_attendance': 0
            }

            # create the data table for events

            create_historical_event_data(
                past_event_stats['creator_id'],
                past_event_stats['event_id'],
                past_event_stats['event_type'],
                past_event_stats['ticket_price'],
                past_event_stats['num_tickets_available'],
                past_event_stats['num_tickets_sold'],
                past_event_stats['host'],
                past_event_stats['is_online'],
                past_event_stats['tmp_mid'],
                past_event_stats['tmp_min'],
                past_event_stats['tmp_max'],
                past_event_stats['precipitation'],
                past_event_stats['wind_speed'],
                past_event_stats['actual_attendance']
            )

def update_attendance(event_id, actual_attendance):
    '''
    After an event has passed, the host enters the actual_attendance data in the 
    frontend to update the actual_attendance figure in the database for this event
    '''
    
    # no need for token as they can only use these feature after the listing of my events
    # Retrieve the list of past events
    historical_events = get_historical_events()
    updated_events = []

    # Check if actual_attendance is a valid integer
    try:
        actual_attendance = int(actual_attendance)
    except ValueError:
        # Return an error message if actual_attendance is not an integer
        return {"error": "Actual attendance must be a valid integer."}

    # Identify the correct event
    for event in historical_events:
        if str(event['event_id']) == str(event_id):
            if actual_attendance > event['num_tickets_sold']:
                # Return an error message if actual_attendance is greater than num_tickets_sold
                return {"error": "Actual attendance cannot be greater than the number of tickets sold."}

            # Update the 'actual_attendance' field for the correct event
            event['actual_attendance'] = actual_attendance
            if db_state == True:
                save_event_database(event)
                updated_events.append(event)

    if updated_events:
        # Return a success message if events were updated
        return {"success": "Attendance updated successfully."}
    else:
        # Return an error message if no events were updated
        return {"error": "Event not found or attendance update failed."}


def predict_attendance(event_id, event_type, ticket_price, num_tickets_available,
                       host, is_online, tmp_mid, tmp_min, tmp_max, precipitation,
                       wind_speed):
    '''
    Given the events and the weather forecast on the day, return the attenance prediction
    for this event
    '''
    
    historical_events = get_historical_events()
    data = pd.DataFrame(historical_events)

    directory = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(directory, 'attendance_prediction_model.xgb')

    best_model = xgb.XGBRegressor()
    best_model.load_model(model_path)

    # Create a DataFrame with the input data
    input_data = pd.DataFrame({
        'event_id': [event_id],
        'event_type': [event_type],
        'ticket_price': [ticket_price],
        'num_tickets_available': [num_tickets_available],
        'host': [host],
        'is_online': [is_online],
        'tmp_mid': [tmp_mid],
        'tmp_min': [tmp_min],
        'tmp_max': [tmp_max],
        'precipitation': [precipitation],
        'wind_speed': [wind_speed],
    })

    label_encoder = LabelEncoder()
    input_data["host"] = label_encoder.fit_transform(input_data["host"])
    input_data["event_type"] = label_encoder.fit_transform(input_data["event_type"])

    # Predict the actual attendance using the loaded model
    attendance_prediction = best_model.predict(input_data)
    if int(attendance_prediction[0]) > int(num_tickets_available):
        attendance_prediction[0] = int(num_tickets_available)

    return attendance_prediction[0]


def is_event_historical(event_id):
    '''
    Given an event id, return true if this event has passed, return false otherwise
    '''
    
    # Get the historical events
    historical_events = get_historical_events()

    # Check if the event_id is present in the historical events list
    for event in historical_events:
        if event.get('event_id') == event_id:
            return True

    return False

def get_historical_attendance(event_id):
    '''
    Given an event id (this event has already passed), get its attendance figure
    '''
    
    events = get_historical_events()
    for event in events:
        if str(event['event_id']) == str(event_id):
            return event['actual_attendance']


def attendance_prediction_past(event_id):
    '''
    Extract critical information as such event details and weather on the day of the event,
    to be used for the attendance prediction. This is for events that have passed
    '''
    
    events = get_historical_events()
    for event in events:
        if event['event_id'] == event_id:
            # Extract the required information for prediction from the event_info dictionary
            event_type = event['event_type']
            ticket_price = event['ticket_price']
            num_tickets_available = event['num_tickets_available']
            host = event['host']
            is_online = event['is_online']
            tmp_mid = event['tmp_mid']
            tmp_min = event['tmp_min']
            tmp_max = event['tmp_max']
            precipitation = event['precipitation']
            wind_speed = event['wind_speed']

            # Call predict_attendance function with the extracted information
            attendance_prediction = predict_attendance(event_id, event_type, ticket_price, num_tickets_available,
                                                        host, is_online, tmp_mid, tmp_min, tmp_max,
                                                        precipitation, wind_speed)

            return attendance_prediction


def attendance_prediction_current(event_id):
    '''
    Extract critical information as such event details and weather on the day of the event,
    to be used for the attendance prediction
    '''
    
    events = fetch_events()
    # Find the event with the given event_id in the events list
    event_info = next((event for event in events if event[0] == int(event_id)), None)

    if event_info:
        # Extract the required information for prediction from the event_info tuple
        event_id = event_info[0]
        event_type = event_info[4]
        ticket_price = event_info[12]
        num_tickets_available = event_info[10]
        host = event_info[7]
        is_online = event_info[6].lower() == 'online'
        tmp_mid = 26.0
        tmp_min = 18.0
        tmp_max = 34.0
        precipitation = 10.0
        wind_speed = 15

        # Call predict_attendance function with the extracted information
        attendance_prediction = predict_attendance(event_id, event_type, ticket_price, num_tickets_available,
                                                    host, is_online, tmp_mid, tmp_min, tmp_max,
                                                    precipitation, wind_speed)

        return attendance_prediction


def user_analytics(token):
    """
    Given user token, return the analytics of this account
    """
    email = get_email_from_token(token)
    
    num_events_participated = 0
    
    attended_events = attended_events_list(token)
                
    # if user has not attended any events, raise access error as user account analytics 
    # are not yet ready
    if attended_events == []:
        raise AccessError(description='Sorry, you have not participated in any events yet. Come back for \
                            user account analytics insights after you attend the amazing events on our site!.')
    
    event_ids = []
    for event in attended_events:
        event_ids.append(event['event_id'])
    
    num_events_participated = len(event_ids)
    
    # a list of type of events that the user have been to
    type_of_events = []
    
    # a list of hosts that the user has booked an event for
    host_list = []
    
    all_events = get_event_database()
    for event in all_events:
        for ids in event_ids:
            if event['event_id'] == ids:
                type_of_events.append(event['event_type'])
                host_list.append(event['host'])

    # find the mode of the types and hosts to determine the user's most booked event type
    # and most booked host
    fav_event_type = mode(type_of_events)
    fav_host = mode(host_list)
    
    # return user account analytics
    return {
        'num_events_participated': num_events_participated,
        'favourite_event_type': fav_event_type, 
        'favourite_host': fav_host
    }

def get_creation_time_event(event_id):
    '''
    Given an event id, obtain its time of creation
    '''
    
    timestamp_event = 0.0
    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                timestamp_event = float(row['creation_time'])
    else:
        timestamp_event = float(fetch_sales_stats(event_id)[0]['timestamp'])

    datetime_object = datetime.fromtimestamp(timestamp_event)
    
    return datetime_object
    
def has_fetched_sales_data(event_id, time_id):
    '''
    This function is called by forecast_demand() to check if the sales data has been 
    stored into the database. if yes, return true, else return false
    '''
    
    has_fetched_event_data = True
    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                if row['time_id'] == time_id:
                    if row['num_tickets_sold'] == -999999:
                        has_fetched_event_data = False
    else:
        list_loop = get_event_with_seats(event_id)
        has_fetched_event_data = check_num_tickets_sold(event_id, time_id)

    return has_fetched_event_data

def store_sales_stats(event_id, time_id, num_tickets_left, num_tickets_sold):
    '''
    Given an event, update the sales data for this time period with time_id
    '''
    
    global dataframes
    
    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                if row['time_id'] == time_id:
                    dataframes.at[index, 'num_tickets_sold'] = num_tickets_sold
                    dataframes.at[index, 'tickets_left'] = num_tickets_left
    else:
        update_sales_stats(event_id, time_id, num_tickets_sold, num_tickets_left)


def get_tickets_sold_df(event_id, time_id):
    '''
    Given an event id, fetch the number of tickets sold data within the time period
    with time_id
    '''
    
    # get the number of tickets sold only for this time period

    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                if row['time_id'] == time_id:
                    return row['num_tickets_sold']
    else:
        return sales_stats_tickets_sold(event_id, time_id)
    

def get_num_tickets_sold_event(event_list, event_id, total_num_tickets):
    '''
    Given an event_id, return the number of tickets that have been sold
    '''
    num_tickets_left = -1
    if not db_state:
        for event in event_list:
            if event['event_id'] == event_id:
                num_tickets_left = event['num_tickets_left']
        num_tickets_sold = total_num_tickets - num_tickets_left
    else:
        num_tickets_left = get_event_with_seats(event_id)['num_tickets_left']
        num_tickets_sold = total_num_tickets - num_tickets_left
    
    return num_tickets_sold

def update_prediction(event_id, time_id, predicted_sales_figure):
    '''
    Updates the prediction figure in the database for the sales table for event with
    event_id
    '''
    
    global dataframes
    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                if row['time_id'] == time_id:
                    dataframes.at[index, 'prediction'] = predicted_sales_figure
    else:
        update_prediction_db(event_id, time_id, predicted_sales_figure)

def is_prediction_there(event_id, time_id):
    '''
    Checks if the prediction field for the sales table has been updated. If not, 
    return false, else return true
    '''
    
    is_prediction_there = True
    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                if row['time_id'] == time_id:
                    if dataframes.at[index, 'prediction'] == -999999:
                        is_prediction_there = False
    else:
        is_prediction_there = is_prediction_there_db(event_id, time_id)
    
    return is_prediction_there

def give_stored_prediction(event_id, time_id):
    '''
    Given an event id, return the prediction data for the time period with time_id
    '''
    
    stored_prediction = -999999
    if not db_state:
        for index, row in dataframes.iterrows():
            if row['event_id'] == event_id:
                if row['time_id'] == time_id:
                    stored_prediction = dataframes.at[index, 'prediction']
    else:
        stored_prediction = give_stored_prediction_db(event_id, time_id)
    
    return stored_prediction


def forecast_demand(event_id):
    '''
    This function predicts how many tickets will be sold for an event by analysing the number of 
    tickets sold in a short duration and extending that trend for the whole duration until the event
    '''
    
    predicted_sales_figure = 0

    all_events = get_event_database()
    
    total_num_tickets = -1
    start_time = ''
    
    for event in all_events:
        if int(event['event_id']) == int(event_id):
            start_time = event['event_details']['start_date_time']
            total_num_tickets = event['num_tickets_available']
    
    # get the start time of the event
    start_datetime = datetime.strptime(start_time, '%Y %m %d %H %M %S')
    
    # get the creation time of the event
    creation_time = get_creation_time_event(event_id)
    
    time_diff = start_datetime - creation_time

    time_diff_minutes = round(time_diff.total_seconds() / 60, 1)
    
    # calculate the time period for this event
    # the demand will be calculated every this "time period"
    time_period = time_diff_minutes / 4

    # if past the first time period, grab ticket sales data for the first time period
    if datetime.now() >= creation_time + timedelta(minutes=time_period) and \
                        datetime.now() < creation_time + timedelta(minutes=2*time_period) :
        # if a prediction has not already been updated for time period one, calculate it
        if not is_prediction_there(event_id, 1): 
            # get the number of tickets sold in the first time period
            num_tickets_sold = get_num_tickets_sold_event(all_events, event_id, total_num_tickets)
            
            # calculate the prediction based on tickets sold in the first time period
            predicted_sales_figure =  num_tickets_sold * 4
            
            # the predicted sales figure is capped at max number of tickets
            if predicted_sales_figure > total_num_tickets:
                predicted_sales_figure = total_num_tickets
            
            num_tickets_left = total_num_tickets - num_tickets_sold
            
            # if num tickets sold data has not been updated, update it in the dataframe. else don't
            # time id here is 1
            if not has_fetched_sales_data(event_id, 1):
                store_sales_stats(event_id, 1, num_tickets_left, num_tickets_sold)

            if predicted_sales_figure < 0:
                predicted_sales_figure = 0

            # store the prediction in the table
            update_prediction(event_id, 1, math.ceil(predicted_sales_figure))
        
        # if a prediction has already been updated for time period one, just return the prediction
        # that is stored in the database
        else: 
            predicted_sales_figure = give_stored_prediction(event_id, 1)
            
        return math.ceil(predicted_sales_figure)
    
    # if past the second time period, grab ticket sales data for the second time period
    elif datetime.now() >= creation_time + timedelta(minutes=2*time_period) and \
        datetime.now() < creation_time + timedelta(minutes=3*time_period):
        # if a prediction has not already been updated for time period one, calculate it
        if not is_prediction_there(event_id, 2): 
            # get number of tickets sold in the first time period
            tickets_sold_first_time_period = get_tickets_sold_df(event_id, 1)
            
            # total number of tickets sold at this point
            total_num_tickets_sold_updated = get_num_tickets_sold_event(all_events, event_id, total_num_tickets)
            
            # get number of tickets sold in the second time period
            tickets_sold_second_time_period = total_num_tickets_sold_updated - tickets_sold_first_time_period
            
            # if host did not fresh and store data for the first time period, tickets_sold_second_time_period is
            # the total number of tickets sold
            if not has_fetched_sales_data(event_id, 1): 
                tickets_sold_second_time_period = total_num_tickets_sold_updated
            
            num_tickets_left = total_num_tickets - total_num_tickets_sold_updated
            
            # store the sales stats
            if not has_fetched_sales_data(event_id, 2):
                store_sales_stats(event_id, 2, num_tickets_left, tickets_sold_second_time_period)
            
            # if host did not fresh and store data for the first time period, make the prediction based
            # on the second time period sales data
            if not has_fetched_sales_data(event_id, 1):
                predicted_sales_figure = tickets_sold_second_time_period*4
            
            else: 
                # if all the data are available, calculate the predicted sales figure. more weights are put on the
                # more recent purchase data
                predicted_sales_figure =  (0.4*tickets_sold_first_time_period + 0.6*tickets_sold_second_time_period)*4
            
            # the predicted sales figure is capped at max number of tickets
            if predicted_sales_figure > total_num_tickets:
                predicted_sales_figure = total_num_tickets
            
            if predicted_sales_figure < total_num_tickets_sold_updated:
                predicted_sales_figure = total_num_tickets_sold_updated
            
            if predicted_sales_figure < 0:
                predicted_sales_figure = 0

            # store the prediction in the table
            update_prediction(event_id, 2, math.ceil(predicted_sales_figure))
        
        # if a prediction has already been updated for time period two, just return the prediction
        # that is stored in the database
        else: 
            predicted_sales_figure = give_stored_prediction(event_id, 2)

        return math.ceil(predicted_sales_figure)
    
    # if past the third time period, grab ticket sales data for the third time period
    elif datetime.now() >= creation_time + timedelta(minutes=3*time_period) and datetime.now() < start_datetime:
        # if a prediction has not already been updated for time period three, calculate it
        if not is_prediction_there(event_id, 3): 
            tickets_sold_first_time_period = get_tickets_sold_df(event_id, 1)
            tickets_sold_second_time_period = get_tickets_sold_df(event_id, 2)
            # total number of tickets sold by time period 3
            total_num_tickets_sold_updated = get_num_tickets_sold_event(all_events, event_id, total_num_tickets)

            tickets_sold_third_time_period = total_num_tickets_sold_updated - tickets_sold_first_time_period - tickets_sold_second_time_period
            num_tickets_left = total_num_tickets - total_num_tickets_sold_updated
            
            # store the sales stats
            if not has_fetched_sales_data(event_id, 3):
                store_sales_stats(event_id, 3, num_tickets_left, tickets_sold_third_time_period) # <<<<<<<<<<<<<< 
            
            # if any of the data is not fetched, tickets_sold_third_time_period = get_num_tickets_sold_event()
            if not has_fetched_sales_data(event_id, 1) or not has_fetched_sales_data(event_id, 2):
                tickets_sold_third_time_period = total_num_tickets_sold_updated
            
            # if data from any time period is missing, calcuate the prediction as:
            if not has_fetched_sales_data(event_id, 1) and not has_fetched_sales_data(event_id, 2):
                predicted_sales_figure = tickets_sold_third_time_period * 2
            elif not has_fetched_sales_data(event_id, 1) and has_fetched_sales_data(event_id, 2):
                predicted_sales_figure = (0.4*tickets_sold_second_time_period + 0.6*tickets_sold_third_time_period)*3
            elif has_fetched_sales_data(event_id, 1) and not has_fetched_sales_data(event_id, 2):
                predicted_sales_figure = (0.3*tickets_sold_first_time_period + 0.7*tickets_sold_third_time_period)*3
            else:
                # if data from all time periods are obtained, calculate the predicted sales figure
                predicted_sales_figure =  (0.2*tickets_sold_first_time_period + 0.3*tickets_sold_second_time_period +
                                            0.5 * tickets_sold_third_time_period)*4
            
            if tickets_sold_second_time_period == 0 and tickets_sold_first_time_period == 0:
                predicted_sales_figure = tickets_sold_third_time_period*2
            
            # the predicted sales figure is capped at max number of tickets
            if predicted_sales_figure > total_num_tickets:
                predicted_sales_figure = total_num_tickets
            
            # predicted sales cannot be less than the actual number of tickets sold 
            if predicted_sales_figure < total_num_tickets_sold_updated:
                predicted_sales_figure = total_num_tickets_sold_updated
            
            if predicted_sales_figure < 0:
                predicted_sales_figure = 0
            
            # store the prediction in the table
            update_prediction(event_id, 3, math.ceil(predicted_sales_figure))
        
        # if a prediction has already been updated for time period three, just return the prediction
        # that is stored in the database
        else: 
            predicted_sales_figure = give_stored_prediction(event_id, 3)
        
        return math.ceil(predicted_sales_figure)

    return "To be updated"


if __name__ == '__main__':
    # testing data collection: (only when the check for not creating event in the past is turned off in event.py)
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    # Create first event. This should have event id of 1
    create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra Chopin", "Music", "Concert Hall Sydney Opera House",
                 "Online", "POMI orchestra", (datetime.now() + timedelta(minutes=4)).strftime("%Y %m %d %H %M %S"), 
                 (datetime.now() + timedelta(minutes=8000)).strftime("%Y %m %d %H %M %S"), 100, 100, 35.5, 0, 100, "concert hall photo", 50, "seats image")

    # Create second event. This should have event id of 2
    #create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 #"Online", "POMI church", "2022 12 15 12 15 12", "2022 12 15 12 20 12", 80, 80, 0.0, "church hall photo", 80, "seats image")
    
    #create_event(login_success['token'], "Chopin's Nocturnes", "Presented by POMI Symphony Orchestra", "Music", "Concert Hall, Sydney Opera House", "Face to face",
                 #"POMI orchestra", "2020 09 15 16 30 12", "2020 09 15 16 35 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, "seats image")
    
    #print(has_fetched_sales_data(1, 1))

    """    # no data for second hour
    book_ticket(login_success['token'], 1, 2, [11, 12])
    time.sleep(65)
    print(forecast_demand(1))
    print(dataframes)
    # no data for second hour
    time.sleep(65)
    print(dataframes)
    # book 10 tickets in the last hour
    book_ticket(login_success['token'], 1, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    # capped at max num tickets
    print(forecast_demand(1))
    print(dataframes)"""


    # TEST CASE 7: Book no tickets in the few two hours but book a lot in the last hour. 
    """    print(forecast_demand(1))
    print(dataframes)
    
    # book no ticket in the first hour
    time.sleep(65)
    print("forecast 1st hr:")
    # 
    print(forecast_demand(1))
    print(dataframes)
    
    # booking no ticket in second hour
    time.sleep(65)
    print("forecast 2nd hr:")
    #
    print(forecast_demand(1))
    print(dataframes)
    
    # booking 10 tickets in the third hour
    book_ticket(login_success['token'], 1, 10, [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    time.sleep(65)
    print("forecast 3rd hr:") 
    #
    print(forecast_demand(1))
    print(dataframes)"""



    # TEST CASE 6: buy lots of tickets in the first hour but only a few in later hours. 
    # forecast should not fall below num of tickets purchased
    """"    print(forecast_demand(1))
    print(dataframes)
    
    # book 10 tickets in the first hour
    booking = book_ticket(login_success['token'], 1, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    print("forecast 1st hr:")
    # 40
    print(forecast_demand(1))
    print(dataframes)
    
    booking = book_ticket(login_success['token'], 1, 2, [20])
    time.sleep(65)
    print("forecast 2nd hr:")
    #
    print(forecast_demand(1))
    print(dataframes)
    
    # booking just 1 ticket in the third hour
    booking = book_ticket(login_success['token'], 1, 1, [30])
    time.sleep(65)
    print("forecast 3rd hr:") 
    #
    print(forecast_demand(1))
    print(dataframes)"""


    """# TEST CASE 5: buy lots of tickets in the first hour but none in later hours. 
    # forecast should not fall below num of tickets purchased
    print(forecast_demand(1))
    print(dataframes)
    
    # book 10 tickets in the first hour
    booking = book_ticket(login_success['token'], 1, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    print("forecast 1st hr:")
    # 40
    print(forecast_demand(1))
    print(dataframes)
    
    # booking nothing in the second hour
    time.sleep(65)
    print("forecast 2nd hr:")
    # 16
    print(forecast_demand(1))
    print(dataframes)
    
    # booking nothing in the third hour
    time.sleep(65)
    print("forecast 3rd hr:") 
    # 10
    print(forecast_demand(1))
    print(dataframes)"""

    """# TEST CASE 4: buy lots of tickets in the first hour but not many in later hours
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the first hour
    booking = book_ticket(login_success['token'], 1, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    time.sleep(65)
    print("forecast 1st hr:")
    # 40 
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the second hour
    booking = book_ticket(login_success['token'], 1, 3, [11, 12, 13])
    time.sleep(65)
    print("forecast 2nd hr:")
    # 24
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the third hour
    booking = book_ticket(login_success['token'], 1, 1, [14])
    time.sleep(65)
    print("forecast 3rd hr:") 
    # 14
    print(forecast_demand(1))
    print(dataframes)"""

    """# TEST CASE 3: only has only has 20 tickets and the demand reaches the maximum
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the first hour
    booking = book_ticket(login_success['token'], 1, 3, [1, 2, 3])
    time.sleep(65)
    print("forecast 1st hr:")
    # 12
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the second hour
    booking = book_ticket(login_success['token'], 1, 5, [4, 5, 6, 7, 8])
    time.sleep(65)
    print("forecast 2nd hr:")
    # 17
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the third hour
    booking = book_ticket(login_success['token'], 1, 8, [9, 10, 11, 12, 13, 14, 15, 16])
    time.sleep(65)
    print("forecast 3rd hr:") 
    # should just return 20
    print(forecast_demand(1))
    print(dataframes)"""

    # TEST CASE 2: book the same number of tickets every hour 
    # forecast will stay the same
    """    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the first hour
    booking = book_ticket(login_success['token'], 1, 2, [1, 2])
    time.sleep(125)
    print("forecast 1st hr:")
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the second hour
    booking = book_ticket(login_success['token'], 1, 2, [3, 4])
    time.sleep(125)
    print("forecast 2nd hr:")
    print(forecast_demand(1))
    print(dataframes)
    
    # book 2 tickets in the third hour
    booking = book_ticket(login_success['token'], 1, 2, [5, 6])
    time.sleep(125)
    print("forecast 3rd hr:")
    print(forecast_demand(1))
    print(dataframes)"""

    # BELOW IS TEST CASE 1 - general
    # need to print out the table too
    print(forecast_demand(1))
    print(dataframes)
    
    # book 1 ticket in the first hour
    booking = book_ticket(login_success['token'], 1, 1, [2]) # 4
    time.sleep(65)
    print("forecast 1st hr:")
    print(forecast_demand(1))
    print(dataframes)
    
    book_ticket(login_success['token'], 1, 4, [100, 99, 98, 97])# 4 purchased in second time period
    print("again:")
    print("-----> " + str(forecast_demand(1)) + " <-----")
    print(dataframes)
    
    #print("!!! again:")
    #print(forecast_demand(1))
    
    # book 3 tickets in the second hour
    booking = book_ticket(login_success['token'], 1, 3, [1, 3, 5]) # 19
    #book_ticket(login_success['token'], 1, 3, [96, 95, 94]) # 26
    time.sleep(65)
    print("forecast 2nd hr:")
    print(forecast_demand(1))
    print(dataframes)
    
    book_ticket(login_success['token'], 1, 3, [96, 95, 94]) # 4 purchased in second time period
    print("again22222:")
    print("-----> " + str(forecast_demand(1)) + " <-----")
    print(dataframes)
    
    #print("!!! again2:")
    #print(forecast_demand(1))
    
    # book 3 tickets in the second hour
    booking = book_ticket(login_success['token'], 1, 3, [10, 7, 9])
    book_ticket(login_success['token'], 1, 5, [93, 92, 91, 90, 89])
    time.sleep(65)
    print("forecast 3rd hr:")
    print(forecast_demand(1))
    print(dataframes)
    book_ticket(login_success['token'], 1, 10, [31, 32, 33, 34, 35, 36, 37, 38, 39, 40])
    print(forecast_demand(1))
    
    #print("!!! again2:")
    #print(forecast_demand(1))
    
    """    date_time = (datetime.now() + timedelta(minutes=8)).strftime("%Y %m %d %H %M %S")
    print("!!!!")
    print(date_time)
    print(type(datetime))"""
    
    """booking = book_ticket(login_success['token'], 1, 1, [1])
    booking2 = book_ticket(login_success['token'], 2, 1, [2])
    booking3 = book_ticket(login_success['token'], 3, 1, [100])
    
    print(user_analytics(login_success['token']))"""
    
    """# update: data_collection now needs a parameter actual_attendance
    data_collection()

    # test code for retrieving search history is below
    # print(get_event_list())

    search_event(login_success['token'], "presented by", "")
    search_event(login_success['token'], "chopin", "")
    search_event(login_success['token'], "orchestra", "")

    # retrieve user search history
    print(retrieve_search_history(login_success['token']))

    search_event(login_success['token'], " ", "")

    print(retrieve_search_history(login_success['token']))
    
    search_event(login_success['token'], "random", "")
    
    print(retrieve_search_history(login_success['token']))

    # print(predict_attendance('some_creator_id', 7, 'Music', 50.0, 100, 50, 'Host Company', True, 25.0, 20.0, 30.0, 5.0, 10.0))

    print(attendance_prediction_current(1))"""
