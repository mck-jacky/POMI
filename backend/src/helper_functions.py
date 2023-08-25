'''
This file contains a set of helper functions
'''

from datetime import datetime
from .data import valid_token_list, event_types
from .data_helper import fetch_events, get_users_of_event, get_num_rows_seats
from email.mime.text import MIMEText
import smtplib
import jwt
from meteostat import Point, Daily
import requests


SYSTEM_EMAIL = "pomipomi2023@gmail.com"
EMAIL_PASSWORD = "zlpwyjaxbmfgsvfp"
EMAIL_SUBJECT = 'Your tickets for your event booking'
SECRET = "HelloWorld2023"

def get_weather(start_time):
    '''
    Using the meteostat library, obtain the weather data on the day/time "start_time"
    '''
    
    # start_time is given as a string YYYY MM DD H M
    year = int(start_time[0:4])
    month = int(start_time[5:7])
    date = int(start_time[8:10])

    time = datetime(year, month, date)

    Australia = Point(-33.865143, 151.209900)

    data = Daily(Australia, time, time)
    
    # obtain weather data for this day
    data = data.fetch()

    data_list = data.values.tolist()

    return data_list

def get_email_from_token(token):
    '''
    Given a jwt token, decode the token and obtain user email that is encoded in the token
    '''
    token_bytes = token.encode()
    
    decoded_token = jwt.decode(
        token_bytes, SECRET, algorithms=['HS256'])  # !!!
    
    user_email = decoded_token['email']

    return user_email


def createList(r1, r2):
    '''
    Given a number r1 and r2, return a list of numbers from r1 to r2 with increment of 1
    
    For example, createList(1, 5) creates a list [1, 2, 3, 4, 5]
    '''
    
    return list(range(r1, r2+1))


def check_valid_token(token):
    '''
    Given a token, check if this token is still valid (active)
    '''
    
    for i in valid_token_list:
        if i == token:
            return True
    
    return False


def is_valid_type(event_type):
    '''
    Given a string, verify if the string refers to a valid event type. We have a set of valid event types
    in data.py
    '''
    
    is_valid = False
    
    for events in event_types:
        if events.lower() == str(event_type).lower():
            is_valid = True

    return is_valid


def standardise_type(event_type):
    '''
    Given a valid type string, write it as a standardised string. For example, this function converts
    "music" to "Music"
    '''
    
    standardised_type = ''
    for events in event_types:
        if events.lower() == str(event_type).lower():
            standardised_type = events
    
    return standardised_type


def convert_datetime_to_str(input_time):
    '''
    Converts a string in datetime format, to a datetime object.

    Parameters:
    <input_time>
        A string in datetime format (year, month, day, hour, minute).
    Returns:
        A datetime object.
    '''

    input_time = input_time.replace(second=0)
    input_time = datetime.strftime(input_time, '%Y-%m-%d %H:%M:%S')

    return input_time


def convert_str_to_datetime(input_time):
    '''
    Converts a datetime object, into a string in datetime format. Seconds is
    hardcoded as zero.

    Parameters:
    <input_time>
        A datetime object.
    Returns:
        A string in datetime format (year, month, day, hour, minute, seconds (00)).
    '''

    input_time = datetime.strptime(str(input_time), '%Y-%m-%d %H:%M:%S').date()
    input_time = input_time.replace(second=0)

    return input_time


def send_email_helper(target_email, message, email_subject):
    '''
    Sends an email from account pomipomi2023@gmail.com (our system email) to designated
    email accounts for various purposes
    '''

    # Connect with Google's servers
    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465

    # Login to the system email account
    username = SYSTEM_EMAIL
    password = EMAIL_PASSWORD

    # Send email from system email to users' email
    from_address = SYSTEM_EMAIL
    user_address = target_email

    # Message containing the reset code
    message = MIMEText(message)
    message['subject'] = email_subject
    message['from'] = from_address
    message['to'] = user_address

    # Connect using SSL
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)

    server.login(username, password)
    server.sendmail(from_address, user_address, message.as_string())
    server.quit()

def get_weather(start_time):
    # start_time is given as a string YYYY MM DD H M
    year = int(start_time[0:4])
    month = int(start_time[5:7])
    date = int(start_time[8:10])

    time = datetime(year, month, date)  # need to change this number

    Australia = Point(-33.865143, 151.209900)

    data = Daily(Australia, time, time)
    data = data.fetch()

    print("Data:", data)

    data_list = data.values.tolist()

    print("Data list:", data_list)

    return data_list

if __name__ == '__main__':
    # end_date_time = datetime(2023, 9, 15, 8, 20, 6)
    # # string
    # print(datetime.strftime(datetime.now(), '%Y %m %d %H %M %S'))
    # # datetime
    # print(datetime.strptime(datetime.strftime(
    #     datetime.now(), '%Y %m %d %H %M %S'), '%Y %m %d %H %M %S'))
    # print(convert_str_to_datetime(datetime.strftime(
    #     datetime.now(), '%Y %m %d %H %M %S')))
    start_time = '2023-07-20 12:00'  # Replace with your desired future start time
    # weather_forecast = get_weather_forecast(start_time)
    print(weather_forecast)
