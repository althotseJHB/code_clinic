import json
import argparse
import textwrap
from typing import Any
import datefinder
import pickle  # API
import os.path  # API
import sys
from uuid import uuid4
from apiclient.discovery import build  # API
from google_auth_oauthlib.flow import InstalledAppFlow  # API
from google.auth.transport.requests import Request  # API
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date  # API
from datetimerange import DateTimeRange
from termcolor import colored
from tabulate import tabulate
from tqdm import tqdm
import pprint




def check_volunteer_slot_conflict(data_file, start_date_time):
    """
    #Shad
    The check_volunteer_slot_conflict() function checks if the entered volunteer
    slot time is available.\n
    returns a List value.
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
    #Shad
    The volunteer_slot() function creates the 90-min slot by creating three
    consecutive events in the Volunteer and the Code Clinic google calendars.\n
    First it checks if there's any conflicts regarding the volunteers entered time.
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
