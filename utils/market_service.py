import random
from datetime import datetime, timedelta

class MarketService:
    def __init__(self):
        self.base_prices = {
            "Rice": 2500, "Wheat": 2200, "Cotton": 6500, "Sugarcane": 350,
            "Maize": 1900, "Pulses": 5500, "Groundnut": 5800, "Soybean": 4200,
            "Jowar": 3200, "Bajra": 2100, "Ragi": 3500, "Barley": 1800,
            "Gram": 5000, "Tur": 6500, "Moong": 7500, "Urad": 6800,
            "Masoor": 5200, "Sunflower": 6200, "Safflower": 5500, "Nigerseed": 6800
        }

    # Live-style simulated prices
    def get_current_prices(self):
        prices = {}
        for crop, base in self.base_prices.items():
            var = random.uniform(-0.05, 0.05)
            now_price = int(base * (1 + var))
            trend = "rising" if var > 0.01 else ("falling" if var < -0.01 else "stable")
            prices[crop] = {
                "price": now_price,
                "unit": "per quintal",
                "trend": trend,
                "change_percent": round(var * 100, 2),
                "last_updated": datetime.now().isoformat(),
            }
        return prices

    def get_crop_price(self, crop_name: str):
        allp = self.get_current_prices()
        return allp.get(crop_name, {
            "price": 0, "unit": "per quintal", "trend": "unknown",
            "change_percent": 0, "last_updated": datetime.now().isoformat()
        })

    def get_price_history(self, crop_name: str, days: int = 30):
        base = self.base_prices.get(crop_name)
        if base is None:
            return []
        hist = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")
            var = random.uniform(-0.1, 0.1)
            hist.append({"date": date, "price": int(base * (1 + var))})
        return hist

    # Agmarknet-like helpers (mocked)
    def get_commodity_prices(self, commodity: str, state: str | None = None):
        mock = {
            "Rice": {"min_price": 2200, "max_price": 2800, "modal_price": 2500, "markets": ["Delhi", "Mumbai", "Bangalore"]},
            "Wheat": {"min_price": 1900, "max_price": 2500, "modal_price": 2200, "markets": ["Punjab", "Haryana", "UP"]},
            "Cotton": {"min_price": 6000, "max_price": 7000, "modal_price": 6500, "markets": ["Gujarat", "Maharashtra", "Telangana"]},
        }
        if commodity in mock:
            return {"success": True, "commodity": commodity, "data": mock[commodity], "timestamp": datetime.now().isoformat()}
        return {"success": False, "error": "Commodity not found"}

    def get_market_arrivals(self, commodity: str, days: int = 7):
        arr = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")
            arr.append({"date": date, "quantity": 1000 + i * 100, "unit": "quintals"})
        return {"success": True, "commodity": commodity, "arrivals": arr}

if __name__ == "__main__":
    ms = MarketService()
    print(ms.get_current_prices())
    print(ms.get_crop_price("Rice"))
