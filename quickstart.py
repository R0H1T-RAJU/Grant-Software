from __future__ import print_function
from datetime import date

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']



def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

service = build('calendar', 'v3', credentials=main())

def getEventId(name):
    id = ''
    events = service.events().list(calendarId='primary', singleEvents=True, q=name).execute()
    for event in events['items']:
        id = event['id']
    return id
    
def updateEvent(name, newDate, description):
    eventId = getEventId(name)
    event = service.events().get(calendarId='primary', eventId=eventId).execute()
    if not eventId == '' and newDate != event['start']['date']:
        event['start']['date'] = newDate 
        event['end']['date'] = newDate
        try:
            service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
            print('Updated event')
        except:
            print('Failed to update event')
    elif not newDate == event['start']['date']:
        createEvent(name, description, newDate)

def deleteEvent(name):
    try:
        service.events().delete(calendarId='primary', eventId=getEventId(name)).execute()
        print('event deleted')
    except:
        print('event does not exist')

def createEvent(name, description, date):
    try:
        event = {
            'summary': name,
            'description': description,
            'start': {
                'date': date,
                'timeZone': 'America/Chicago',
            },
            'end': {
                'date': date,
                'timeZone': 'America/Chicago',
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print('An error occurred: %s' % error)

