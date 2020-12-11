def cancel_slot(service):
    page_token = None
    all_events = []
    event_id_andstatus = []
    events = service.events().list(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com',
                                   pageToken=page_token, ).execute()
    user_details = service.events().list(calendarId='primary', pageToken=page_token, ).execute()
    events_2 = events
    if len(events['items']) == 0:
        print(colored("Sorry there are no slots available to delete", "red"))
        return
    else:
        display_table_header()
        count = 0
        event_count = 0
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
        # event_ID = result
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

    booked_events_counter = 0
    event_number = get_number(len(all_events))
    choosen_event = all_events[event_number]
    for count in range(len(choosen_event['event id'])):
        for one_event in events_2['items']:
            if choosen_event['event id'][count] == one_event['id']:
                if len(one_event['attendees']) == 1:
                    eventid = one_event['id']
                    service.events().delete(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com',
                                            eventId=eventid).execute()
                elif len(one_event['attendees']) > 1:
                    booked_events_counter += 1
    if booked_events_counter > 0:
        print(f'NOTE:{booked_events_counter} of your slot were booked and you have to attend them')
    else:
        print('You have succefully deleted your slots from the calendar')
