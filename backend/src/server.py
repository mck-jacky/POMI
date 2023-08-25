import signal
from flask import Flask, request, make_response
from flask_cors import CORS
from json import dumps

# Local File Imports
from .analytics import retrieve_search_history, update_attendance, attendance_prediction_current, attendance_prediction_past, get_historical_attendance, user_analytics, forecast_demand
from .auth import auth_logout, auth_login, auth_register, auth_passwordreset_request, auth_passwordreset_reset, check_valid_reset_code
from .booking import book_ticket, cancel_booking, get_event_and_seats_by_id_fixed
from .communication import broadcast_to_customer
from .data_helper import give_recommendations, get_event_with_seats
from .errors import AccessError, InputError
from .image import store_image_locally, encode_to_base64, clear_user_images_uploads
from .event import create_event, decrement_num_tickets, search_event, get_event_list, cancel_event, user_tickets_booked, user_events_created, get_user_events_created_past, get_current_event_id, user_tickets_booked_past
from .reviews import post_review, reply_review, get_reviews_of_event

# Change Server Port Here
import src.config


## Server Setup ################################################################


def quit_gracefully(*args):
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

reset_code = ''


## Debugging ###################################################################


def debug(text, number, data):
    """
    Prints the inputs to the terminal. Debugging purposes only.

    Parameters:
        <text>
            The title of the print statement.
        <number>
            Sequence number if needed. If not, set to zero, and this won't
            print.
        <data>
            The data to be printed.
    Returns:
        None
    File:
        server.py
    """

    print("===================================================================")
    print(text)

    if number != 0:
        print(number)

    print(data)
    print("===================================================================")

    return


## Test Route ##################################################################


@APP.route("/echo", methods=['GET'])
def echo():
    """
    Debugging route. Returns whatever JSON file is sent to it.

    HTTP request body input:
        None
    Exceptions:
        InputError:
        - If the key in the JSON file is "echo".
    Returns:
        Returns the given JSON file, unless the file contains the key "echo",
        of which it will raise an exception.
    File:
        server.py
    """

    data = request.get_json()

    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')

    return dumps({
        'data': data
    })


## Authentication Routes #######################################################


@APP.route("/auth/register", methods=['POST'])
def auth_register_route():
    """
    Registers a new user if all the input fields are valid. Validity check
    happens in auth.py.

    HTTP request body input:
        <input_email> 
            Standard email format.
        <password>
            The password can be any string containing ASCII
            characters. The string must be at least 7 chars long.
        <first_name>
            The first name is a string of ASCII characters,
            that has a length of 2-49 chars.
        <last_name>
            The last name is a string of ASCII characters,
            that has a length of 2-49 chars.
        <cardholder_name>
            Any length of ASCII characters. Not tied to first_name and
            last_name.
        <card_number>
            Should be 16 digits (will be converted to int in auth.py).
        <expiry_month>
            Should be 2 digits (will be converted to int in auth.py). If month
            is Jan-Sep, it is not necessary to add leading zeroes.
        <expiry_year>
            Should be 4 digits (will be converted to int in auth.py).
        <cvv_num>
            Should be 3 digits (will be converted to int in auth.py).
    Exceptions:
        InputError:
        - Email format is not valid, or has been taken.
        - First or last name does not meet the required length.
        - Password is less than 7 chars.
        - Card number is not 16 digits, and is all digits.
        - Card expiry month should be between 1-12 inclusive.
        - Card expiry year should be 4 digits.
        - Card expiry should be after the present date.
        - Card CVV should be 3 digits.
    Returns:
        Returns a str in JSON format with the keys as above, and their
        respective values.
    Routes Page:
        RegisterPage.jsx
    """

    data = request.get_json()

    return dumps(auth_register(data['input_email'],
                               data['password'],
                               data['first_name'],
                               data['last_name'],
                               data['cardholder_name'],
                               data['card_number'],
                               data['expiry_month'],
                               data['expiry_year'],
                               data['cvv_num']))


@APP.route("/auth/login", methods=['POST'])
def auth_login_route():
    """
    Let a registered user login, if they enter their email and password 
    correctly.

    HTTP request body input:
        <email>
            Format checking done with backend. Validity is given by HTTP codes. 
        <password>
            The password can be any string containing ASCII 
            characters. The string must be at least 6 chars long.
    Exceptions:
        InputError:
        - If the password to the email used is incorrect.
        - If the email is invalid.
    Returns:
        Returns a JSON dictionary with the generated token (session).
    Routes Page:
        LoginPage.jsx
    """

    data = request.get_json()

    return dumps(
        auth_login(data['email'],
                   data['password']))


@APP.route("/auth/logout", methods=['POST'])
def auth_logout_route():
    """
    Given an active token, invalidates the token to log the user out.

    HTTP request body input:
        <token>
            The user's token that is currently logged in.
    Exceptions:
        AccessError:
        - If the token is invalid.
        - If the logout process fails.
    Return Value:
        Returns an empty JSON dictionary.
    Routes Page:
        NavBar.jsx
    """

    data = request.get_json()

    response = auth_logout(data['token'])

    if response['is_success'] == True:
        return dumps({})
    else:
        # Will logging out ever fail?
        raise AccessError(description="Logout failed.")


@APP.route("/auth/password/reset/request", methods=['POST'])
def auth_password_reset_request_route():
    """
    Requests the reset of password of a valid email associated with an account.
    An email will be sent to the registered email with a validation code.

    Step 1 in password reset process.

    HTTP request body input:
        <input_email>
            A registered email that the user would like the associated account's
            password reset.
    Exceptions:
        InputError:
        - The email is not a valid/registered email.
    Return Value:
        Returns an empty JSON dictionary.
    Routes Page:
        ResetPasswordPage.jsx
    """

    data = request.get_json()

    return auth_passwordreset_request(data['email'])


@APP.route("/auth/password/reset/verify", methods=['POST'])
def auth_password_reset_request_verify():
    """
    Requests the reset of password by asking the user to enter the verification
    code sent to the nominated email.

    Step 2 in password reset process.

    HTTP request body input:
        <reset_code>
            The reset code sent to the nominated email.
    Exceptions:
        InputError:
        - The reset code is invalid.
    Return Value:
        Returns an empty JSON dictionary.
    Routes Page:
        ResetPasswordPage.jsx
    """

    data = request.get_json()

    global reset_code
    reset_code = data['code']

    return dumps(check_valid_reset_code(data['code']))


@APP.route("/auth/password/reset/reset", methods=['POST'])
def auth_password_reset_reset_route():
    """
    Resets the password of an account by prompting the user to enter a new
    password.

    Step 3 in password reset process.

    HTTP request body input:
        <password>
            A new password of the same standard format.
    Exceptions:
        InputError:
        - The password format is invalid.
        - The reset code is invalid.
    Return Value:
        Returns an empty JSON dictionary.
    Routes Page:
        ResetPasswordPage.jsx
    """

    data = request.get_json()

    return auth_passwordreset_reset(reset_code, data['password'])


## Event Routes ################################################################


@APP.route("/event/create", methods=['POST'])
def event_create_route():
    """
    Creates an event with the required fields.

    HTTP request body input:
        <token>
            A user's active, valid token.
        <event_title>
            The event's title (no format limitations).
        <event_description>
            The event's description (no format limitations).
        <event_type>
            The event's type. Is a selection from pre-selected types only.
        <venue>
            The event's venue (no format limitations).
        <venue_type>
            The event's venue type. Can only choose from venue (in-person),
            online, or TBA. If venue is selected, then the event will need an
            address as well.
        <organiser>
            The host of the event. Does not necessarily have to be the same as
            the creator of the event.
        <start_date_time>
            The start time of the event in ('%Y %m %d %H %M %S) format.
        <end_date_time>
            The end time of the event in ('%Y %m %d %H %M %S) format.
        <num_tickets_available>
            The total number of tickets available (i.e., before any are sold).
        <tickets_left>
            The number of tickets left that are available for purchase.
        <ticket_price>
            The price of one ticket (decimal).
    Exceptions:
        AccessError:
        - Token is invalid.
        InputError:
        - Invalid event type (event type is chosen from presets).
        - Incorrect date format ('%Y %m %d %H %M %S).
        - If event end time is before the start time.
        - If the start time is before the present.
        - If for some reason the tickets remaining is not equal to the total
          amount of tickets (when none have been purchased yet).
    Returns:
        Returns a str in JSON format with the keys as above, and their
        respective values.
    Routes Page:
        EventCreatePage.jsx
    """

    data = request.get_json()

    # Converts the incoming image from a base64 data URL object to a local file
    image = store_image_locally('event',
                                get_current_event_id(),
                                data['image'])
    
    # Only save the seating image if the venue type is not online
    if data['venue_type'] != "Online":
        seating_plan_image = store_image_locally('seating',
                                                 get_current_event_id(),
                                                 data['seating_plan_image'])
    else:
        seating_plan_image = ""

    created_event = create_event(data['token'],
                                 data['event_title'],
                                 data['event_description'],
                                 data['event_type'],
                                 data['venue'],
                                 data['venue_type'],
                                 data['organiser'],
                                 data['start_date_time'],
                                 data['end_date_time'],
                                 data['num_tickets_available'],
                                 data['tickets_left'],
                                 data['ticket_price'],
                                 data['price_min'],
                                 data['price_max'],
                                 image,
                                 data['number_of_seats'],
                                 seating_plan_image)

    return dumps(created_event)


@APP.route("/event/list/get", methods=['GET'])
def get_event_list_route():
    """
    Returns a list of all future event that have not sold out (e.g.,
    dictionaries representing events).

    HTTP request body input:
        None
    Exceptions:
        None
    Returns:
        A list of dictionaries, with each dictionary being an event.
    Routes Page:
        EventPage.jsx
        LandingPage.jsx
        SearchFunction.jsx
    """

    # Grabs the list of events for images conversion
    events_list_with_local_images = get_event_list()  # List
    events_list_with_base64_images = []

    # Replaces all instances of local images with their base64 equivalent
    for event in events_list_with_local_images:
        events_list_with_base64_images.append(convert_local_images_to_base64_in_event(event))

    response = make_response(dumps(events_list_with_base64_images))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@APP.route("/event/search", methods=['GET'])
def search_event_route():
    """
    Search for events based on event title, event description and type. It
    retrieves events matching the search criteria.

    HTTP request body input:
        <event_title>
            The title of the event.
        <event_description>
            The description of the event.
        <event_type>
            The type of event.
    Exceptions:
        None
    Returns:
        A list of dictionaries of all the relevant event searches.
    Routes Page:
        SearchFunction.jsx
    """

    token = ''

    try:
        token = request.args.get('token', '')
    except ValueError as error:
        raise AccessError("Guests cannot search.")

    event_keyword = request.args.get('event_keyword', '')
    event_type = request.args.get('event_type', '')

    return dumps(search_event(token,
                              event_keyword,
                              event_type))


@APP.route("/search/history", methods=['GET'])
def search_history_route():
    """
    Retrieves the search history of a particular user given the token.

    HTTP request body input:
        <token>
            The token of the user
    Exceptions:
        None
    Returns:
        A list of dictionaries of all the search histories of the user.
    Routes Page:
        SearchHistoryPage.jsx
    """

    token = request.args.get('token', '')

    return dumps(retrieve_search_history(token))


@APP.route("/event/ticket/decrease", methods=['PUT'])
def decrement_num_tickets_route():
    """
    Decrements the number of tickets (just purchased) from the total number of
    tickets still available, from the given event.

    HTTP request body input:
        <event_id>
            The ID of the event to have remaining ticket quantity decremented
            (will be converted to int in event.py).
        <num_tickets_bought>
            The number of tickets bought in this one transaction. I.e., current
            number of available tickets minus num_tickets_bought. (Will be
            converted to int in event.py).
    Exceptions:
        AccessError:
        - If the event does not exist.
    Returns:
        Does not return anything. Only a HTTP 200 response if sucessful.
    Routes Page:
        AAA
    """

    data = request.get_json()

    decrement_num_tickets(data['event_id'], int(data['num_tickets_bought']))

    return dumps({})


@APP.route("/event/cancel", methods=['POST'])
def event_cancel_route():
    """
    Allows a creator of an event to cancel it, with several conditions. It also
    broadcasts a cancellation message, and refunds all tickets.

    HTTP request body input:
        <token>
            A valid token (to make sure the cancel operation is performed by
            the event creator only).
        <event_id>
            A valid event ID.
    Exceptions:
        AccessError:
        - The token is invalid, thus user cannot cancel this event.
        - Can only cancel events that are more than 30 minutes from starting.
        - Cannot cancel an event that has started.
    Returns:
        An empty dictionary.
    Routes Page:
        MyEvent.jsx
    """

    data = request.get_json()

    return dumps(cancel_event(data['token'],
                              data['event_id']))


@APP.route("/event/searchbyid", methods=['POST'])
def event_searchbyid_route():
    """
    (Specifically requested by the frontend.)

    Retrieves the full information of a specific event, by its event ID; and
    append the remaining available seats (list) for that event as an extra
    key.

    HTTP request body input:
        <event_id>
            A valid event ID.
    Exceptions:
        None
    Returns:
        A dictionary with details of a single event, with the additional key
        of 'available_seats' with integer values in a list.
    Routes Page:
        EventPage.jsx
    """

    data = request.get_json()

    # Adds remaining seating to the event dictionary
    requested_event = get_event_and_seats_by_id_fixed(data['event_id'])

    # Converts local image to base64
    requested_event = convert_local_images_to_base64_in_event(requested_event)

    return dumps(requested_event)


@APP.route("/event/broadcast", methods=['POST'])
def event_broadcast_route():
    """
    The creator of an event can send a message (through email) to all users
    who have booked the event.

    HTTP request body input:
        <token>
            A valid token.
        <event_id>
            A valid event ID.
        <message>
            The (email) message to be broadcasted to the event attendees.
        <email_subject>
            The subject of the email to be sent out.
    Exceptions:
        AccessError:
        - Token is invalid for event. I.e., editor is not the creator of the
          event.
        InputError:
        - The event ID is invalid.
    Returns:
        None
    Routes Page:
        MyEvent.jsx
    """

    data = request.get_json()

    return dumps(broadcast_to_customer(data['token'],
                                       data['event_id'],
                                       data['message'],
                                       data['email_subject']))


@APP.route("/event/recommendations", methods=['POST'])
def event_recommendations_route():
    """
    Recommends events based off of a machine learning algorithm and the user's
    past events history. Is displayed on the landing page under the heading,
    'Recommends for you'.

    HTTP request body input:
        <email>
            A valid user email that is logged in.
    Exceptions:
        None
    Returns:
        A list of events (an event is a dictionary.)
    Routes Page:
        LandingPage.jsx
    """

    data = request.get_json()

    event_id_recommendations_list = give_recommendations(data['email'])  # [1, 2]
    event_list = []
    events_list_with_base64_images = []

    # Adds seating information to each event
    for event_id in event_id_recommendations_list:
        event_list.append(get_event_with_seats(event_id))

    # Converts local image to base64
    for event in event_list:
        events_list_with_base64_images.append(convert_local_images_to_base64_in_event(event))

    event_list_dumps = dumps(events_list_with_base64_images)

    return event_list_dumps


## Booking Routes ##############################################################


@APP.route("/booking/ticket", methods=['POST'])
def booking_ticket_route():
    """
    Allows the user to book ticket(s) for an event. Multiple tickets can be
    booked in one transaction, and seat selection is mandatory.

    HTTP request body input:
        <token>
            A valid user token.
        <event_id>
            The event ID that the user would like to purchase tickets for.
        <num_tickets_to_purchase>
            The number of tickets (as a total quantity) in this transaction.
        <requested_seats>
            The specific seats that the user would like to purchase (a list).
    Exceptions:
        AccessError:
        - User's token is invalid.
        InputError:
        - If the event (event_id) is invalid.
        - If the seat selection is invalid.
        - If num_tickets_to_purchase != requested_seats.
    Returns:
        A list of dictionaries, with each dictionary being one ticket.
    Routes Page:
        EventPage.jsx
    """

    data = request.get_json()

    return dumps(
        book_ticket(data['token'],
                    data['event_id'],
                    data['num_tickets_to_purchase'],
                    data['requested_seats']))


@APP.route("/booking/cancel", methods=['POST'])
def booking_cancel_route():
    """
    Allows a user to cancel a booking to an upcoming event, with several
    conditions.

    HTTP request body input:
        <token>
            A valid token.
        <event_id>
            The event ID.
        <ticket_code>
            The unique ticket code, of which to cancel.
    Exceptions:
        AccessError:
        - Only logged in users can cancel their bookings.
        - User cannot cancel a booking they did not book.
        InputError:
        - Cannot cancel a booking for an event that has started.
        - Cannot cancel a booking that is starting within 7 days.
    Returns:
        Returns an empty dictionary.
    Routes Page:
        Ticket.jsx
    """

    data = request.get_json()

    return dumps(cancel_booking(data['token'],
                                data['event_id'],
                                data['ticket_code']))


@APP.route("/user/events/booked/past", methods=['POST'])
def booking_ticket_past_route():
    """
    Gets the past tickets that a user has booked (i.e., bookings that have
    expired already).

    HTTP request body input:
        <email>
            A valid user's email.
    Exceptions:
        None
    Returns:
         A list of tickets the user have booked, only for events that haven't
         started.
    Routes Page:
        AAA
    """

    data = request.get_json()

    return dumps(user_tickets_booked_past(data['input_email']))


## User Routes #################################################################


@APP.route("/user/events/created", methods=['POST'])
def user_events_created_route():
    """
    Returns all events a user has created that have not passed.

    HTTP request body input:
        <input_email>
            The email of the user to return details of.
    Exceptions:
        AccessError:
        - If the event does not exist.
    Returns:
        A list of dictionaries of events that a user has created.
    Routes Page:
        MyEventsPage.jsx
    """

    data = request.get_json()

    user_events_list = user_events_created(data['input_email'])
    user_events_list_updated = []

    # Converts local image to base64
    for event in user_events_list:
        user_events_list_updated.append(convert_local_images_to_base64_in_event(event))

    return dumps(user_events_list_updated)


@APP.route("/user/events/created/past", methods=['POST'])
def get_user_events_created_past_route():
    """
    Given user email, returns a list of past events created by this user.

    HTTP request body input:
        <token>
            The email of the user to return details of.
    Exceptions:
        AccessError:
        - If the event does not exist.
    Returns:
        A list of dictionaries of events that a user has created that has passes.
    Routes Page:
        MyEventsPage.jsx
    """

    data = request.get_json()

    user_events_list = get_user_events_created_past(data['input_email'])
    user_events_list_updated = []

    # Converts local image to base64
    for event in user_events_list:
        user_events_list_updated.append(convert_local_images_to_base64_in_event(event))

    return dumps(user_events_list_updated)


@APP.route("/user/events/booked", methods=['POST'])
def user_events_booked_route():
    """
    Returns all events a user has booked.

    HTTP request body input:
        <input_email>
            The email of the user to return details of.
    Exceptions:
        AccessError:
        - If the event does not exist.
    Returns:
        A list of dictionaries of events that a user has booked.
    Routes Page:
        TicketPage.jsx
    """

    data = request.get_json()

    user_events_list = user_tickets_booked(data['input_email'])
    user_events_list_updated = []

    # Converts local image to base64
    for event in user_events_list:
        user_events_list_updated.append(convert_local_images_to_base64_in_event(event))

    return dumps(user_events_list_updated)


## Analytics Routes ############################################################


@APP.route("/update/attendance", methods=['POST'])
def update_attendance_route():
    """
    Updates the attendance of an event.

    HTTP request body input:
        <event_id>
            The event_id of the event.
        <actual_attendance>
            The actual_attendance of the event.
    Exceptions:
        N/A
    Returns:
        N/A
    Routes Page:
        InsightsPage.jsx
    """

    data = request.get_json()

    event_id = data['event_id']
    actual_attendance = data['actual_attendance']

    # Return a success response
    return dumps(update_attendance(event_id, actual_attendance))


@APP.route("/attendance/prediction/current", methods=['POST'])
def attendance_prediction_current_route():
    """
    Returns the attendance prediction of current events.

    HTTP request body input:
        <event_id>
            The event_id of the event.
        <actual_attendance>
            The actual_attendance of the event.
    Exceptions:
        N/A
    Returns:
        N/A
    Routes Page:
        InsightsPage.jsx
    """

    data = request.get_json()

    event_id = data['event_id']

    # Return a success response
    return dumps(str(attendance_prediction_current(event_id)))


@APP.route("/attendance/prediction/past", methods=['POST'])
def attendance_prediction_past_route():
    """
    Returns the attendance prediction of past events.

    HTTP request body input:
        <event_id>
            The event_id of the event.
        <actual_attendance>
            The actual_attendance of the event.
    Exceptions:
        N/A
    Returns:
        N/A
    Routes Page:
        InsightsPage.jsx
    """

    data = request.get_json()

    event_id = data['event_id']

    # Return a success response
    return dumps(str(attendance_prediction_past(event_id)))


@APP.route("/get/historical/attendance", methods=['POST'])
def get_historical_attendance_route():
    """
    Returns the true attendance of a past event.

    HTTP request body input:
        <event_id>
            The event_id of the event.
        <actual_attendance>
            The actual_attendance of the event.
    Exceptions:
        N/A
    Returns:
        N/A
    Routes Page:
        InsightsPage.jsx
    """

    data = request.get_json()

    event_id = data['event_id']

    # Return a success response
    return dumps(str(get_historical_attendance(event_id)))


@APP.route("/user/analytics", methods=['POST'])
def get_user_analytics_route():
    """
    Given user token, return the analytics of this account

    HTTP request body input:
        <token>
            The token of the user.
    Exceptions:
        N/A
    Returns:
        favourite_host
        favourite_event_type
        num_events_participated
    Routes Page:
        AcctInsightsPage.jsx
    """
    data = request.get_json()
    return dumps(user_analytics(data['token']))

@APP.route("/forecast/demand", methods=['POST'])
def get_forecast_demand_route():
    """
    Given an event_id, return the predicted ticket sales

    HTTP request body input:
        <event_id>
            The event_id.
    Exceptions:
        N/A
    Returns:
        predicted demand
    Routes Page:
        insightsPage.jsx
    """
    data = request.get_json()
    return dumps(str(forecast_demand(data['event_id'])))


## Review Routes ###############################################################


@APP.route("/review/post", methods=['POST'])
def review_post_route():
    """
    Customers, after attending an event they have booked, to leave a review for
    that event (one review per customer).

    HTTP request body input:
        <token>
            A valid user token.
        <event_id>
            The event ID of which to leave a review for.
        <review_content>
            The contents of the review, as a string.
    Exceptions:
        AccessError
        - If a user did not attend this event.
        - If a user has already left a review for this event.
        - If a user is trying to post a review that has not started yet.
    Returns:
        A dictionary with the keys 'thread_id' and 'event_id'. thread_id is
        nested dictionary with details of the specific review.
    Routes Page:
        LeaveComment.jsx
    """

    data = request.get_json()

    return dumps(post_review(data['token'],
                             data['event_id'],
                             data['review_content']))


@APP.route("/review/reply", methods=['POST'])
def review_reply_route():
    """
    Hosts to reply to reviews that have been left by customers for their events.

    HTTP request body input:
        <token>
            A valid user token.
        <event_id>
            The event ID of which to leave a reply to a reivew for.
        <thread_id>
            The ID of the thread (specific review) that the host will be
            replying to.
        <reply_content>
            The contents of the reply, as a string.
    Exceptions:
        AccessError
        - If the person attempting to reply to a reivew is not a host.
    Returns:
        True or False depending on whether a reply was successful.
    Routes Page:
        LeaveComment.jsx
    """

    data = request.get_json()

    return dumps(reply_review(data['thread_id'],
                              data['host_id'],
                              data['event_id'],
                              data['reply_content']))


@APP.route("/review/read", methods=['POST'])
def review_read_route():
    """
    Customers and prospective customers to read reviews, as well as host replies
    to reviews, for all events.

    HTTP request body input:
        <event_id>
            The event ID of which to read review(s) for.
    Exceptions:
        None
    Returns:
        A list of dictionaries, with each dictionary being a review (thread).
    Routes Page:
        EventPage.jsx
    """

    data = request.get_json()

    return dumps(get_reviews_of_event(data['event_id']))


## Image Routes ################################################################


@APP.route("/image/load", methods=['POST'])
def image_load_route():
    """
    (Strictly for frontend only.) Passes the local file storage path of a
    specific image to and from the database to the frontend.

    HTTP request body input:
        <image_path>
            The local file storage path of the image, relative to the root
            folder of the project, as a string.
    Exceptions:
        None
    Returns:
        The path as a string.
    Routes Page:
        EventPage.jsx
    """

    data = request.get_json()

    return dumps((data['image'],
                  data['seating_plan_image']))


@APP.route("/clear", methods=['POST'])
def image_clear_route():
    """
    (Strictly for frontend only.) Clears the user uploaded event and seating
    images in the root > frontend > src > images > upload folder.

    HTTP request body input:
        None
    Exceptions:
        None
    Returns:
        True of cleared successfully.
    Routes Page:
        EventPage.jsx
    """
    
    return dumps(clear_user_images_uploads())


## Helpers #####################################################################


def replace_value_by_key(dictionary, target_key, new_value):
    """
    Replaces a value of a target key in a (nested) dictionary. Edits the
    dictionary in place.

    Parameters:
        <dictionary>
            The target dictionary (can be nested).
        <target_key>
            The target key to edit its value (can be nested).
        <new_value>
            The new value to replace the old value.
    Returns:
        None
    """

    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if key == target_key:
                dictionary[key] = new_value
            elif isinstance(value, (dict, list)):
                replace_value_by_key(value, target_key, new_value)
    
    elif isinstance(dictionary, list):
        for item in dictionary:
            if isinstance(item, (dict, list)):
                replace_value_by_key(item, target_key, new_value)


def find_value_by_key(dictionary, target_key):
    """
    Finds a specific value in a dictionary (if available), and return it.

    Parameters:
        <dictionary>
            The target dictionary (can be nested).
        <target_key>
            The target key (can be nested).
    Returns:
        Either the value of the target key if found, or None.
    """

    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                found_value = find_value_by_key(value, target_key)
                if found_value is not None:
                    return found_value
                
    elif isinstance(dictionary, list):
        for item in dictionary:
            if isinstance(item, (dict, list)):
                found_value = find_value_by_key(item, target_key)
                if found_value is not None:
                    return found_value
    
    return None


def convert_local_images_to_base64_in_event(event):
    """
    Given an event, converts all of the images within from local storage format
    into a base64 data URL format, ready to be sent to the frontend. The
    conversion converts both the event image, and the event seating plan.

    Parameters:
        <event>
            The target event to change the images format.
    Returns:
        An updated event dictionary.
    """

    # Finds the existing local images (e.g., event1.jpeg)
    image_file = find_value_by_key(event, 'image')
    seating_file = find_value_by_key(event, 'seating_plan_image')
    
    event_copy = event

    # Replaces them with their base64 data URL equivalent
    replace_value_by_key(event_copy, 'image', encode_to_base64(image_file))
    replace_value_by_key(event_copy, 'seating_plan_image', encode_to_base64(seating_file))

    return event_copy


## Please Do Not Edit Below This ###############################################


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(debug=False, port=src.config.port)     # Do not edit this port
