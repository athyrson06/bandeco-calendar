import requests
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from util import format_names


class CardapioAPI:
    """
    Represents the Cardapio API used to retrieve the daily menu from Unicamp's restaurants.

    This class is strongly based on the original code by Gustavo Maronato (Copyright © 2017).

    Raises
    ------
    LookupError
        If there is no menu available for the day.
    """

    BASE_URL = "https://sistemas.prefeitura.unicamp.br/apps/cardapio/index.php?d="
    MEAL_NAMES = ["Almoço", "Almoço Vegano", "Jantar", "Jantar Vegano"]

    def _get_day(self, date=None, days_delta=0, hours_delta=0):
        """Get the parsed text from the website for a specific day.

        Parameters
        ----------
        date : string, optional
            string in format : 'yyyy-mm-dd', by default None
        days_delta : int, optional
            deviation in number of days, by default 0
        hours_delta : int, optional
            deviation in number of hours, by default 0

        Returns
        -------
        BeautifulSoup text parser
            Returns the parsed text from the website.

        Raises
        ------
        LookupError
            If there is no menu available for the day.
        """
        date = date or (datetime.today() + timedelta(days=days_delta, hours=hours_delta)).strftime('%Y-%m-%d')
        response = requests.get(self.BASE_URL + date, timeout=3)
        response.raise_for_status()
        if response.text.find("Não existe cardápio") >= 0:
            raise LookupError("Não existe cardápio")

        return BeautifulSoup(response.text, 'lxml')
  
    def get_all_meals(self, date = None):
        """Get all meals from a specific day.

        Parameters
        ----------
        date : string, optional
            string in format : 'yyyy-mm-dd', by default None

        Returns
        -------
        dict
            Returns a dictionary with all meals from the day.
        """
        raw = self._get_day(date).find_all("div", {"class": "menu-section"})

        meals_dict = {}
        for idx, meal in zip(self.MEAL_NAMES, raw):
            main_course_raw = meal.find("div", {"class": "menu-item-name"})
            if main_course_raw == None:
                pass
            else:
                main_course = main_course_raw.get_text()
                description = meal.find("div", {"class": "menu-item-description"}).get_text(separator = '\n', strip=True).split("\n")
                meals_dict[idx] = {
                    "Data" : date if date != None else datetime.today(),
                    "Refeição": idx,
                    "Prato Principal": format_names(main_course),
                    "Acompanhamento" : format_names(description[1]),
                    "Salada"         : format_names(description[2]),
                    "Sobremesa"      : format_names(description[3]),
                    "Suco"           : format_names(description[4])
                }
                
        return meals_dict


    def get_meal(self, date = None, meal = 'Almoço', veg = False):
        """
        Get a specific meal from a specific day.
        
        Parameters
        ----------
        date : string, optional
            string in format : 'yyyy-mm-dd', by default None
        meal : str, optional
            meal name ('Almoço' or 'Janta'), by default 'Almoço'
        veg : bool, optional
            if the meal is vegetarian, by default False
        
        Returns
        -------
        dict
            Returns a dictionary with the specific meal from the day.
        """   
        meal = meal.capitalize()
        if veg:
            meal += f' Vegano' 
        
        return self.get_all_meals(date)[meal]

    def create_meal_event(self, meal_data = None, date = None, meal = 'Almoço', veg = False):
        """
        Create a Google Calendar event for a specific meal.\n
        If meal_data is not provided, the function will fetch the meal data from the website.
        
        Parameters
        ----------
        meal_data : dict, optional
            dictionary with the meal data\n
            It should have the following keys:\n
            'Data', 'Refeição', 'Prato Principal', 'Acompanhamento',\n
            'Salada', 'Sobremesa', 'Suco', by default None
        date : string, optional
            string in format : 'yyyy-mm-dd', by default None
        meal : str, optional
            meal name ('Almoço' or 'Janta'), by default 'Almoço'
        veg : bool, optional
            if the meal is vegetarian, by default False
        
        Returns
        -------
        dict
            Returns a dictionary with the event data as a Google Calendar event.

        """
        date = date or datetime.today().strftime('%Y-%m-%d')
        if meal_data == None:
            meal_data = self.get_meal(date, meal, veg)
        else:
            meal_data = meal_data

        if meal == 'Almoço':
            start_time = f'{date}T11:00:00-03:00'
            end_time = f'{date}T14:00:00-03:00'
        elif meal == 'Jantar':
            start_time = f'{date}T17:30:00-03:00'
            end_time = f'{date}T19:00:00-03:00'
        location = f'R. Saturnino de Brito - Cidade Universitária, Campinas - SP, 13083-889'
        
        meal_type = f'{meal_data["Refeição"]}'
        main_course = f'{meal_data["Prato Principal"]}'
        warn_time = 10

        side_dish = f'{meal_data["Acompanhamento"]}'
        salad = f'{meal_data["Salada"]}'
        dessert = f'{meal_data["Sobremesa"]}'
        juice = f'{meal_data["Suco"]}'

        event = {'summary': f'{meal_type}',
                'location': location,
                    'description': f'{main_course}\n{side_dish}\n{salad}\n{dessert}\n{juice}',  
                    'start': {'dateTime': start_time, 'timeZone': 'America/Sao_Paulo'},
                    'end': {'dateTime': end_time, 'timeZone': 'America/Sao_Paulo'},
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                        {'method': 'popup', 'minutes': warn_time},
                        ]} 


        }

        return event
    



        
