import sys
import requests  # https://docs.python-requests.org/en/master/
import datetime
from pprint import pprint


class OneDayWeather:
    def __init__(self):
        self.rain = 0
        self.snow = 0

    def output_message(self):  # this method returns message
        if self.rain == 1 and self.snow == 1:
            return "It will rain and snow."
        if self.rain == 1 and self.snow == 0:
            return "It will rain."
        if self.rain == 0 and self.snow == 1:
            return "It will snow."
        else:
            return "It will be clear."


class WeatherForecast:
    def __init__(self, api_key, url, town, days):  # is api key necessary here?
        self.key = sys.argv[1]
        self.url = url
        self.town = town
        self.forecast_length = days
        self.date = self.set_date()
        self.forecast_dict = {}  # dictionary: key - date, value - object OneDayWeather
        self.current_weather = OneDayWeather()
        self.counter = 0

    def set_date(self):
        # if sys.argv[2] == None
        if len(sys.argv) < 3:
            # print(f'set date: {datetime.datetime.today().date() + datetime.timedelta(days=1)}')
            return datetime.datetime.today().date() + datetime.timedelta(days=1)
        # print(f'set date 2: {datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()}')
        return datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

    def check_date(self):  # true if correct date
        difference = self.date - datetime.datetime.today().date()
        # print(f'check date: difference {difference.days}')
        return difference.days <= 10 and difference.days >= 0

    def read_forecast_from_file(self):  # reads from file and adds result to dictionary
        with open("forecast.txt", "r") as file:
            for line in file.readlines():
                current_line = line.split(',')
                current_date = datetime.datetime.strptime(current_line[0], "%Y-%m-%d").date()
                self.forecast_dict[current_date] = OneDayWeather()
                self.forecast_dict[current_date].rain = int(current_line[1])
                self.forecast_dict[current_date].snow = int(current_line[2].split("\n")[0])
            # print(f'read from file: current line {current_line}')

    def get_data(self):
        request_params = {'key': self.key, 'q': self.town, 'days': self.forecast_length, 'dt': self.date}
        response = requests.get(self.url, params=request_params)
        self.current_weather.rain = response.json()['forecast']['forecastday'][0]['day']['daily_will_it_rain']
        self.current_weather.snow = response.json()['forecast']['forecastday'][0]['day']['daily_will_it_snow']
        print(f'get data: current rain {self.current_weather.rain}')
        # pprint(response.json())
        # obsługa błędu!!! zawsze jak działam z API to muszę to obsłużyć,
        # bo to jest korzystanie z zewnętrznej usługi i nie mam wpływu na to, czy ktoś tego nie zmieni
        # sprawdzić, czy struktura się zgadza, poszczególne klucze istnieją itp
        # .get() - pierwszy parametr - to klucz, a drugi parametr - wartość jeśli klucza nie ma
        # przechwycić wyjątek i dodać do loga (tabela w bazie danych log z treścią błędu)
        # albo plik z błędami związanymi z API

    def write_to_file(self, weather):
        with open("forecast.txt", "a") as file:
            file.write(f'{self.date},{weather.rain},{weather.snow}\n')

    def get_forecast_for_date(self):
        self.read_forecast_from_file()
        # print(f'get forecast for date 0: dict {self.forecast_dict}, and current date: {self.date}')
        if self.date in self.forecast_dict.keys():  # if date is already in file, take it
            # print(f'get forecast for date 1: read from dict {self.forecast_dict[self.date].rain}')
            self.current_weather.rain = self.forecast_dict[self.date].rain
            self.current_weather.snow = self.forecast_dict[self.date].snow

        else:
            # print(f'get forecast for date 2: get from API {self.current_weather.rain}')
            self.get_data()  # if not, get data from API
            self.write_to_file(self.current_weather)  # and add recent forecast to file
        return self.current_weather.output_message()

    def __getitem__(self, date):  # answer for given date
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        return self.get_forecast_for_date()

    def items(self):  # returns tuple generator
        for date, weather in self.forecast_dict.items():
            yield date, weather.output_message()

    def __iter__(self):  # iterator returning all dates with known forecast
        return self

    def __next__(self):
        self.counter += 1
        list_of_keys = list(self.forecast_dict.keys())
        if self.counter > len(list_of_keys):
            raise StopIteration
        return list_of_keys[self.counter - 1]


# -------------------------------------------------------------------------------------------------------------
my_weather_forecast = WeatherForecast(sys.argv[1], "http://api.weatherapi.com/v1/forecast.json", "Warsaw", 10)

if not my_weather_forecast.check_date():
    print("I don't know.")
else:
    print(my_weather_forecast.get_forecast_for_date())

# -------------------------------------------------------------------------------------------------------------
print("Magical methods, iterators:")
print("getitem:")
print(my_weather_forecast["2021-07-07"])

print("items:")
for date, forecast in my_weather_forecast.items():  # we iterate over tuple generator
    print (date, forecast)

print("iterator:")
for date in my_weather_forecast:
    print(date)


