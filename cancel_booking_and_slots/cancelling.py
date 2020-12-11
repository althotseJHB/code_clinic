def sorted_information_cancel_slot(final_lis, events):
    """This function return a dictionary with information sorted accordingly"""
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
        if event_temp in final_lis:
            continue
        else:
            final_lis.append(event_temp)
    return final_lis


def sorted_information(final_list, cal_events):
    '''This function takes two parameters the list and the calander info and puts
        them in a dictionary in a sorted way and when done append that dictionary to
    the list and returns  that list when it is done'''
    count = 0
    for events_available in cal_events['items']:
        clin_name = events_available['description']
        evnt_topic = events_available['summary']
        event_temp = {'topic': evnt_topic, 'Clinician name': clin_name,
                      'event id': [], 'Status': [], 'Date and time': [], 'Time': []}
        for event_details in cal_events['items']:
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
    event_id = input('Please copy & paste the event id that you want to cancel: ')
    while True:
        for count in events:
            if event_id in count['event id']:
                return event_id
            else:
                print('Please type or copy the correct event name')
                event_id = input('Please copy & paste the event id that you want to cancel: ')


def display_table_and_information(list_events):
    '''This function extract the information from the calendar and display that information
    accordingly and returns the selected event ID '''
    count = 0
    for events_list in list_events:
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
    result = check_the_id(list_events)
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
    event_number = input("Please choose a number of the event that you want to remove :")
    while True:
        if event_number.isdigit() == True and 0 <= int(event_number) <= events_lenght:
            return int(event_number)
        else:
            print('Please make sure that it is a number')
            event_number = input("Please choose a number of the event that you want to remove :")


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
    all_events = []
    event_id_andstatus = []
    events = service.events().list(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com',
                                   pageToken=page_token, ).execute()
    user_details = service.events().list(calendarId='primary', pageToken=page_token, ).execute()
    events_2 = events
    if len(events['items']) == 0:
        return print(colored("Sorry there are no available slots open to cancel for now", "red"))
    else:
        display_table_header()
        count = 0
        all_events = sorted_information(all_events, events)
    event_ID = display_table_and_information(all_events)

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
            service.events().patch(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com', eventId=event_ID,
                                   body=event, sendUpdates='all').execute()
            return print('booking canceled')
        if final_answer in no:
            return print('almost canceled your booking')
        else:
            print('Please type the correct answer')
            final_answer = input('Are you sure you want to cancel your booking(Y/N) : ')


def cancel_slot(service):
    """This function cancels the whole slot if no one has booked them"""
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
            service.events().delete(calendarId='f5dk826mlubpqfmmq5fjv9kbqo@group.calendar.google.com',
                                    eventId=event_Id).execute()
        return print('You have succefully deleted your slots from the calendar')

