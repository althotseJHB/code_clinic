def book_slot(service, event_id):
    """Add an atendee to an event
    :param service: calendar api service
    :param event_id: id to the event to add the attendee
    :param email_address: email of the attendee
    """

    # Get email of the patient
    # patient_email = service.calendarList().get(
    #     calendarId='primary').execute()['id']
    if len(service.events().get(calendarId=CLINIC_CALENDAR_ID, eventId=event_id).execute()['attendees']) == 2:
        print("Sorry the event is fully booked")

    elif check_calendar_conflict(event_id):
        print("You already have an event at this time slot. Please choose another slot!")
    else:
        event = service.events().get(calendarId=CLINIC_CALENDAR_ID,
                                     eventId=event_id).execute()
        # print(event)
        event['attendees'].append(
            {'email': 'joeslovo@gmail.com', 'responseStatus': 'accepted'})
        #
        try:
            service.events().patch(calendarId=CLINIC_CALENDAR_ID, eventId=event_id,
                                   body=event, sendUpdates='all').execute()
            print(f"Slot {event_id} successfully booked")
        except HttpError as e:
            print(e)
    return



def check_calendar_conflict(event_id):

    clinic_events = file_obj(CLINIC_EVENTS)
    str_time = [(event['start']['dateTime'], event['end']['dateTime'])
                for event in clinic_events if event['id'] == event_id]
    start_time = datetime.strptime(str_time[0][0], "%Y-%m-%dT%H:%M:%S+02:00")
    end_time = datetime.strptime(str_time[0][1], "%Y-%m-%dT%H:%M:%S+02:00")
    user_events = file_obj(USER_EVENTS)
    for event in user_events:
        if start_time < datetime.strptime(event['start']['dateTime'], "%Y-%m-%dT%H:%M:%S+02:00") < end_time:
            print(event['id'])
            return True
        elif start_time < datetime.strptime(event['end']['dateTime'], "%Y-%m-%dT%H:%M:%S+02:00") < end_time:
            return True

    return False
    # return True if get_events(start_time, end_time, event_id) else False
