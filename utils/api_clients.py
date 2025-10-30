import requests
from datetime import datetime
from config.settings import (
    OPENWEATHER_API_KEY,
    AVIATIONSTACK_API_KEY,
    CURRENCYAPI_KEY
)

class WeatherAPI:
    """OpenWeatherMap API client"""
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    @staticmethod
    def get_weather(city_name: str) -> dict:
        """Hava durumu bilgisi al"""
        try:
            params = {
                "q": city_name,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "en"
            }
            response = requests.get(WeatherAPI.BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "city": city_name.title(),
                    "temp": data["main"]["temp"],
                    "description": data["weather"][0]["description"].capitalize(),
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "formatted": (
                        f"The current weather in {city_name.title()} is "
                        f"{data['weather'][0]['description'].capitalize()}, "
                        f"{data['main']['temp']}°C, humidity {data['main']['humidity']}% "
                        f"and wind speed {data['wind']['speed']} m/s."
                    )
                }
            else:
                return {
                    "success": False,
                    "error": f"Could not find weather for {city_name}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}


class AviationAPI:
    """Aviationstack API client for flight data"""
    BASE_URL = "http://api.aviationstack.com/v1/flights"
    
    @staticmethod
    def get_flights(dep_iata: str, arr_iata: str, date: str = None) -> dict:
        """
        Uçuş bilgisi al
        dep_iata: Kalkış havalimanı kodu (örn: 'IST')
        arr_iata: Varış havalimanı kodu (örn: 'FCO')
        date: YYYY-MM-DD formatında tarih (opsiyonel)
        """
        try:
            params = {
                "access_key": AVIATIONSTACK_API_KEY,
                "dep_iata": dep_iata,
                "arr_iata": arr_iata,
            }
            
            if date:
                params["flight_date"] = date
            
            response = requests.get(AviationAPI.BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("data"):
                    return {
                        "success": False,
                        "error": "No flights found"
                    }
                
                flights = []
                for flight in data["data"][:5]:  # İlk 5 uçuş
                    flights.append({
                        "airline": flight["airline"]["name"],
                        "flight_number": flight["flight"]["iata"],
                        "departure": flight["departure"]["airport"],
                        "arrival": flight["arrival"]["airport"],
                        "dep_time": flight["departure"]["scheduled"],
                        "arr_time": flight["arrival"]["scheduled"],
                        "status": flight["flight_status"]
                    })
                
                return {
                    "success": True,
                    "flights": flights,
                    "count": len(flights)
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def format_flights(flights_data: dict) -> str:
        """Uçuş bilgilerini okunabilir formata çevir"""
        if not flights_data.get("success"):
            return flights_data.get("error", "Could not fetch flight data")
        
        result = f"✈️ Found {flights_data['count']} flights:\n\n"
        
        for i, flight in enumerate(flights_data["flights"], 1):
            result += (
                f"{i}. {flight['airline']} ({flight['flight_number']})\n"
                f"   {flight['departure']} → {flight['arrival']}\n"
                f"   Departure: {flight['dep_time']}\n"
                f"   Arrival: {flight['arr_time']}\n"
                f"   Status: {flight['status']}\n\n"
            )
        
        return result


class CurrencyAPI:
    """CurrencyAPI.com client"""
    BASE_URL = "https://api.currencyapi.com/v3/latest"
    
    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str) -> dict:
        """
        Döviz dönüşümü yap
        amount: Miktar
        from_currency: Kaynak para birimi (örn: 'USD')
        to_currency: Hedef para birimi (örn: 'EUR')
        """
        try:
            params = {
                "apikey": CURRENCYAPI_KEY,
                "base_currency": from_currency.upper(),
                "currencies": to_currency.upper()
            }
            
            response = requests.get(CurrencyAPI.BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" not in data:
                    return {
                        "success": False,
                        "error": "Invalid currency code"
                    }
                
                rate = data["data"][to_currency.upper()]["value"]
                converted = amount * rate
                
                return {
                    "success": True,
                    "from_currency": from_currency.upper(),
                    "to_currency": to_currency.upper(),
                    "amount": amount,
                    "rate": rate,
                    "converted": round(converted, 2),
                    "formatted": (
                        f"{amount} {from_currency.upper()} = "
                        f"{round(converted, 2)} {to_currency.upper()} "
                        f"(Rate: {round(rate, 4)})"
                    )
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_rates(base_currency: str = "USD") -> dict:
        """Tüm döviz kurlarını al"""
        try:
            params = {
                "apikey": CURRENCYAPI_KEY,
                "base_currency": base_currency.upper()
            }
            
            response = requests.get(CurrencyAPI.BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "base": base_currency.upper(),
                    "rates": data["data"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}