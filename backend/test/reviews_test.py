import pytest
from src.auth import auth_login, auth_register
from src.event import create_event, get_event_database, get_past_events
from src.errors import InputError, AccessError
from test.other import clear
from src.booking import book_ticket
from src.data import events, db_state
from src.reviews import has_user_attended_event, post_review, is_host_of_event, reply_review, get_reviews_of_event

def test_attended_event_true():
    """
    This tests the has_user_attended_event function
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("registerme@gmail.com", "1234567")
    
    # Create first event
    create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")
    
    # user books event 1
    book_ticket(login_success['token'], 1, 1, [3])
    
    # event is in the past so user has attended the event
    assert has_user_attended_event(login_success['token'], 1) == True

    create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2000 12 15 12 15 00", "2000 12 15 12 20 00", 20, 20, 0.0, 0.0, 0.0, "church hall photo", 20, 
                 "seats image")

    # because user hasn't booked the event
    assert has_user_attended_event(login_success['token'], 2) == False

    # book user for event 2
    book_ticket(login_success['token'], 2, 1, [20])
    
    # since the event has already passed, user has attended the event
    assert has_user_attended_event(login_success['token'], 2) == True


def test_attended_event_false():
    """
    This tests the has_user_attended_event function
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("registerme@gmail.com", "1234567")
    
    # Event hasn't started
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2026 09 15 12 30 12", "2026 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 1, [3])
    
    assert has_user_attended_event(login_success['token'], event1_id) == False


def test_leave_review():
    clear()
    # 1 event for 2 customers
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    registration2 = auth_register("luya.pan@student.unsw.edu.au", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("luya.pan@student.unsw.edu.au", "hahaha")
    
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    book_ticket(login_success['token'], event1_id, 1, [3])
    book_ticket(login_success2['token'], event1_id, 1, [10])
    
    assert has_user_attended_event(login_success['token'], event1_id) == True
    assert has_user_attended_event(login_success2['token'], event1_id) == True
    
    # post a review
    post_review(login_success['token'], event1_id, "Really loved the repertoire")
    
    past_events = get_past_events()
    review = []
    for event in past_events:
        if event['event_id'] == event1_id:
            review = event['reviews']
    review_string = ''
    for rev in review:
        if rev['customer_email'] == "luyapan1202@gmail.com":
            review_string = rev['review_content']
            
    assert review_string == "Really loved the repertoire"
        
    # try the get_reviews_of_event function
    all_reviews_event1 = get_reviews_of_event(event1_id)
    assert all_reviews_event1[0]['review_content'] == "Really loved the repertoire"
    
    post_review(login_success2['token'], event1_id, "Lah lah lah")
    past_events = get_past_events()
    review = []
    for event in past_events:
        if event['event_id'] == event1_id:
            review = event['reviews']
    review_string = ''
    for rev in review:
        if rev['customer_email'] == "luya.pan@student.unsw.edu.au":
            review_string = rev['review_content']
            
    assert review_string == "Lah lah lah"

    review_string1 = False
    review_string2 = False
    # try the get_reviews_of_event function
    all_reviews_event1 = get_reviews_of_event(event1_id)
    for rev in all_reviews_event1:
        if rev['review_content'] == "Really loved the repertoire":
            review_string1 = True
        if rev['review_content'] == "Lah lah lah":
            review_string2 = True
    assert review_string1 == True
    assert review_string2 == True


def test_leave_review_non_customer():
    """
    Tests the post review function when a user is not a customer but still tries
    to leave a review
    """
    clear()
    # 1 event for 2 customers
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")

    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']

    assert has_user_attended_event(login_success['token'], event1_id) == False
    
    with pytest.raises(AccessError):
        # user is not a customer
        post_review(login_success['token'], event1_id, "random string")


def test_review_two_events():
    """
    Test two users book for two different events and are able to leave a review for each event
    """
    clear()
    # customers book for two events
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    # Create first event
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    event2_id = create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                 "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                 "seats image")['event_id']

    # user 1 books event 1
    book_ticket(login_success['token'], event1_id, 1, [3])
    
    # user 2 books event 2
    book_ticket(login_success2['token'], event2_id, 1, [10])
    
    assert has_user_attended_event(login_success['token'], event1_id) == True
    assert has_user_attended_event(login_success2['token'], event2_id) == True
    
    
    # test post review function for user 1. user 1 can leave 1 review for event 1
    # post a review to event 1
    post_review(login_success['token'], event1_id, "Really loved the repertoire haha")
    past_events = get_past_events()
    review = []
    for event in past_events:
        if event['event_id'] == event1_id:
            review = event['reviews']
    review_string = ''
    for rev in review:
        if rev['customer_email'] == "luyapan1202@gmail.com":
            review_string = rev['review_content']
            
    assert review_string == "Really loved the repertoire haha"
    
    all_reviews_event1 = get_reviews_of_event(event1_id)
    assert all_reviews_event1[0]['review_content'] == "Really loved the repertoire haha"
    
    # now check if the review database for event 2 is indeed empty
    review = []
    for event in past_events:
        if event['event_id'] == event2_id:
            review = event['reviews']
    review_string = ''
    for rev in review:
        if rev['customer_email'] == "scanlulu@gmail.com":
            assert rev['review_content'] == []
    
    # testing the get_reviews_of_event() function
    all_reviews_event2 = get_reviews_of_event(event2_id)
    assert all_reviews_event2 == []
    
    # user 1 cannot post review to event 2
    with pytest.raises(AccessError):
        # user is not a customer
        post_review(login_success['token'], event2_id, "My review haha")
    
    # let user 2 post a review for event 2
    post_review(login_success2['token'], event2_id, "My review haha")
    review = []
    for event in past_events:
        if event['event_id'] == event2_id:
            review = event['reviews']
    review_string = ''
    for rev in review:
        if rev['customer_email'] == "scanlulu@gmail.com":
            assert rev['review_content'] == "My review haha"
    
    all_reviews_event2 = get_reviews_of_event(event2_id)
    assert all_reviews_event1[0]['review_content'] == "Really loved the repertoire haha"

def test_leave_review_twice():
    clear()
    # customers book for two events
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    # Create first event
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']

    # user 1 books event 1
    book_ticket(login_success['token'], event1_id, 1, [3])
    # leave thr first review
    post_review(login_success['token'], event1_id, "First review")
    
    with pytest.raises(AccessError):
        # user cannot comment the second time
        post_review(login_success['token'], event1_id, "Can't comment a second time")

def test_leave_review_not_started():
    """
    This tests the behaviour of post_review() when an event hasn't started. 
    """
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    # Create first event
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2025 09 15 12 30 12", "2025 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']

    # user 1 books event 1
    book_ticket(login_success['token'], event1_id, 1, [3])

    with pytest.raises(AccessError):
        # can't leave review for an event that hasn't started
        post_review(login_success['token'], event1_id, "Sorry, you cannot post reviews to an unstarted event!")

def test_is_host_of_event():
    """
    This tests the is_host_of_event() function
    """

    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    # Create first event
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2025 09 15 12 30 12", "2025 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    # user 1 is the host of event 1
    assert is_host_of_event("luyapan1202@gmail.com", event1_id) == True
    
    # user 2 is not the host of event 1
    assert is_host_of_event("scanlulu@gmail.com", event1_id) == False


def test_reply_second_time():
    """
    Hosts can only reply to a review once. This tests the correctness of this behaviour
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("registerme@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    # user 2 books a ticket for event 1
    book_ticket(login_success2['token'], event1_id, 1, [3])
    
    thread_id = post_review(login_success2['token'], event1_id, "woof")['thread_id']
    
    # reply for the first time
    reply_review(thread_id, "registerme@gmail.com", event1_id, "my reply")

    with pytest.raises(InputError):
        # cannot reply a second time
        reply_review(thread_id, "registerme@gmail.com", event1_id, "cannot reply")

def test_reply_non_host():
    """
    Test catching error for non host attempting to reply to reviews
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("registerme@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    # user 2 books a ticket for event 1
    book_ticket(login_success2['token'], event1_id, 1, [3])
    
    thread_id = post_review(login_success2['token'], event1_id, "woof")['thread_id']
    
    with pytest.raises(AccessError):
    # non host user 2 tries to reply to reviews, should raise an error
        reply_review(thread_id, "scanlulu@gmail.com", event1_id, "my reply")


def test_reply_review():
    """
    Test host successfully replying to a review
    """
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    # Create first event
    event_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    book_ticket(login_success2['token'], 1, 1, [3])
    # user 2 leaves a comment
    thread_id = post_review(login_success2['token'], 1, "loved it")['thread_id']
    
    # host replies to the review
    reply_review(thread_id, "luyapan1202@gmail.com", event_id, "my reply")
    
    all_reviews = get_reviews_of_event(event_id)
    assert all_reviews[0]['host_reply'] == "my reply"
    assert all_reviews[0]['host_reply_timestamp'] != ''
    
def test_reply_review():
    """
    # Test hosts successfully replying to multiple events
    """
    clear()
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    registration3 = auth_register("scanlulu2@gmail.com", "hahaha", "Pomi", "Kim",
                                  "Pomi Kim", "1111222233334444", 12, 2026, "322")
    login_success3 = auth_login("scanlulu2@gmail.com", "hahaha")
    
    # Create first event
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    event2_id = create_event(login_success['token'], "Christmas Carol 2023", "Presented by POMI Church", "Seasonal", "POMI Church, Randwick",
                "Online", "POMI church", "2018 09 15 16 30 12", "2018 09 15 16 35 12", 10 , 10, 0.0, 0.0, 0.0, "church hall photo", 10, 
                "seats image")['event_id']
    
    # user 2 books a ticket to event 1
    book_ticket(login_success2['token'], event1_id, 1, [3])
    
    # user 3 books a ticket to event 2
    book_ticket(login_success3['token'], event2_id, 1, [10])
    # user 3 also books a ticket to event 1
    book_ticket(login_success3['token'], event1_id, 1, [100])
    
    # user 2 leaves a comment to event 1
    thread1_id = post_review(login_success2['token'], event1_id, "loved it")['thread_id']
    # host replies to the review
    reply_review(thread1_id, "luyapan1202@gmail.com", event1_id, "my reply")
    
    # user 3 leaves a comment to event 1
    thread2_id = post_review(login_success3['token'], event1_id, "review2")['thread_id']
    reply_review(thread2_id, "luyapan1202@gmail.com", event1_id, "my reply2")
    
    reply_string1 = False
    reply_string2 = False
    # try the get_reviews_of_event function
    all_reviews_event1 = get_reviews_of_event(event1_id)
    for rev in all_reviews_event1:
        if rev['host_reply'] == "my reply":
            reply_string1 = True
        if rev['host_reply'] == "my reply2":
            reply_string2 = True
    assert reply_string1 == True
    assert reply_string2 == True

    # +++ user 3 leaves comment for event 2
    thread3_id = post_review(login_success3['token'], event2_id, "loved it")['thread_id']
    
    reply_review(thread3_id, "luyapan1202@gmail.com", event2_id, "my reply3")
    
    # check if host review has been added to the thread
    all_reviews_event2 = get_reviews_of_event(event2_id)
    assert all_reviews_event2[0]['host_reply'] == "my reply3"



def test_reply_non_host():
    """
    Test catching error for non host attempting to reply to reviews
    """
    clear()
    registration = auth_register("registerme@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    login_success = auth_login("registerme@gmail.com", "1234567")
    
    registration2 = auth_register("scanlulu@gmail.com", "hahaha", "Peter", "Pan",
                                  "Peter Pan", "1111222233334444", 12, 2025, "321")
    login_success2 = auth_login("scanlulu@gmail.com", "hahaha")
    
    event1_id = create_event(login_success['token'], "Debussy's Nocturnes", "POMI Symphony Orchestra, Chopin", "Music", "Concert Hall, Sydney Opera House",
                 "Online", "POMI orchestra", "2020 09 15 12 30 12", "2020 09 15 12 45 12", 100, 100, 35.5, 35.5, 40, "concert hall photo", 100, 
                 "seats image")['event_id']
    
    # user 2 books a ticket for event 1
    book_ticket(login_success2['token'], event1_id, 1, [3])
    
    thread_id = post_review(login_success2['token'], event1_id, "woof")['thread_id']
    
    with pytest.raises(AccessError):
    # non host user 2 tries to reply to reviews, should raise an error
        reply_review(thread_id, "scanlulu@gmail.com", event1_id, "my reply")