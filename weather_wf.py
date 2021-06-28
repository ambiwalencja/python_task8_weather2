import sys
import requests  # https://docs.python-requests.org/en/master/
import datetime

# 57836734f5964a9a970213219211406


class FileMixin:  # pomocnicze klasy się tak nazywają - z dopiskiem "mixin"
    def read_from_file(self):
        with open("forecast.txt", "r") as file:
            for line in file.readlines():
                date_in_line = datetime.datetime.strptime(line.split(",")[0], "%Y-%m-%d").date()
                if date_in_line == self.date:
                    self.rain = int(line.split(",")[1])
                    self.snow = int(line.split(",")[2].split("\n")[0])
                    return True
            return False

    def write_to_file(self):
        with open("forecast.txt", "a") as file:
            file.write(f'{self.date},{self.rain},{self.snow}\n')


class Weather(FileMixin):  # klasa Weather dziedziczy po FileMixin? czy odwrotnie?
    def __init__(self, url, town, days):
        self.url = url
        self.town = town
        self.date = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
        self.forecast_length = days
        self.rain = 0
        self.snow = 0

    def check_date(self):
        difference = self.date - datetime.datetime.today().date()
        if difference.days > 10:
            return False
        if difference.days < 0:
            return False
        return True

    def get_data(self):
        api_key = sys.argv[1]
        request_params = {'key': api_key, 'q': self.town, 'days': self.forecast_length, 'dt': self.date}
        response = requests.get(self.url, params=request_params)
        self.rain = response.json()['forecast']['forecastday'][0]['day']['daily_will_it_rain']
        self.snow = response.json()['forecast']['forecastday'][0]['day']['daily_will_it_snow']
        self.write_to_file()
        return True


class WeatherForecast:
    def __init__(self, api_key):
        self.key = api_key
        self.forecast_dict = {}  # dictionary: key - date, value - forecast
        self.read_forecast_from_file()
        self.weather = Weather("http://api.weatherapi.com/v1/forecast.json", "Warsaw", 10)
        self.counter = 0

    def read_forecast_from_file(self):
        with open("forecast.txt", "r") as file:
            for line in file.readlines():
                current_line = line.split(',')
                rain = int(current_line[1])
                snow = int(current_line[2].split("\n")[0])
                if rain == 1 and snow == 1:
                    self.forecast_dict[current_line[0]] = "It will rain and snow."
                elif rain == 1 and snow == 0:
                    self.forecast_dict[current_line[0]] = "It will rain."
                elif rain == 0 and snow == 1:
                    self.forecast_dict[current_line[0]] = "It will snow."
                else:
                    self.forecast_dict[current_line[0]] = "It will be clear."

    def __getitem__(self, date):  # wf[date] => odpowiedź dla podanej daty (getitem)
        if date in self.forecast_dict.keys():  # jeśli jest w słowniku, to bierzemy pogodę stamtąd
            return self.forecast_dict[date]
        else:  # inaczej pobierz dane z API
            self.weather.get_data()
            if self.weather.rain == 1 and self.weather.snow == 1:
                return "It will rain and snow."
            elif self.weather.rain == 1 and self.weather.snow == 0:
                return "It will rain."
            elif self.weather.rain == 0 and self.weather.snow == 1:
                return "It will snow."
            else:
                return "It will be clear."

    def items(self):  # returns tuple generator
        for date, weather in self.forecast_dict.items():
            yield date, weather

    def __iter__(self):  # iterator zwracający wszystkie daty, dla których znana jest pogoda.
        return self

    def __next__(self):
        self.counter += 1
        list_of_keys = list(self.forecast_dict.keys())
        if self.counter > len(list_of_keys):
            raise StopIteration
        return list_of_keys[self.counter - 1]


print("Magical methods, iterators:")
my_weather_forecast = WeatherForecast(sys.argv[1])

print("getitem:")
print(my_weather_forecast[sys.argv[2]])

print("items:")
for date, forecast in my_weather_forecast.items():  # we iterate in
    print (date, forecast)

print("iterator:")
for date in my_weather_forecast:
    print(date)


