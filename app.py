from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from mysql.connector import Error
import os
import pickle
import numpy as np
from datetime import datetime
import pandas as pd
from utils.weather_service import WeatherService
from utils.market_service import MarketService
from utils.soil_analysis import SoilAnalyzer

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize services
weather_service = WeatherService()
market_service = MarketService()
soil_analyzer = SoilAnalyzer()

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'crop_recommendation'
}

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"[v0] Error connecting to MySQL: {e}")
        return None

# ==================== LOAD TRAINED ML MODEL ==================== #
MODEL_DIR = os.path.join(os.getcwd(), "models")
try:
    model = pickle.load(open(os.path.join(MODEL_DIR, "crop_recommendation_model.pkl"), "rb"))
    scaler = pickle.load(open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb"))
    le_crop = pickle.load(open(os.path.join(MODEL_DIR, "crop_label_encoder.pkl"), "rb"))
    label_encoders = pickle.load(open(os.path.join(MODEL_DIR, "label_encoders.pkl"), "rb"))
    feature_columns = pickle.load(open(os.path.join(MODEL_DIR, "feature_columns.pkl"), "rb"))
    print("[v0]ML model and encoders loaded successfully!")
except Exception as e:
    print(f"[v0]Failed to load ML model: {e}")
    model, scaler, le_crop, label_encoders, feature_columns = None, None, None, None, None
# ================================================================ #

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

# ================================================================= #
# 🔥 MACHINE LEARNING BASED CROP RECOMMENDATION
# ================================================================= #
@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Get crop recommendations using the trained ML model + analysis"""
    data = request.json or {}

    try:
        state = data.get('state')
        season = data.get('season')
        rainfall = float(data.get('rainfall', 1000))
        temperature = float(data.get('temperature', 25))
        fertilizer = float(data.get('fertilizer', 100000))
        pesticide = float(data.get('pesticide', 5000))
        area = float(data.get('area', 10000))

        if not model:
            return jsonify({'success': False, 'error': 'ML model not loaded. Please check /models folder.'}), 500

        # Encode categorical features safely
        state_encoded = label_encoders['State'].transform([state])[0] if state in label_encoders['State'].classes_ else 0
        season_encoded = label_encoders['Season'].transform([season])[0] if season in label_encoders['Season'].classes_ else 0

        # Derived features
        fert_per_area = fertilizer / (area + 1)
        pest_per_area = pesticide / (area + 1)

        # Prepare input for model
        row = {
            'Season_encoded': season_encoded,
            'State_encoded': state_encoded,
            'Area': area,
            'Annual_Rainfall': rainfall,
            'Fertilizer': fertilizer,
            'Pesticide': pesticide,
            'Fertilizer_per_Area': fert_per_area,
            'Pesticide_per_Area': pest_per_area
        }

        X = pd.DataFrame([[row[col] for col in feature_columns]], columns=feature_columns)
        X_scaled = scaler.transform(X)
        probs = model.predict_proba(X_scaled)[0]

        # Get top 5 predicted crops
        idxs = np.argsort(probs)[-5:][::-1]
        results = []

        for idx in idxs:
            crop = le_crop.inverse_transform([idx])[0]
            confidence = round(float(probs[idx] * 100), 2)

            # 🌧️ Fertilizer / Pesticide / Rainfall analysis
            pros, cons = [], []

            if 800 <= rainfall <= 1500:
                pros.append(f"Optimal rainfall level ({rainfall} mm)")
            elif rainfall < 800:
                cons.append(f"Low rainfall ({rainfall} mm) may require irrigation")
            else:
                cons.append(f"High rainfall ({rainfall} mm) may need drainage management")

            if 15 <= temperature <= 35:
                pros.append(f"Ideal temperature range ({temperature}°C)")
            elif temperature < 15:
                cons.append(f"Low temperature ({temperature}°C) - crop growth may slow")
            else:
                cons.append(f"High temperature ({temperature}°C) - heat stress risk")

            if 50000 <= fertilizer <= 200000:
                pros.append(f"Balanced fertilizer level ({fertilizer} kg/ha)")
            elif fertilizer < 50000:
                cons.append("Low fertilizer usage - may affect yield")
            else:
                cons.append("High fertilizer usage - risk of nutrient burn")

            if 1000 <= pesticide <= 8000:
                pros.append(f"Appropriate pesticide level ({pesticide} kg/ha)")
            elif pesticide < 1000:
                cons.append("Low pesticide - monitor for pest attacks")
            else:
                cons.append("High pesticide - consider integrated pest management")

            growth_period = get_growth_period(crop)
            tips = get_growing_tips(crop, temperature, rainfall)
            water_need = 'High' if rainfall > 1500 else 'Medium' if rainfall > 800 else 'Low'
            profitability = 'High' if confidence > 70 else 'Medium' if confidence > 50 else 'Low'

            price_data = market_service.get_crop_price(crop)
            price_str = f"₹{price_data['price']}/quintal" if isinstance(price_data, dict) and 'price' in price_data else "N/A"

            results.append({
                'crop': crop,
                'confidence': confidence,
                'growth_period': growth_period,
                'pros': pros,
                'cons': cons,
                'growing_tips': tips,
                'water_need': water_need,
                'profitability': profitability,
                'market_price': price_str
            })

        return jsonify({
            'success': True,
            'recommendations': results,
            'source': 'ml_model',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[v0] Error generating ML recommendations: {e}")
        return jsonify({'success': False, 'error': str(e), 'recommendations': []}), 500

# ================================================================= #
# 🌿 Helper Functions
# ================================================================= #
def get_growing_tips(crop, temperature, rainfall):
    tips = {
        'Wheat': [
            'Plant when soil temperature is above 4°C',
            'Ensure good drainage to avoid waterlogging',
            'Monitor for rust and mildew diseases',
            'Apply nitrogen in split doses'
        ],
        'Rice': [
            'Maintain standing water during growth',
            'Transplant seedlings at 3-4 leaf stage',
            'Monitor for blast and stem borer attacks',
            'Apply phosphorus during planting'
        ],
        'Cotton': [
            'Requires long frost-free growing season',
            'Monitor for bollworms and aphids',
            'Plant when soil temp is above 18°C',
            'Harvest when bolls open fully'
        ],
        'Maize': [
            'Plant after soil reaches 10°C',
            'Tolerates moderate drought',
            'Harvest when husks dry and brown',
            'Apply fertilizer early for better yield'
        ]
    }
    return tips.get(crop, [
        f"Plant under optimal {temperature}°C temperature",
        f"Maintain adequate rainfall around {rainfall}mm",
        "Use fertilizers based on soil test",
        "Monitor pest levels regularly"
    ])

def get_growth_period(crop):
    periods = {
        'Wheat': '120-150 days',
        'Rice': '120-150 days',
        'Cotton': '180-200 days',
        'Maize': '90-120 days',
        'Sugarcane': '300-365 days',
        'Sunflower': '90-120 days',
        'Soybean': '90-120 days',
        'Groundnut': '100-150 days',
        'Tomato': '60-90 days',
        'Potato': '90-120 days'
    }
    return periods.get(crop, '90-150 days')

# ================================================================= #
# 🌦️ Weather, Market, Soil Routes (unchanged)
# ================================================================= #
@app.route('/api/weather/<city>', methods=['GET'])
def weather(city):
    return jsonify(weather_service.get_current_weather(city))

@app.route('/api/market-prices', methods=['GET'])
def market_prices():
    prices = market_service.get_current_prices()
    return jsonify({'success': True, 'prices': prices, 'timestamp': datetime.now().isoformat()})

@app.route('/api/soil/improvement/<soil_type>', methods=['GET'])
def soil_improvement(soil_type):
    tips = soil_analyzer.get_soil_improvement_tips(soil_type)
    return jsonify({'success': True, 'soil_type': soil_type, 'tips': tips})


@app.route('/api/auto-fill', methods=['GET'])
def auto_fill():
    state = request.args.get('state')
    season = request.args.get('season')

    print(f"[DEBUG] Auto-fill called with state={state}, season={season}")

    connection = get_db_connection()
    if not connection:
        print("[v0]Database connection failed")
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                AVG(annual_rainfall) AS avg_rainfall,
                AVG(fertilizer) AS avg_fertilizer,
                AVG(pesticide) AS avg_pesticide,
                AVG(area) AS avg_area
            FROM crop_yield
            WHERE state = %s AND season = %s
        """, (state, season))
        result = cursor.fetchone()

        print(f"[DEBUG] Query result: {result}")

        if not result or not result['avg_rainfall']:
            print(f"[v0]No rows found for {state}+{season}, falling back to global avg")
            cursor.execute("""
                SELECT 
                    AVG(annual_rainfall) AS avg_rainfall,
                    AVG(fertilizer) AS avg_fertilizer,
                    AVG(pesticide) AS avg_pesticide,
                    AVG(area) AS avg_area
                FROM crop_yield
            """)
            result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'rainfall': round(result['avg_rainfall'] or 0, 2),
            'fertilizer': round(result['avg_fertilizer'] or 0, 2),
            'pesticide': round(result['avg_pesticide'] or 0, 2),
            'area': round(result['avg_area'] or 0, 2)
        })

    except Exception as e:
        print(f"[v0] Error in auto_fill: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



