#!/usr/bin/env python3
# import importer
import sys
import os
import os.path
import colorsys
import datetime
import datefinder
from termcolor import colored
from dateutil import parser
import pickle
import pickle
from tabulate import tabulate
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date
from datetimerange import DateTimeRange
import json
import argparse
import textwrap
from uuid import uuid4
from tqdm import tqdm


CLINIC_CALENDAR_ID = 'c_ckbi989o2ujtcvtummcm75qjqo@group.calendar.google.com'
CREDENTIALS_FILE = 'client_secret.json'
CLINIC_EVENTS = 'clinic.json'
USER_EVENTS = 'patient.json'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+02:00'
SCOPES = ['https://www.googleapis.com/auth/calendar']


#althotse
def client_secret():
    with open("client_secret.json",'r') as secret:
        a = secret.read()
        secret.close()
        return a
client_secret()

# jmohale
def get_calendar_service():
    """
    Create the calendar api service
    :return service: google calendar api service
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())    

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            # creds = flow.run_console()
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def book_slot(service):
    """
    books a slot by adding an attendee to the event slot
    :param service: calendar api service

    """

    events = file_obj(CLINIC_EVENTS)
    event_id_list = [event['id'] for event in events]
    print(view_available_slots(), '\n')
    event_id = input('Please copy the event id that you want to book: ')
    # Get email of the patient
    patient_email = service.calendarList().get(
        calendarId='primary').execute()['id']

    try:
        attendee_info = service.events().get(calendarId=CLINIC_CALENDAR_ID,
                                             eventId=event_id).execute()['attendees']
        if len(attendee_info) == 2:
            print("Sorry the event is fully booked")
        elif patient_email in [attendee['email'] for attendee in attendee_info]:
            print('you cant book your own slot.')
        elif check_calendar_conflict(event_id):
            print(
                "You already have an event at this time slot. Please choose another slot!")
        else:
            event = service.events().get(calendarId=CLINIC_CALENDAR_ID,
                                         eventId=event_id).execute()
            # print(event)
            event['attendees'].append(
                {'email': patient_email, 'responseStatus': 'accepted'})
            #
            try:
                service.events().patch(calendarId=CLINIC_CALENDAR_ID, eventId=event_id,
                                       body=event, sendUpdates='all').execute()
                return print(f"Slot {event_id} successfully booked")
            except HttpError as e:
                return print("An error occurred while trying book the event.Please try again!")
    except HttpError as e:
        return print("You have entered an incorrect event_id")
    # if event_id not in event_id_list:
    #     print("You have entered an incorrect event_id")


def check_calendar_conflict(event_id):
    """
    prevent double booking of events
    :param event_id: id of the evnets that is currently being booked
    :return: True if there is an event ooked at that time slot else False

    """

    # get the events data from user and clinic calendar
    clinic_events = file_obj(CLINIC_EVENTS)
    user_events = file_obj(USER_EVENTS)
    # extract start time from clinic calendar
    str_time = [(event['start']['dateTime'], event['end']['dateTime'])
                for event in clinic_events if event['id'] == event_id]
    if len(str_time) != 0:
        start_time = datetime.strptime(str_time[0][0], DATE_FORMAT)
        end_time = datetime.strptime(str_time[0][1], DATE_FORMAT)

        # check for conflicts
        for event in user_events:
            if start_time < datetime.strptime(event['start']['dateTime'], DATE_FORMAT) < end_time:
                print(event['id'])
                return True
            elif start_time < datetime.strptime(event['end']['dateTime'], DATE_FORMAT) < end_time:
                return True

    return False
    # return True if get_events(start_time, end_time, event_id) else False


def file_obj(filename):
    """
    loads data from a json file
    :param filename: the file data is read from
    :return data: list of calendar data
    """

    with open(filename) as f:
        data = json.load(f)
    return data



def view_available_slots():
    """
    The view_available_slots() function returns tabulated clinic calendar data. 
    """
    # download_event(service)
    with open(CLINIC_EVENTS) as events:
        data = json.load(events)

    # print('-'*95,'\n',colored('{0:^50}'.format('AVAILABLE SLOTS'), 'blue'),'\n', '-'*95)

    # print(colored('{0:<15}{1}{2:>15}{3:>32}{4:>30}'.format('CLINICIAN','TOPIC','TIME','EVENT ID', 'AVAILABLE'), 'red'),'\n', '-'*95)
    tab_data = []
    color_header = [colored('CLINICIAN', 'magenta'), colored('TOPIC', 'magenta'), colored('DATE', 'magenta'), colored(
        'TIME', 'magenta'), colored('EVENT_ID', 'magenta'), colored('AVAILABLE', 'magenta')]
    for event in data:
        tab_data.append(format_events(event))
        # print('{0:<15}{1:<15}{2:>15}{3:>30}{4:>7}'.format(creator, summary, start+'-'+end, event_id, slot_open))
    tab_data.sort(key=lambda x: x[2])
    print('\n')
    return tabulate(tab_data, headers=color_header, tablefmt='github')

    # for id in tab_data:
    #     print("./booking.py book_slot "+id[4])
    # check_calendar_conflict('6jrkcljpta940ej31s492nm8fd')


def format_events(event):
    """
    The format_events() function appends calendar events to a list
    in a formatted structure.
    returns: A list containing the formatted events.
    """
    rows = []
    rows.append(colored(event['creator']['email'].split('@')[0], 'cyan'))
    rows.append(colored(event['summary'], 'cyan'))
    start = datetime.strptime(
        (event['start']['dateTime']), DATE_FORMAT).strftime(
        "%I:%M:%S %p")
    end = datetime.strptime(
        (event['end']['dateTime']), DATE_FORMAT).strftime(
        "%I:%M:%S %p")
    rows.append(colored(datetime.strptime(
        event['start']['dateTime'], DATE_FORMAT).strftime("%d %B %Y"), 'cyan'))

    rows.append(colored(start + '-' + end, 'cyan'))
    rows.append(colored(event['id'], 'cyan'))

    rows.append(colored('YES', 'green') if 'attendees' in event.keys() and len(
        event['attendees']) < 2 else colored("NO", 'red'))
    return rows


def download_event(service):
    """
    Get the calendar events for the next 7 days
    :param service: calendar api service
    :param data_file: local json file to store calendar events
    :param calendar_id: events to be downloaded from the calendar whose id is calendar_id
    :return data_file: a json file with calendar events

    """
    min_range = datetime.now().replace(
        hour=0, minute=0, second=1)
    max_range = min_range.replace(hour=23, minute=59, second=59) + timedelta(6)
    min_range = min_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    max_range = max_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")

    patient_events = service.events().list(
        calendarId='primary', timeMin=min_range, timeMax=max_range).execute().get('items', [])
    clinic_events = service.events().list(
        calendarId=CLINIC_CALENDAR_ID, timeMin=min_range, timeMax=max_range).execute().get('items', [])

    p_obj = json.dumps(check_recurring_events(
        service, patient_events), indent=4)
    c_obj = json.dumps(clinic_events, indent=4)
    # save the the calendar events
    with open('patient.json', 'w') as p_data, open("clinic.json", 'w') as c_data:
        # datafile.write(f_obj)
        p_data.write(p_obj)
        c_data.write(c_obj)


def check_recurring_events(service, user_events):
    # duplicate of occurrence events
    """
    :param service: calendar api service
    :param user_events: events created by the user
    :return: add_events: returns updated user_events downloaded into a list 
    """
    add_events = user_events

    for event in user_events:
        if 'recurrence' in event:
            new_events = service.events().instances(
                calendarId='primary', eventId=event['id']).execute().get('items', [])
            for item in new_events:
                add_events.append(item)

    return add_events


# smabitse


def check_volunteer_slot_conflict(data_file, start_date_time):
    """
    The check_volunteer_slot_conflict() function checks if the entered volunteer slot time is available.\n
    :params: data_file: 
    :params: start_date_time: date time format entered by the user
    :return: returns True for a List value [bool,str,str].
    """

    with open(data_file) as file:
        event_data = json.load(file)

    time_format = "%Y-%m-%dT%H:%M:%S+02:00"
    end_date_time = start_date_time + timedelta(minutes=90)
    start_date_time_str = start_date_time.strftime(time_format)
    end_date_time_str = end_date_time.strftime(time_format)

    for event in event_data:
        event_start = event['start']['dateTime']
        event_end = event['end']['dateTime']
        event_start_obj = datetime.strptime(event_start, time_format)
        event_end_obj = datetime.strptime(event_end, time_format)
        event_start_obj_str = event_start_obj.strftime(
            "[%A]\t[%d-%m-%Y]\t[%H:%M")
        event_end_obj_str = event_end_obj.strftime(" - %H:%M].")
        volunteer_slot_time_range = DateTimeRange(
            start_date_time_str, end_date_time_str)

        if event_start in volunteer_slot_time_range:
            response1 = "\n'" + colored(str(event['summary']), "red", attrs=['bold', 'underline']) \
                        + "' event time conflict found." \
                        + "\nThe events start-time is in your volunteer slots proposed 90-minute time range."
            response2 = "\t-> '" + str(event['summary']) + "' event info: " \
                        + event_start_obj_str + event_end_obj_str
            return [False, response1, response2]
        if event_end in volunteer_slot_time_range:
            response1 = "\n'" + colored(str(event['summary']), "red", attrs=['bold', 'underline']) \
                        + "' event time conflict found." \
                        + "\nThe events end-time is in your volunteer slots proposed 90-minute time range."
            response2 = "\t-> '" + str(event['summary']) + "' event info: " \
                        + event_start_obj_str + event_end_obj_str
            return [False, response1, response2]
    return [True]


def volunteer_slot(service):
    """
    The volunteer_slot() function creates the 90-min slot by creating three
    consecutive events in the Volunteer and the Code Clinic google calendars.\n
    First it checks if there's any conflicts regarding the volunteers entered time.
    :params: service: creates a slot if check_volunteer_slot_conflict function returns a True
    """
    clinician_email = service.calendarList().get(
        calendarId='primary').execute()['id']
    print("\nPlease enter your volunteer slots DATE and START-TIME.")
    print(colored("Note", attrs=['bold'])
          + ", the duration of the volunteer slot will be "
          + colored("90-minutes", attrs=['bold']) + ".")
    input_time = input(
        colored("Day Month Time - [14 dec 14:30]: ", 'yellow', attrs=['bold']))

    start_date_time = list(datefinder.find_dates(input_time))[0]
    start_date_time_str = start_date_time.strftime(
        "%Y-%m-%dT%H:%M:%S+02:00")

    # Check for conflicting times.
    create_volunteer_slot = check_volunteer_slot_conflict(
        "patient.json", start_date_time)

    if create_volunteer_slot[0] == True:
        summary = input("\nPlease enter the slot summary: ")
        description = input("Please enter the slot description: ")
        print('\n')

        increment_time = 30
        number_of_slots = 0

        end_date_time = start_date_time + timedelta(minutes=increment_time)
        end_date_time_str = end_date_time.strftime("%Y-%m-%dT%H:%M:%S+02:00")

        google_meet_id = uuid4().hex

        for i in tqdm(range(3)):
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_date_time_str,
                    'timeZone': 'Africa/Johannesburg',
                },
                'end': {
                    'dateTime': end_date_time_str,
                    'timeZone': 'Africa/Johannesburg',
                },
                'attendees': [
                    {
                        'email': clinician_email,
                        'responseStatus': 'accepted'
                    }
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
                'conferenceData': {"createRequest": {"requestId": google_meet_id,
                                                     "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
            }
            try:
                event = service.events().insert(calendarId=CLINIC_CALENDAR_ID,
                                                body=event, conferenceDataVersion=1).execute()
                start_date_time = start_date_time + \
                    timedelta(minutes=increment_time)
                start_date_time_str = start_date_time.strftime(
                    "%Y-%m-%dT%H:%M:%S+02:00")
                end_date_time = end_date_time + \
                    timedelta(minutes=increment_time)
                end_date_time_str = end_date_time.strftime(
                    "%Y-%m-%dT%H:%M:%S+02:00")
                number_of_slots += 1
            except HttpError as e:
                print(e)
        if number_of_slots == 3:
            print(colored("[", 'green', attrs=['bold'])
                  + colored(summary, 'yellow', attrs=['bold'])
                  + colored("]", 'green', attrs=['bold']) +
                  colored(" [", 'green', attrs=['bold'])
                  + colored(description, 'yellow', attrs=['bold'])
                  + colored("]", 'green', attrs=['bold']))
            print(colored('Your volunteer slot for [', 'green', attrs=['bold'])
                  + colored(summary, 'yellow', attrs=['bold'])
                  + colored('] was successfully created.\n', 'green', attrs=['bold']))
        elif number_of_slots != 3:
            print(colored('An issue has occurred.\nNot all three events were created.\n',
                          'red', attrs=['bold', 'underline']))
        download_event(service)
    elif create_volunteer_slot[0] == False:
        print(create_volunteer_slot[1])
        print(create_volunteer_slot[2])
        print(colored("\nPlease select a different time for your volunteer slot.\n",
                      'blue', attrs=['bold', 'underline']))


# lmduduzi


def sorted_information_cancel_slot(final_lis, events):
    """This function return a dictionary with information sorted accordingly"""
    
    count = 0
    event_count = 0
    for events_available in events['items']:
        clin_name = events_available['creator']['email'].split('@')[0]
        evnt_topic = events_available['summary']
        event_temp = {'topic': evnt_topic, 'Clinician name': clin_name, 'event id': [], 'Status': [],
                      'Date and time': [], 'Time': []}

        for event_details in events['items']:
            if events_available['creator']['email'].split('@')[0]== clin_name and event_details['summary'] == evnt_topic:
                event_temp['event id'].append(event_details['id'])
                if len(event_details['attendees']) == 1:
                    status = colored(max_display('slot Open'), 'green')
                elif len(event_details['attendees']) == 2:
                    status = colored(max_display('slot Booked'), 'red')
                event_temp['Status'].append(status)
                extracted_date = str(event_details['start']['dateTime'])
                end_time = str(event_details['end']['dateTime'])
                temp_date = extracted_date[:10]
                start_time = extracted_date[11:-9]
                end_time = end_time[11:-9]
                event_temp['Date and time'].append(get_date(temp_date))
                event_temp['Time'].append(f'{start_time} to {end_time}')
        if event_temp in final_lis:
            continue
        else:
            final_lis.append(event_temp)
    return final_lis


def sorted_information(final_list, cal_events):
    '''This function takes two parameters the list and the calander info and puts
        them in a dictionary in a sorted way and when done append that dictionary to
    the list and returns  that list when it is done'''
    for events_available in cal_events['items']:
        clin_name = events_available['creator']['email'].split('@')[0]
        evnt_topic = events_available['summary']
        event_temp = {'topic': evnt_topic, 'Clinician name': clin_name,
                      'event id': [], 'Status': [], 'Date and time': [], 'Time': []}
        
        for event_details in cal_events['items']:
            if events_available['creator']['email'].split('@')[0] == clin_name and event_details['summary'] == evnt_topic:
                event_temp['event id'].append(event_details['id'])
                if len(event_details['attendees']) == 1:
                    status = colored(max_display('slot Open'), 'green')
                    # status = max_display('slot Open')

                elif len(event_details['attendees']) == 2:
                    status = colored(max_display('slot Booked'), 'red')
                    # status = max_display('slot Open')
                event_temp['Status'].append(status)
                extracted_date = str(event_details['start']['dateTime'])
                end_time = str(event_details['end']['dateTime'])
                temp_date = extracted_date[:10]
                start_time = extracted_date[11:-9]
                end_time = end_time[11:-9]
                event_temp['Date and time'].append(get_date(temp_date))
                event_temp['Time'].append(f'{start_time} to {end_time}')

        if event_temp in final_list:
            continue
        else:

            final_list.append(event_temp)
    return final_list


def display_table_and_information_no_return(sorted_events):
    '''This function is specific to cancel_slot,Its displays the information provided by the list  in a table'''
    count = 0
    for events_list in sorted_events:
        if len(events_list['event id']) == 1:
            display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status'][0],
                                 events_list['event id'][0], events_list['Date and time'][0], events_list['Time'][0],
                                 count)
            print(colored("~" * 154, 'blue'))
        elif len(events_list['event id']) == 2:
            for events in range(2):
                if events == 0:
                    display_rows_and_col_one(events_list['Status'][events], events_list['event id'][events],
                                             events_list['Time'][events], 0)
                if events == 1:
                    display_rows_and_col(events_list['topic'], events_list['Clinician name'],
                                         events_list['Status'][events], events_list['event id'][events],
                                         events_list['Date and time'][events], events_list['Time'][events], count)
                print(colored("~" * 154, 'blue'))
        else:
            for events in range(len(events_list['event id'][0]) - 1):
                if events == 0 or events == 2:
                    display_rows_and_col_one(events_list['Status'][events], events_list['event id'][events],
                                             events_list['Time'][events], 0)
                elif events == 1:
                    display_rows_and_col(events_list['topic'], events_list['Clinician name'],
                                         events_list['Status'][events], events_list['event id'][events],
                                         events_list['Date and time'][events], events_list['Time'][events], count)
            print(colored("~" * 154, 'blue'))
        count += 1


def check_the_id(events):
    '''This function takes the eventId provided by the user and check if it is valid and return it if true '''
    # print(len(events[0]['event id']))
    event_id = input(
        'Please copy & paste the event id that you want to cancel: ')
    while True:
        for count in events:
            if event_id in count['event id']:
                return event_id
        else:
            print('Please type or copy the correct event Id')
            event_id = input(
                'Please copy & paste the event id that you want to cancel: ')


def display_table_and_information(list_events):
    '''This function extract the information from the calendar and display that information
    accordingly and returns the selected event ID '''
    count = 0
    for events_list in list_events:
        if len(events_list['event id']) == 1:
            display_rows_and_col(events_list['topic'],events_list['Clinician name'],events_list['Status'][0],events_list['event id'][0],events_list['Date and time'][0],events_list['Time'][0],count)
            print(colored("~"*154,'blue'))
        elif len(events_list['event id']) == 2:
            for events in range(2):
                if events == 0:
                    display_rows_and_col_one(events_list['Status'][events],events_list['event id'][events],events_list['Time'][events],0)
                if events == 1:
                    display_rows_and_col(events_list['topic'],events_list['Clinician name'],events_list['Status'][events],events_list['event id'][events],events_list['Date and time'][events],events_list['Time'][events],count)
            print(colored("~"*154,'blue')) 
        else:
            for eventy in range(0,3):
                if eventy == 0 or eventy == 2:
                    display_rows_and_col_one(events_list['Status'][eventy],events_list['event id'][eventy],events_list['Time'][eventy],0)
                elif eventy == 1:
                    display_rows_and_col(events_list['topic'],events_list['Clinician name'],events_list['Status'][eventy],events_list['event id'][eventy],events_list['Date and time'][eventy],events_list['Time'][eventy],count)   
            print(colored("~"*154,'blue'))
        count += 1
    result  = check_the_id(list_events)
    return result


def get_date(str_date):
    '''this function take a string of date and return that date in a formated way'''
    for g in datefinder.find_dates(str(str_date)):
        date = g
    date = f"{date.year} {date.strftime('%b')} {date.day}"
    return date


def max_display(name):
    '''This function take a string and makes  sure that the lenght is always 26  '''
    max_char_lnght = 26
    empty_char = ' '
    lenghth_name = len(name)
    if lenghth_name > max_char_lnght:
        return name[:26]
    elif lenghth_name < max_char_lnght:
        count = max_char_lnght - lenghth_name
    else:
        return name
    for lngth in range(count):
        name = name + empty_char
    return name


def get_number(events_lenght):
    '''This function checks the number provided by the user and return the number if it is correct'''
    print("Note: you can't delete that slot if its has been booked")
    event_number = input(
        "Please choose a number of the event that you want to remove :")
    while True:
        if event_number.isdigit() == True and 0 <= int(event_number) <= events_lenght:
            return int(event_number)
        else:
            print('Please make sure that it is a number')
            event_number = input(
                "Please choose a number of the event that you want to remove :")


def display_table_header():
    '''This function displays the header of the table which is responsible for displaying the information'''
    print(colored("~" * 154, 'blue'))
    print(
        f'  {colored(max_display("Topic/specialty"), "blue")}{colored("|", "blue")}{colored(max_display(" Clinician Name"), "blue")}{colored("|", "blue")}{colored(max_display(" Event status"), "blue")}{colored("|", "blue")}{colored(max_display(" event ID"), "blue")}{colored("|", "blue")}{colored(max_display(" Date"), "blue")}{colored("|", "blue")}{colored(max_display(" Time"), "blue")}')
    print(colored("~" * 154, 'blue'))


def display_rows_and_col(event_topic, event_Clinician_name, event_status, event_id, event_date, event_time, count):
    '''This functions displays the information  supplied to it by parameters '''
    print(
        f"{colored(count, 'blue')}.{colored(max_display(event_topic))}{colored('|', 'blue')}{colored(max_display(event_Clinician_name))}{colored('|', 'blue')}{(colored(event_status))}{colored('|', 'blue')}{colored(max_display(event_id))}{colored('|', 'blue')}{colored(max_display(event_date))}{colored('|', 'blue')}{colored(max_display(event_time))}")


def display_rows_and_col_one(event_status, event_id, event_time, count):
    '''This function is a duplicated of the display_rows_and_col function but
    this one does not display duplicated info instant  in replace them with a blank space  '''
    count
    print(
        f"{max_display(' ')}  {colored('|', 'blue')}{max_display(' ')}{colored('|', 'blue')}{colored(event_status)}{colored('|', 'blue')}{colored(max_display(event_id))}{colored('|', 'blue')}{max_display(' ')}{colored('|', 'blue')}{colored(max_display(event_time))}")


def booking_cancalation(service):
    """This function cancels the second attendee of the event if the emails are the same"""
    page_token = None
    all_event = []
    event_id_andstatus = []
    min_range = datetime.now().replace(
        hour=0, minute=0, second=1)
    max_range = min_range.replace(hour=23, minute=59, second=59) + timedelta(6)
    min_range = min_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    max_range = max_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")

    events = service.events().list(calendarId=CLINIC_CALENDAR_ID ,
                                   pageToken=page_token,timeMin=min_range ,timeMax=max_range).execute()
    user_details = service.events().list(
        calendarId='primary', pageToken=page_token,timeMin = min_range ,timeMax = max_range).execute()
    
    events_2 = events
    if len(events['items']) == 0:
        return print(colored("Sorry there are no available slots open to cancel for now", "red"))
    else:
        display_table_header()
        all_events = sorted_information(all_event, events)
        event_ID = display_table_and_information(all_events)
        

    for v in events_2['items']:
        if event_ID == v['id'] and len(v['attendees']) == 2:
            if v['attendees'][1]['email'] == user_details['summary']:
                clinician_email = v['attendees'][0]['email']
            elif v['attendees'][1]['email'] != user_details['summary']:
                return print('Sorry your email does not match with the attendee')
        elif event_ID == v['id'] and len(v['attendees']) == 1:
            return print(colored('Sorry that slot is empty','red'))


    event = {
        'attendees': [{'email': clinician_email, 'responseStatus': 'accepted'}, ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    yes = ['Y', 'y', 'yes']
    no = ['N', 'n', 'no']
    final_answer = input(
        'Are you sure you want to cancel your booking(Y/N) : ')
    while True:
        if final_answer.isalpha() == True:
            final_answer = final_answer.lower()
        if final_answer in yes:
            service.events().patch(calendarId=CLINIC_CALENDAR_ID, eventId=event_ID,
                                   body=event, sendUpdates='all').execute()
            return print('booking canceled')
        if final_answer in no:
            return print('almost canceled your booking')
        else:
            print('Please type the correct answer')
            final_answer = input(
                'Are you sure you want to cancel your booking(Y/N) : ')


def cancel_slot(service):
    """This function cancels the whole slot if no one has booked them"""
    page_token = None
    all_events = []
    event_id_andstatus = []
    min_range = datetime.now().replace(
        hour=0, minute=0, second=1)
    max_range = min_range.replace(hour=23, minute=59, second=59) + timedelta(6)
    min_range = min_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    max_range = max_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")

    events = service.events().list(calendarId=CLINIC_CALENDAR_ID,
                                   pageToken=page_token,timeMin=min_range ,timeMax=max_range).execute()
    user_details = service.events().list(
        calendarId='primary', pageToken=page_token, ).execute()
    events_2 = events
    if len(events['items']) == 0:
        print(colored("Sorry there are no slots available to delete", "red"))
        return
    else:
        display_table_header()
        all_events = sorted_information_cancel_slot(all_events, events)
        display_table_and_information_no_return(all_events)

    temp_list = []
    booked_events_counter = 0
    event_number = get_number(len(all_events))
    choosen_event = all_events[event_number]
    for count in range(len(choosen_event['event id'])):
        for one_event in events_2['items']:
            if choosen_event['event id'][count] == one_event['id']:
                temp_list.append(one_event['id'])
                if len(one_event['attendees']) == 2:
                    booked_events_counter += 1

    if booked_events_counter > 0:
        return print(colored("Sorry you can't delete your slot beacuse one of them is booked", "red"))
    else:
        for event_to_delete in range(len(temp_list)):
            event_Id = temp_list[event_to_delete]
            service.events().delete(calendarId=CLINIC_CALENDAR_ID,
                                    eventId=event_Id).execute()
        return print('You have succefully deleted your slots from the calendar')


def main():
    """
    Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def view_calendar():
    """
    The view_calendar() function displays two calendars
    \t1 -> Student Calendar - Displays the students personal calendar events.
    \t1 -> Clinic Calendar -  Displays the code clinics calendar events.
    """
    # download_event(service)
    service = main()
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # now = datetime.datetime.now()
    datetime_max_date = parser.parse(now)
    max_date = str(datetime_max_date + timedelta(days=7))
    max_date = parser.parse(max_date)
    max_date = max_date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    calendars = ['primary',
                 CLINIC_CALENDAR_ID]
    # i = 0
    for i in calendars:

        if i == CLINIC_CALENDAR_ID:
            print(colored("\nClinic Calendar", attrs=['bold', 'underline']))

        else:
            print(colored("\nStudent Calendar", attrs=['bold', 'underline']))

        events_result = service.events().list(calendarId=i, timeMin=now, timeMax=max_date,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        data = []

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            start_unsplit = start.split("T")
            end_unsplit = end.split("T")
            start_date = start_unsplit[0]
            end_date = end_unsplit[0]

            start_time = start.split("T")[1]
            end_time = end.split("T")[1]

            if 'summary' in event:
                data.append([colored(start_date, 'cyan'), colored(start_time.split('+')[0], 'cyan'),
                             colored(end_time.split(
                                 '+')[0], 'cyan'), colored(event['summary'], 'cyan'),
                             colored(event['id'], 'cyan'), colored(event['status'], 'green')])

        print(tabulate(data, headers=[colored("Date", 'white', attrs=['bold']),
                                      colored("Start Time", 'white',
                                              attrs=['bold']),
                                      colored("End Time", 'white',
                                              attrs=['bold']),
                                      colored("Summary", 'white',
                                              attrs=['bold']),
                                      colored("ID", 'white', attrs=['bold']),
                                      colored("Status", 'white', attrs=['bold'])], tablefmt="grid"))


# althotse


# rellis


if __name__ == "__main__":

    service = get_calendar_service()
    download_event(service)

    my_parser = argparse.ArgumentParser(prog="code clinic", description="These are the code clinic commands that can be used in various situations:", usage='%(prog)s <command>', formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
            Working with the calendar
            
                    view_calendar               - display your calendar events and code clinic events
                    view_slot                   - view all available slots
                    book_slot                   - book a slot for help
                    volunteer_slot              - create a slot to volunteer                                                        
                    cancel_booking              - cancel you booking 
                    cancel_volunteer_slot       - remove yourself as a volunteer
                    help                        - list valid command
         '''), add_help=False)

    if len(sys.argv) == 1:
        print("\n")
        my_parser.print_help()
        print("\n\n")
        # view_available_slots()
    elif len(sys.argv) == 2 and sys.argv[1] == 'view_calendar':
        view_calendar()
        # display_calendar(USER_EVENTS, 'MY CALENDAR', 15)
        # display_calendar(CLINIC_EVENTS, 'CLINIC CALENDAR', 15)
    elif len(sys.argv) == 2 and sys.argv[1] == 'volunteer_slot':
        volunteer_slot(service)
        download_event(service)
    elif len(sys.argv) == 2 and sys.argv[1] == 'book_slot':
        book_slot(service)
        download_event(service)
    elif len(sys.argv) == 2 and sys.argv[1] == 'view_slot':
        print(view_available_slots(), '\n')
    elif len(sys.argv) == 2 and sys.argv[1] == 'cancel_volunteer_slot':
        cancel_slot(service)
        download_event(service)
    elif len(sys.argv) == 2 and sys.argv[1] == 'cancel_booking':
        booking_cancalation(service)
        download_event(service)
    elif len(sys.argv) == 2 and sys.argv[1] == 'help':
        print("\n")
        my_parser.print_help()
        print("\n\n")
    else:
        print("\n")
        my_parser.print_help()
        print("\n\n")
