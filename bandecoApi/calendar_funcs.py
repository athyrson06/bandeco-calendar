from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import cardapio
from util import deterministic_hash

# Define the required scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]
file = open('IDs.txt', 'r')
lines = file.readlines()
IDCAL = lines[0].strip()
IDCALVEG = lines[1].strip()


class CalendarAPI:
    def __init__(self, calendar_id=IDCAL):
        self.calendar_id = calendar_id
        self.api = cardapio.CardapioAPI()

    def get_calendar_service(self):
        """
        Returns a Google Calendar service object.\n
        If the token.json file does not exist, the user is prompted to authenticate\n
        and authorize the application to access their Google Calendar.

        Returns:
            service: A Google Calendar service object.
        """

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        return build("calendar", "v3", credentials=creds)

    def create_events(self, date = None, meal = 'Almoço', veg = False, calendar_id=IDCAL, verbose = False):
        """
        Creates an event on the user's primary Google Calendar.\n
        If no date is provided, the current date is used.

        Parameters
        ----------
        date : string, optional
            string in format : 'yyyy-mm-dd', by default None
        meal : str, optional
            meal name ('Almoço' or 'Janta'), by default 'Almoço'
        veg : bool, optional
            if the meal is vegetarian, by default False
        calendar_id : str, optional
            The calendar ID to create the event on, by default IDCAL
        verbose : bool, optional
            If True, prints the event summary and date, by default False
        """
        if date == None:
            date = datetime.today().strftime('%Y-%m-%d')
        try:
            service = self.get_calendar_service()
            api = cardapio.CardapioAPI()
            try:
                meal_data = api.get_meal(date = date, meal = meal, veg = veg)
                meal_key, meal_hash = hash_meal(meal_data)
                value_str = str((meal_key, meal_hash))[1:-1].replace("'", '')
                check_backup = meal_in_backup('backup.txt', meal_key, meal_hash)

                if not check_backup:
                    append_to_file('backup.txt', value_str)
                    event = api.create_meal_event(meal_data = meal_data)
                    service.events().insert(calendarId=calendar_id, body=event).execute()
                    if verbose:
                        print(f"Event {event['summary']} created for date: {date}")
                elif check_backup == -1:
                    print(f"Meal needs to be updated.")
                else:
                    print(f"Nothing to do.")
            except LookupError:
                pass
        except HttpError as error:
            print(f"An error occurred: {error}")


    def populate_calendar(self, start_day = None, n_days=7, mode = 'after', meal = 'Almoço', veg = False, calendar_id=IDCAL, verbose = False):
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
            meal name ('Almoço' or 'Janta'), by default 'Almoço'
        veg : bool, optional
            if the meal is vegetarian, by default False
        calendar_id : str, optional
            The calendar ID to create the event on, by default IDCAL
        verbose : bool, optional
            If True, prints the event summary and date, by default False
        """
        try:
            service = get_calendar_service()
            api = cardapio.CardapioAPI()
            date = datetime.today() if start_day == None else datetime.strptime(start_day, '%Y-%m-%d')
            if mode == 'after':
                date -= timedelta(days=1)
            for _ in range(n_days):
                if mode == 'after':
                    date += timedelta(days=1)
                elif mode == 'before':
                    date -= timedelta(days=1)
                else:
                    raise ValueError("Invalid mode. Choose 'after' or 'before'.")
                try:
                    meal_data = api.get_meal(date = date, meal = meal, veg = veg)
                    event = api.create_meal_event(meal_data = meal_data)
                    service.events().insert(calendarId=calendar_id, body=event).execute()
                    if verbose:
                        print(f"Event {event['summary']} created for date: {date}")
                except LookupError:
                    pass
            
            print(f"{n_days} events created  for {meal} meals.")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def _list_events_ids(self, calendar_id=IDCAL):
        """
        Lists all event IDs on the user's primary Google Calendar.\n
        Returns a list of event IDs.

        Parameters
        ----------
        calendar_id : str, optional
            The calendar ID to list the events from, by default IDCAL
        
        Returns
        -------
        list
            A list of event IDs.
        """
        try:
            service = get_calendar_service()
            list_ids = []
            page_token = None
            while True:
                events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
                list_ids.extend(event['id'] for event in events['items'])
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
            return list_ids
        except HttpError as error:
            print(f"An error occurred: {error}")

    def _delete_events(self, list_ids, calendar_id=IDCAL, verbose = False):
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
            service = get_calendar_service()
            for event_id in list_ids:
                service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
                if verbose:
                    print(f"Event {event_id} deleted.")
        except HttpError as error:
            print(f"An error occurred: {error}")

        print("All events deleted.")


    def hash_meal(self, meal_dict):
        """
        Returns a hash of the meal dictionary.\n
        The hash is used to compare meal dictionaries.

        Parameters
        ----------
        meal_dict : dict
            A dictionary with the meal data.
        """
        backup_string = ''
        for key, value in meal_dict.items():
            backup_string += f"{value}\n"
        data_key = f'{meal_dict["Data"]}-{meal_dict["Refeição"]}'
        return data_key, deterministic_hash(backup_string)


    def append_to_file(self, file_path, data):
        """
        Appends a new line to the specified file.

        Parameters
        ----------
        file_path : str
            The file path to append the data.
        data : str
            The data to append to the file.
        """
        with open(file_path, 'a') as file:
            file.write(f"{data}\n")

    def meal_in_backup(self, file_path, data_key = None, data_hash = None):
        """
        Checks if the data is already in the backup file.

        Parameters
        ----------
        file_path : str
            The file path to check for the data.
        data : str
            The data to check in the file.
        
        Returns
        -------
        bool
            True if the data is already in the file, False otherwise.
        """
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
            code = False
            for line in lines:
                meal_key = line.split(',')[0]
                meal_hash = line.split(',')[1].strip()
                if meal_key == data_key and meal_hash == data_hash:
                    code = 1 #already in backup
                elif meal_key == data_key and meal_hash != data_hash:
                    if code != 1:
                        code = -1 #needs update
            return code

if __name__ == "__main__":
    # populate_calendar()
    create_events(meal='Almoço', veg=False, calendar_id=IDCAL, verbose=True)
    # meal_in_backup('backup.txt', '2024-08-13-Almoço', '3355d018044f409f3a5f1531eb963c6341b93f8207ba47068d0459cdf1e4e2c4')
    # populate_calendar(n_days = 15,mode = 'after', meal='Almoço', veg=False, calendar_id=IDCAL, verbose=False)
    # populate_calendar(n_days = 15,mode = 'after', meal='Jantar', veg=False, calendar_id=IDCAL, verbose=False)
    # list_of_events = list_events()
    # print(list_of_events)
    # delete_events(list_of_events)
    # list_of_events = list_events()
    # print(list_of_events)