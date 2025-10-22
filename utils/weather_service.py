import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")  # now you can use this
print("API Key loaded:", api_key) 
 
class WeatherService:
    def __init__(self):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_current_weather(self, city: str, country: str = "IN"):
        try:
            url = f"{self.base_url}/weather"
            params = {"q": f"{city},{country}", "appid": self.api_key, "units": "metric"}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                d = r.json()
                return {
                    "success": True,
                    "city": d.get("name", city),
                    "temperature": round(d["main"]["temp"], 1),
                    "feels_like": round(d["main"]["feels_like"], 1),
                    "humidity": d["main"]["humidity"],
                    "pressure": d["main"]["pressure"],
                    "description": d["weather"][0]["description"],
                    "icon": d["weather"][0]["icon"],
                    "wind_speed": d["wind"]["speed"],
                    "rainfall": d.get("rain", {}).get("1h", 0),
                    "timestamp": datetime.now().isoformat(),
                }
            return {"success": False, "error": "City not found or API error"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_forecast_by_city(self, city: str, country: str = "IN", days: int = 5):
        """
        Forecast in 3h steps via /forecast, summarized to daily with agri hints.
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {"q": f"{city},{country}", "appid": self.api_key, "units": "metric", "cnt": days * 8}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                return {"success": False, "error": "City not found or API error"}

            data = r.json()
            raw = data.get("list", [])
            daily = {}
            for slot in raw:
                date_key = slot["dt_txt"].split(" ")[0]
                rec = daily.setdefault(
                    date_key,
                    {"temps": [], "humidities": [], "rains": [], "wind": [], "descriptions": []},
                )
                rec["temps"].append(slot["main"]["temp"])
                rec["humidities"].append(slot["main"]["humidity"])
                rec["rains"].append(slot.get("rain", {}).get("3h", 0) or 0)
                rec["wind"].append(slot["wind"]["speed"])
                rec["descriptions"].append(slot["weather"][0]["description"])

            forecasts = []
            for day, rec in list(daily.items())[:days]:
                temp_avg = round(sum(rec["temps"]) / len(rec["temps"]), 1)
                humidity = int(sum(rec["humidities"]) / len(rec["humidities"]))
                rainfall = round(sum(rec["rains"]), 1)
                desc = max(set(rec["descriptions"]), key=rec["descriptions"].count)
                wind = round(sum(rec["wind"]) / len(rec["wind"]), 1)
                f = {
                    "date": day,
                    "temp_avg": temp_avg,
                    "humidity": humidity,
                    "rainfall": rainfall,
                    "description": desc,
                    "wind_speed": wind,
                }
                f["farming_conditions"] = self._agri_conditions(f)
                forecasts.append(f)

            return {"success": True, "city": data["city"]["name"], "forecasts": forecasts, "summary": self._weekly_summary(forecasts)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _agri_conditions(self, f):
        cond = []
        if f["temp_avg"] < 10:
            cond.append("Too cold for most crops")
        elif f["temp_avg"] > 35:
            cond.append("High temperature - ensure irrigation")
        else:
            cond.append("Favorable temperature")
        if f["rainfall"] > 50:
            cond.append("Heavy rainfall - postpone spraying")
        elif f["rainfall"] > 10:
            cond.append("Moderate rainfall - good for crops")
        elif f["rainfall"] == 0:
            cond.append("No rainfall - irrigation needed")
        if f["humidity"] > 80:
            cond.append("High humidity - watch for fungal disease")
        if f["wind_speed"] > 15:
            cond.append("Strong winds - secure structures")
        return cond

    def _weekly_summary(self, forecasts):
        if not forecasts:
            return {"total_rainfall": 0, "avg_temperature": 0, "avg_humidity": 0, "recommendation": "No data"}
        total_rain = round(sum(x["rainfall"] for x in forecasts), 1)
        avg_temp = round(sum(x["temp_avg"] for x in forecasts) / len(forecasts), 1)
        avg_hum = round(sum(x["humidity"] for x in forecasts) / len(forecasts))
        if total_rain > 100:
            rec = "Heavy rain likely. Ensure drainage; postpone fertilizer application."
        elif total_rain < 10 and avg_temp > 30:
            rec = "Hot and dry. Increase irrigation and consider mulching."
        elif avg_temp < 15:
            rec = "Cool week. Good for winter crops."
        elif avg_hum > 75 and avg_temp > 25:
            rec = "Humid and warm. Monitor for fungal diseases."
        else:
            rec = "Favorable week for most activities."
        return {"total_rainfall": total_rain, "avg_temperature": avg_temp, "avg_humidity": avg_hum, "recommendation": rec}

if __name__ == "__main__":
    ws = WeatherService()  # Create an instance of the class
    print(ws.get_current_weather("Delhi"))  # Call the method through the instance

