def booking_cancalation(service):
    page_token = None
    all_events = []
    event_id_andstatus = []
    events = service.events().list(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com',
                                   pageToken=page_token, ).execute()
    user_details = service.events().list(calendarId='primary', pageToken=page_token, ).execute()
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
            event_temp = {'topic': evnt_topic, 'Clinician name': clin_name, 'event id': [], 'Status': [],
                          'Date and time': [], 'Time': []}
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
                display_rows_and_col(events_list['topic'], events_list['Clinician name'], events_list['Status'][0],
                                     events_list['event id'][0], events_list['Date and time'][0],
                                     events_list['Time'][0], count)
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
    final_answer = input('Are you sure you want to cancel your booking(Y/N) : ')
    while True:
        if final_answer.isalpha() == True:
            final_answer = final_answer.lower()
            if final_answer in yes:
                service.events().patch(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com',
                                       eventId=event_ID, body=event, sendUpdates='all').execute()
                return print('booking canceled')
            if final_answer in no:
                return print('almost canceled your booking')
        else:
            print('Please type the correct answer')
            final_answer = input('Are you sure you want to cancel your booking(Y/N) : ')

