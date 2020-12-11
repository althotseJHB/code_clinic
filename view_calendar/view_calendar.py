from __future__ import print_function
import datetime
from dateutil import parser
import pickle
import os.path
from tabulate import tabulate
import datefinder
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from termcolor import colored 


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """Shows basic usage of the Google Calendar API.
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
    service = main()
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # now = datetime.datetime.now()
    datetime_max_date = parser.parse(now)
    max_date = str(datetime_max_date + timedelta(days = 7))
    max_date = parser.parse(max_date)
    max_date = max_date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    
    calendars = ['primary','c_pivle9lhu7mn8aensev675obe0@group.calendar.google.com']
    # i = 0
    for i in calendars:
       
        if i == 'c_pivle9lhu7mn8aensev675obe0@group.calendar.google.com':
            print(colored("\nClinic Calendar", attrs=['bold', 'underline']))
            

        else:
            print(colored("\nStudent Calendar", attrs=['bold', 'underline']))

        events_result = service.events().list(calendarId= i, timeMin=now, timeMax=max_date,
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
                data.append([colored(start_date, 'cyan'), colored(start_time.split('+')[0], 'cyan'), colored(end_time.split('+')[0], 'cyan'), colored(event['summary'], 'cyan'), colored(event['id'], 'cyan'), colored(event['status'], 'green')])
                
                
        print(tabulate(data, headers= [colored("Date", 'white', attrs = ['bold']), colored("Start Time", 'white', attrs = ['bold']), colored("End Time",'white', attrs = ['bold']), colored("Summary", 'white', attrs = ['bold']), colored("ID", 'white', attrs = ['bold']), colored("Status",'white', attrs = ['bold'])], tablefmt= "grid"))

      


def add_event():

    service = main()
    summ = input("Name of the event: ")
    desc = input("What you are helping with : ")
    start_time = input("DD MMM TT(am/pm)...format : ")

    time_list = list(datefinder.find_dates(start_time))

    if len(time_list):
        start_time = time_list[0]
        end = start_time + timedelta(minutes = 90)

    event = {
    'summary': summ,
    # 'location': '800 Howard St., San Francisco, CA 94103',
    'description': desc,
    'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': 'CAT',
    },
    'end': {
        'dateTime': end.strftime("%Y-%m-%dT%H:%M:%S") ,
        'timeZone': "CAT",
    },
    'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }



    event = service.events().insert(calendarId='c_pivle9lhu7mn8aensev675obe0@group.calendar.google.com', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def delete_event():
    service = main()
    event = input("Which event do you want to delete?")
    service.events().delete(calendarId='primary', eventId=event).execute()
    print("Event deleted")


if __name__ == '__main__':

    print(colored("Welcome To Code Clinic", attrs=['bold']))
    print(colored("***********************", attrs=['bold']))
    view_calendar()