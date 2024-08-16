from datetime import datetime, timedelta


from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import cardapio

SERVICE_ACCOUNT_FILE = 'key.json'

# Define the required scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]
file = open('IDs.txt', 'r')
lines = file.readlines()
IDCAL = lines[0].strip()
IDCALVEG = lines[1].strip()


class CalendarAPI:
    def __init__(self, calendar_id=IDCAL, date = None, veg = False):
        self.calendar_id = calendar_id
        self.api = cardapio.CardapioAPI()
        self.veg = veg
        self.date = datetime.today() if date == None else datetime.strptime(date, '%Y-%m-%d')
        try:
            self.service = self._get_calendar_service_()
        except HttpError as error:
            print(f"An error occurred: {error}")



    def _get_calendar_service_(self):
        """
        Returns a Google Calendar service object using a service account.

        Returns:
            service: A Google Calendar service object.
        """

        # Path to your service account key file
        SERVICE_ACCOUNT_FILE = 'key.json'
        
        # Define the required scopes
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        # Authenticate using the service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Build the service using the authenticated credentials
        service = build('calendar', 'v3', credentials=credentials)
        
        return service



    def _list_events_ids_(self, start_day=None, n_days=7, mode='after'):
        """
        Lists all event IDs on the user's primary Google Calendar.
        Returns a list of event IDs.

        Parameters
        ----------
        start_date : str, optional
            The start date for listing events, in 'YYYY-MM-DD' format. Defaults to None.
        n_days : int, optional
            The number of days to list events for. Defaults to 7.
        mode : str, optional
            The mode to list events ('after' or 'before'). Defaults to 'after'.
        
        Returns
        -------
        list
            A list of event IDs.
        """
        if n_days != -1:
            n_days = n_days if mode == 'after' else -n_days
            if start_day is None:
                date = self.date
            else:
                if type(start_day) == str:
                    date = datetime.strptime(start_day, '%Y-%m-%d')
                elif type(start_day) == datetime:
                    date = start_day
                else:
                    raise ValueError("Invalid start_day type. Should be 'str' or 'datetime'.")  
            start_date = date.strftime('%Y-%m-%dT00:00:00-03:00')
            end_date = (date + timedelta(days=n_days)).strftime('%Y-%m-%dT00:00:00-03:00')
            
            if mode == 'after':
                time_min, time_max = start_date, end_date
            elif mode == 'before':
                time_min, time_max = end_date, start_date
            else:
                raise ValueError("Mode should be 'after' or 'before'")
        
        list_ids = []
        page_token = None

        try:
            while True:
                if n_days == -1:
                    events = self.service.events().list(calendarId=self.calendar_id,
                                                    pageToken=page_token).execute()
                else:
                    events = self.service.events().list(calendarId=self.calendar_id,
                                                    timeMin=time_min, timeMax=time_max,
                                                    pageToken=page_token).execute()
                list_ids.extend(event['id'] for event in events['items'])
                page_token = events.get('nextPageToken')
                if not page_token:
                    break

            return list_ids

        except Exception as e:
            print(f"An error occurred: {e}")
            return []


    def _list_events_(self, start_day=None, n_days=7, mode='after'):
        """
        Lists all events on the user's primary Google Calendar.
        Returns a list of events.

        Parameters
        ----------
        start_date : str, optional
            The start date for listing events, in 'YYYY-MM-DD' format. Defaults to None.
        n_days : int, optional
            The number of days to list events for. Defaults to 7.
        mode : str, optional
            The mode to list events ('after' or 'before'). Defaults to 'after'.
        
        Returns
        -------
        list
            A list of events.
        """
        if n_days != -1:
            n_days = n_days if mode == 'after' else -n_days
            date = self.date if start_day is None else datetime.strptime(start_date, '%Y-%m-%d')
            start_date = date.strftime('%Y-%m-%dT00:00:00-03:00')
            end_date = (date + timedelta(days=n_days)).strftime('%Y-%m-%dT00:00:00-03:00')
            
            if mode == 'after':
                time_min, time_max = start_day, end_date
            elif mode == 'before':
                time_min, time_max = end_date, start_day
            else:
                raise ValueError("Mode should be 'after' or 'before'")
        
        list_events = []
        page_token = None

        try:
            while True:
                if n_days == -1:
                    events = self.service.events().list(calendarId=self.calendar_id,
                                                    pageToken=page_token).execute()
                else:
                    events = self.service.events().list(calendarId=self.calendar_id,
                                                    timeMin=time_min, timeMax=time_max,
                                                    pageToken=page_token).execute()
                list_events.extend(event['description'] for event in events['items'])
                page_token = events.get('nextPageToken')
                if not page_token:
                    break

            return list_events

        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        
    def _delete_events_(self, list_ids, all = False, verbose = False):
        """
        Deletes events from the user's primary Google Calendar.
        
        Parameters
        ----------
        list_ids : list
            A list of event IDs to delete.
        calendar_id : str, optional
            The calendar ID to delete the events from, by default IDCAL
        verbose : bool, optional
            If True, prints the event ID being deleted, by default False
        """
        try:
            if all:
                list_ids = self._list_events_ids_(n_days=-1)
            
            for event_id in list_ids:
                self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
                if verbose:
                    print(f"Event {event_id} deleted.")
        except HttpError as error:
            print(f"An error occurred: {error}")

        print("All events deleted.")

    def create_event(self, date = None, meal = 'Almoço', verbose = False):
        """
        Creates an event on the user's primary Google Calendar.\n
        If no date is provided, the current date is used.

        Parameters
        ----------
        date : string, optional
            string in format : 'yyyy-mm-dd', by default None
        meal : str, optional
            meal name ('Almoço' or 'Jantar'), by default 'Almoço'
        calendar_id : str, optional
            The calendar ID to create the event on, by default IDCAL
        verbose : bool, optional
            If True, prints the event summary and date, by default False
        """
        if date is None:
                date = self.date
        else:
            if type(date) == str:
                date = datetime.strptime(date, '%Y-%m-%d')
            elif type(date) == datetime:
                date = date
            else:
                raise ValueError("Invalid start_day type. Should be 'str' or 'datetime'.")  
        try:
            date = date.strftime('%Y-%m-%d')
            event_data = self.api.create_meal_event(date = date, meal = meal, veg = self.veg)
            
            event = self.service.events().insert(calendarId=self.calendar_id, body=event_data).execute()
            event_id = event['id']
            if verbose:
                print(f"Event {event['summary']} created for date: {date} with ID: {event_id}")
            return event_id
        except LookupError:
            print (f"No meal data found for {date}.")
            pass

    def populate_calendar(self, start_day = None, n_days=7, mode = 'after', meal = 'Almoço', verbose = False):
        """
        Populates the user's primary Google Calendar with events\n
        for a specific meal for a number of days.

        Parameters
        ----------
        start_day : string, optional
            string in format : 'yyyy-mm-dd', by default None
        n_days : int, optional
            number of days to populate, by default 7
        mode : str, optional
            'after' or 'before', by default 'after'
        meal : str, optional
            meal name ('Almoço' or 'Jantar'), by default 'Almoço'
        verbose : bool, optional
            If True, prints the event summary and date, by default False
        """
        try:
            if start_day is None:
                date = self.date
            else:
                if type(start_day) == str:
                    date = datetime.strptime(start_day, '%Y-%m-%d')
                elif type(start_day) == datetime:
                    date = start_day
                else:
                    raise ValueError("Invalid start_day type. Should be 'str' or 'datetime'.")  

            date -= timedelta(days=1) #adjusting for the first day being included in the loop
            list_sucess = []
            for _ in range(n_days):
                if mode == 'after':
                    date += timedelta(days=1)
                elif mode == 'before':
                    date -= timedelta(days=1)

                else:
                    raise ValueError("Invalid mode. Choose 'after' or 'before'.")
                try:
                    temp_date = date.strftime('%Y-%m-%d')
                    event_id = self.create_event(date = temp_date, meal = meal, verbose = verbose)
                    list_sucess.append(event_id)
                except LookupError:
                    print (f"No meal data found for {temp_date}.")
                    pass
            
            print(f"{len(list_sucess)} events created  for {meal}.")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def update_week(self, start_day = None, n_days = 7, mode = 'after', verbose = False):
        """
        Updates the user's primary Google Calendar with the meals for a week by deleting the events and creating new ones.\n
        Can be used to update the calendar for the current week or the next week (or any number of days).

        Parameters
        ----------
        start_day : string, optional
            string in format : 'yyyy-mm-dd', by default None
        n_days : int, optional
            number of days to populate, by default 7
        mode : str, optional
            'after' or 'before', by default 'after'
        verbose : bool, optional
            If True, prints the event summary and date, by default False
        """
        if start_day == None:
            start_day = self.date
        try:
            list_ids = self._list_events_ids_(start_day=start_day, n_days=n_days, mode=mode)   
            self._delete_events_(list_ids = list_ids, verbose = verbose)
            if verbose:
                print(f"Deleted {len(list_ids)} events.")
            self.populate_calendar(start_day=start_day, n_days=n_days, mode=mode, meal='Almoço', verbose=verbose)
            self.populate_calendar(start_day=start_day, n_days=n_days, mode=mode, meal='Jantar', verbose=verbose)
            
            if verbose:
                print(f"Updated {n_days} days starting from {start_day.strftime('%d/%m of %Y')}.")
        except HttpError as error:
            print(f"An error occurred: {error}")
    

if __name__ == "__main__":

    calendar = CalendarAPI(calendar_id=IDCAL)
    calendar.update_week(n_days=10, mode='after', verbose=True)

