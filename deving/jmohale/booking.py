#!/usr/bin/env python3
import json
import argparse
import textwrap
import datefinder
import pickle
import os.path
import sys
from uuid import uuid4
from apiclient.discovery import build
from dateutil import parser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date
from termcolor import colored
from tabulate import tabulate
from tqdm import tqdm


# temporary code clinic calendar id
CLINIC_CALENDAR_ID = 'c_ckbi989o2ujtcvtummcm75qjqo@group.calendar.google.com'
# 'c_crobkpscujcp15baikn95tt110@group.calendar.google.com'

CREDENTIALS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLINIC_EVENTS = 'clinic.json'
USER_EVENTS = 'patient.json'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+02:00'


def download_event(service_event):
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

    patient_events = service_event.events().list(
        calendarId='primary', timeMin=min_range).execute().get('items', [])
    clinic_events = service_event.events().list(
        calendarId=CLINIC_CALENDAR_ID, timeMin=min_range).execute().get('items', [])

    p_obj = json.dumps(check_recurring_events(
        service_event, patient_events), indent=4)
    c_obj = json.dumps(clinic_events, indent=4)
    # save the the calendar events
    with open('patient.json', 'w') as p_data, open("clinic.json", 'w') as c_data:
        # datafile.write(f_obj)
        p_data.write(p_obj)
        c_data.write(c_obj)


def check_recurring_events(service, user_events):
    # duplicate of occurrence events
    add_events = user_events

    for event in user_events:
        if 'recurrence' in event:
            new_events = service.events().instances(
                calendarId='primary', eventId=event['id']).execute().get('items', [])
            for item in new_events:
                add_events.append(item)

    return add_events
    # for i in add_events:
    #     for eve in i:
    #         print(eve['start'])
    # print(add_events)


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
            creds = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def volunteer_slot(service):
    clinician_email = service.calendarList().get(
        calendarId='primary').execute()['id']
    print("Please enter your volunteer slots Date and Start-Time.")
    input_time = input(
        colored("Day Month Time - e.g: 14 Dec 14:30]: ", 'yellow'))
    summary = input("Please enter the slot summary: ")
    description = input("Please enter the slot description: ")

    increment_time = 30

    start_date_time = list(datefinder.find_dates(input_time))[0]
    start_date_time_str = start_date_time.strftime(
        "%Y-%m-%dT%H:%M:%S+02:00")

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
        event = service.events().insert(calendarId=CLINIC_CALENDAR_ID,
                                        body=event, conferenceDataVersion=1).execute()
        # print('Event created: {0}'.format(event.get('htmlLink')))
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(event)
        start_date_time = start_date_time + timedelta(minutes=increment_time)
        start_date_time_str = start_date_time.strftime(
            "%Y-%m-%dT%H:%M:%S+02:00")
        end_date_time = end_date_time + timedelta(minutes=increment_time)
        end_date_time_str = end_date_time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    print(colored('Your volunteer slot for ', 'green') +
          colored(summary, 'yellow') + colored(' was successfully created.', 'green'))


def book_slot(service):
    """
    books a slot by adding an attendeet to the event slot
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
            print("You already have an event at this time slot. Please choose another slot!")
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
                return print("An error occured while trying book the event.Please try again!")
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
    
    rows.append(colored(start+'-'+end, 'cyan'))
    rows.append(colored(event['id'], 'cyan'))

    rows.append(colored('YES', 'green') if 'attendees' in event.keys() and len(
        event['attendees']) < 2 else colored("NO", 'red'))
    return rows





def display_calendar(file, user, time_frame):
    # change the
    with open(file) as f:
        data = json.load(f)
    min_range = datetime.now().replace(
        hour=0, minute=0, second=1)
    max_range = min_range.replace(
        hour=23, minute=59, second=59) + timedelta(time_frame)

    cal_header = ['DATE', 'SUMMARY', 'START-TIME', 'END-TIME', 'STATUS']
    time_data = {event['start']["dateTime"].split('T')[0] for event in data if min_range <= datetime.strptime(
        event['start']["dateTime"], "%Y-%m-%dT%H:%M:%S+02:00") <= max_range}
    time_data = list(time_data)
    time_data.sort()
    table_print = []
    for day in time_data:
        for event in data:
            if event['start']["dateTime"].split('T')[0] == day:
                row_data = []
                row_data.append(day)
                row_data.append(event['summary'])
                row_data.append(event['start']["dateTime"].split('T')[
                                1].split('+')[0])
                row_data.append(event['end']["dateTime"].split('T')[
                                1].split('+')[0])
                table_print.append(row_data)

    print(colored(user, 'magenta'))
    print(tabulate(table_print, headers=cal_header, tablefmt='grid'))
    print('\n')


def valid_book_commands(args):
    # unfinished
    clinic_event_ids = [event['id'] for event in file_obj(CLINIC_EVENTS)]
    command, option = args
    if command == 'book_slot' and option in clinic_event_ids:
        return True
    else:
        return False


def booking_cancalation(service):
    page_token = None
    all_events = []
    event_id_andstatus = []
    min_range = datetime.now().replace(
        hour=0, minute=0, second=1)
    max_range = min_range.replace(hour=23, minute=59, second=59) + timedelta(6)
    min_range = min_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    max_range = max_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")

    events = service.events().list(calendarId=CLINIC_CALENDAR_ID,
                                   pageToken=page_token, timeMin=min_range).execute()
    user_details = service.events().list(
        calendarId='primary', pageToken=page_token, timeMin=min_range).execute()
    events_2 = events
    if len(events['items']) == 0:
        print(colored("Sorry there are no slot open to cancel available for now", "red"))
        return
    else:
        display_table_header()
        count = 0
        for events_available in events['items']:
            clin_name = events_available['description']
            evnt_topic = events_available['summary']
            event_temp = {'topic': evnt_topic, 'Clinician name': clin_name,
                          'event id': [], 'Status': [], 'Date and time': [], 'Time': []}
            for event_details in events['items']:
                if event_details['description'] == clin_name and event_details['summary'] == evnt_topic:
                    event_temp['event id'].append(event_details['id'])
                    if len(event_details['attendees']) == 1:
                        status = colored(max_display('slot Open'), 'green')
                    elif len(event_details['attendees']) == 2:
                        status = colored(max_display('slot Closed'), 'red')

                    event_temp['Status'].append(status)
                    extracted_date = str(event_details['start']['dateTime'])
                    end_time = str(event_details['end']['dateTime'])
                    temp_date = extracted_date[:10]
                    start_time = extracted_date[11:-9]
                    end_time = end_time[11:-9]
                    event_temp['Date and time'].append(get_date(temp_date))
                    event_temp['Time'].append(f'{start_time} to {end_time}')

            if event_temp in all_events:
                continue
            else:
                all_events.append(event_temp)
        # print

        for events_list in all_events:
            if len(events_list['event id']) == 1:
                display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status']
                                     [0], events_list['event id'][0], events_list['Date and time'][0], events_list['Time'][0], count)
                print(colored("~"*154, 'blue'))
            elif len(events_list['event id']) == 2:
                for events in range(2):
                    if events == 0:
                        display_rows_and_col_one(
                            events_list['Status'][events], events_list['event id'][events], events_list['Time'][events], 0)
                    if events == 1:
                        display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status'][events],
                                             events_list['event id'][events], events_list['Date and time'][events], events_list['Time'][events], count)
                print(colored("~"*154, 'blue'))
            else:
                for events in range(len(events_list['event id'][0])-1):
                    if events == 0 or events == 2:
                        display_rows_and_col_one(
                            events_list['Status'][events], events_list['event id'][events], events_list['Time'][events], 0)
                    elif events == 1:
                        display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status'][events],
                                             events_list['event id'][events], events_list['Date and time'][events], events_list['Time'][events], count)
                print(colored("~"*154, 'blue'))
            count += 1
    result = check_the_id(all_events)
    event_ID = result

    for v in events_2['items']:
        if event_ID == v['id'] and len(v['attendees']) == 2:
            if v['attendees'][1]['email'] == user_details['summary']:
                clinician_email = v['attendees'][0]['email']
            elif v['attendees'][1]['email'] != user_details['summary']:
                return print('Sorry your email does not match with the attendee')
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
    page_token = None
    all_events = []
    event_id_andstatus = []
    min_range = datetime.now()
    max_range = min_range.replace(hour=23, minute=59, second=59) + timedelta(6)
    min_range = min_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    max_range = max_range.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    events = service.events().list(calendarId=CLINIC_CALENDAR_ID,
                                   pageToken=page_token, timeMin=min_range).execute()
    user_details = service.events().list(
        calendarId='primary', pageToken=page_token, timeMin=min_range).execute()
    events_2 = events
    if len(events['items']) == 0:
        return print(colored("Sorry there are no slots available to delete", "red"))
    else:
        display_table_header()
        count = 0
        event_count = 0
        # print(events)
        for events_available in events['items']:
            clin_name = events_available['description']
            evnt_topic = events_available['summary']
            event_temp = {'topic': evnt_topic, 'Clinician name': clin_name,
                          'event id': [], 'Status': [], 'Date and time': [], 'Time': []}

            for event_details in events['items']:
                if event_details['description'] == clin_name and event_details['summary'] == evnt_topic:
                    event_temp['event id'].append(event_details['id'])
                    if len(event_details['attendees']) == 1:
                        status = colored(max_display('slot Open'), 'green')
                    elif len(event_details['attendees']) == 2:
                        status = colored(max_display('slot Closed'), 'red')

                    event_temp['Status'].append(status)
                    extracted_date = str(event_details['start']['dateTime'])
                    end_time = str(event_details['end']['dateTime'])
                    temp_date = extracted_date[:10]
                    start_time = extracted_date[11:-9]
                    end_time = end_time[11:-9]
                    event_temp['Date and time'].append(get_date(temp_date))
                    event_temp['Time'].append(f'{start_time} to {end_time}')
            if event_temp in all_events:
                continue
            else:
                all_events.append(event_temp)
    # event_ID = result
        for events_list in all_events:

            if len(events_list['event id']) == 1:
                display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status']
                                     [0], events_list['event id'][0], events_list['Date and time'][0], events_list['Time'][0], count)
                print(colored("~"*154, 'blue'))

            elif len(events_list['event id']) == 2:
                for events in range(2):
                    if events == 0:
                        display_rows_and_col_one(
                            events_list['Status'][events], events_list['event id'][events], events_list['Time'][events], 0)
                    if events == 1:
                        display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status'][events],
                                             events_list['event id'][events], events_list['Date and time'][events], events_list['Time'][events], count)
                print(colored("~"*154, 'blue'))
            else:
                for events in range(len(events_list['event id'][0])-1):
                    if events == 0 or events == 2:
                        display_rows_and_col_one(
                            events_list['Status'][events], events_list['event id'][events], events_list['Time'][events], 0)
                    elif events == 1:
                        display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status'][events],
                                             events_list['event id'][events], events_list['Date and time'][events], events_list['Time'][events], count)
                print(colored("~"*154, 'blue'))
            count += 1

    booked_events_counter = 0
    event_number = get_number(len(all_events))
    choosen_event = all_events[event_number]
    for count in range(len(choosen_event['event id'])):
        for one_event in events_2['items']:
            if choosen_event['event id'][count] == one_event['id']:
                if len(one_event['attendees']) == 1:
                    eventid = one_event['id']
                    service.events().delete(calendarId=CLINIC_CALENDAR_ID, eventId=eventid).execute()
                elif len(one_event['attendees']) > 1:
                    booked_events_counter += 1
    if booked_events_counter > 0:
        print(
            f'NOTE:{booked_events_counter} of your slot were booked and you have to attend them')
    else:
        print('You have succefully deleted your slots from the calendar')


def display_table_header():
    print(colored("~"*154, 'blue'))
    print(f'  {colored(max_display("Topic/specialty"),"blue")}{colored("|","blue")}{colored(max_display(" Clinician Name"),"blue")}{colored("|","blue")}{colored(max_display(" Event status"),"blue")}{colored("|","blue")}{colored(max_display(" event ID"),"blue")}{colored("|","blue")}{colored(max_display(" Date"),"blue")}{colored("|","blue")}{colored(max_display(" Time"),"blue")}')
    print(colored("~"*154, 'blue'))


def display_rows_and_col(event_topic, event_Clinician_name, event_status, event_id, event_date, event_time, count):
    print(f"{colored(count,'blue')}.{colored(max_display(event_topic))}{colored('|','blue')}{colored(max_display(event_Clinician_name))}{colored('|','blue')}{(colored(event_status))}{colored('|','blue')}{colored(max_display(event_id))}{colored('|','blue')}{colored(max_display(event_date))}{colored('|','blue')}{colored(max_display(event_time))}")


def check_the_id(events):
    event_id = input('Please copy the event id that you want to book: ')
    while True:
        for count in events:
            if event_id in count['event id']:
                return event_id
        else:
            print('Please type or copy the correct event name')
            event_id = input(
                'Please copy the event id that you want to book: ')


def get_number(events_lenght):
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


def max_display(name):
    max_char_lnght = 26
    empty_char = ' '
    lenghth_name = len(name)
    if lenghth_name > max_char_lnght:
        return name[:26]
    elif lenghth_name < max_char_lnght:
        count = max_char_lnght-lenghth_name
    else:
        return name
    for lngth in range(count):
        name = name+empty_char
    return name


def get_date(str_date):
    for g in datefinder.find_dates(str(str_date)):
        date = g
    date = f"{date.year} {date.strftime('%b')} {date.day}"
    return date



def display_rows_and_col_one(event_status, event_id, event_time, count):
    count
    print(f"{max_display(' ')}  {colored('|','blue')}{max_display(' ')}{colored('|','blue')}{colored(event_status)}{colored('|','blue')}{colored(max_display(event_id))}{colored('|','blue')}{max_display(' ')}{colored('|','blue')}{colored(max_display(event_time))}")


def view_calendar(service):
    # service = main()
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    datetime_max_date = parser.parse(now)
    max_date = str(datetime_max_date + timedelta(days=7))
    max_date = max_date.replace(" ", "T")
    max_date = max_date[:len(max_date)-6] + "Z"

    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=max_date,
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
            data.append([start_date, start_time.split(
                '+')[0], end_time.split('+')[0], event['summary'], event['id'], event['status']])
            # print(event['id'])

    # print(data)
    print(tabulate(data, headers=[
          "Date", "Start Time", "End Time", "Summary", "ID", "Status"], tablefmt="grid"))


if __name__ == "__main__":

    service = get_calendar_service()
    


    my_parser = argparse.ArgumentParser(prog="booking", description="These are the code clinic commands that can be used in various situations:", usage='%(prog)s <command> [<args]', formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
            Working with the calendar
                    book_slot             - book a slot for help 
                    view_calendar         - display your calendar events and code clinic events
                    volunteer_slot        - create a slot to volunteer
                    cancel_booking        - cancel you booking 
                    cancel_volunteer_slot - remove yourself as a volunteer
                    view_slot             - view all available slots


         '''), add_help=False)

    if len(sys.argv) == 1:
        my_parser.print_help()
        # view_available_slots()
    elif len(sys.argv) == 2 and sys.argv[1] == 'view_calendar':
        view_calendar(service)
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
    elif len(sys.argv) == 3 and valid_book_commands(sys.argv[1:]):
        book_slot(service, sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == 'cancel_volunteer_slot':
        cancel_slot(service)
        download_event(service)
    elif len(sys.argv) == 2 and sys.argv[1] == 'cancel_booking':
        booking_cancalation(service)
        download_event(service)
    else:
        print(view_available_slots(), '\n')
        my_parser.print_help()
