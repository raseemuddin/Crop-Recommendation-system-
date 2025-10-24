<<<<<<< HEAD
# Crop Recommendation System

A comprehensive Flask-based web application for crop recommendation using machine learning, live weather data, and market prices.

## Features

- 🌾 ML-based crop recommendations using Random Forest
- 🌤️ Live weather integration with agricultural forecasting
- 💰 Real-time market prices and trends
- 🌍 Multi-language support (Hindi, Telugu, Marathi, Punjabi, Tamil, Kannada, English)
- 📊 Data-driven insights with pros/cons analysis
- 🌱 Soil analysis and recommendations
- 📈 Feature importance visualization

## Setup Instructions

### 1. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configure Environment Variables

\`\`\`bash
cp .env.example .env
# Edit .env with your credentials:
# - MySQL database credentials
# - OpenWeatherMap API key (get free key from openweathermap.org)
# - Other API keys as needed
\`\`\`

### 3. Database Setup

\`\`\`bash
# Create the database and tables
mysql -u root -p < scripts/create_database.sql

# Or run the SQL script directly in MySQL
\`\`\`

### 4. Load Dataset into Database

\`\`\`bash
# Analyze the dataset first (optional)
python scripts/analyze_dataset.py

# Load data into MySQL
python scripts/load_data_to_mysql.py
\`\`\`

### 5. Train the Machine Learning Model

\`\`\`bash
# Train the model with hyperparameter tuning
python scripts/train_model.py

# This will:
# - Download and preprocess the dataset
# - Train a Random Forest classifier
# - Perform hyperparameter tuning
# - Generate evaluation metrics
# - Save model artifacts to models/ directory
# - Create visualization plots
\`\`\`

### 6. Run the Application

\`\`\`bash
python app.py
\`\`\`

Visit `http://localhost:5000` in your browser.

## Project Structure

\`\`\`
crop-recommendation-app/
├── app.py                          # Main Flask application
├── models/
│   ├── crop_predictor.py          # ML prediction class
│   ├── crop_recommendation_model.pkl  # Trained model
│   ├── scaler.pkl                 # Feature scaler
│   ├── crop_label_encoder.pkl     # Crop encoder
│   ├── label_encoders.pkl         # State/Season encoders
│   ├── feature_columns.pkl        # Feature names
│   ├── model_metadata.json        # Model info
│   └── visualizations/            # Training plots
├── scripts/
│   ├── train_model.py             # Model training script
│   ├── analyze_dataset.py         # Data analysis
│   ├── create_database.sql        # Database schema
│   └── load_data_to_mysql.py      # Data loading
├── utils/
│   ├── weather_api.py             # Weather integration
│   ├── market_api.py              # Market prices
│   ├── agmarknet_api.py           # Agricultural market data
│   ├── weather_forecast.py        # Weather forecasting
│   └── soil_analysis.py           # Soil recommendations
├── templates/
│   └── index.html                 # Main UI template
├── static/
│   ├── css/style.css              # Custom styles
│   ├── js/app.js                  # Main JavaScript
│   ├── js/voice.js                # Voice commands
│   └── js/translations.js         # Multi-language support
└── requirements.txt               # Python dependencies
\`\`\`

## API Endpoints

- `GET /` - Main application page
- `GET /api/states` - Get list of available states
- `GET /api/seasons` - Get list of available seasons
- `POST /api/recommend` - Get crop recommendations
- `GET /api/weather/<city>` - Get current weather data
- `GET /api/weather-forecast/<city>` - Get 5-day forecast
- `GET /api/market-prices` - Get current market prices
- `GET /api/market-prices/<crop>` - Get prices for specific crop
- `GET /api/soil-analysis` - Get soil recommendations

## Model Training Details

The machine learning model uses:
- **Algorithm**: Random Forest Classifier
- **Features**: Season, State, Area, Rainfall, Fertilizer, Pesticide, and derived features
- **Hyperparameter Tuning**: GridSearchCV with cross-validation
- **Evaluation**: Accuracy, precision, recall, F1-score, confusion matrix
- **Feature Engineering**: Fertilizer per area, pesticide per area ratios

Training outputs:
- Model accuracy and cross-validation scores
- Feature importance rankings
- Confusion matrix visualization
- Classification report for all crops

## Voice Commands

Supported commands (in multiple languages):
- "Show weather" / "मौसम दिखाओ"
- "Market prices" / "बाजार भाव"
- "Recommend crops" / "फसल सुझाव"
- "Change language" / "भाषा बदलें"

## Technologies Used

- **Backend**: Flask 3.0, Python 3.8+
- **Database**: MySQL 8.0+
- **ML**: scikit-learn, pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **APIs**: OpenWeatherMap, Agricultural Market APIs
- **Voice**: Web Speech API

## Dataset

The application uses historical crop yield data including:
- 20+ crop varieties
- State-wise production data (all Indian states)
- Seasonal patterns (Kharif, Rabi, Summer)
- Annual rainfall data
- Fertilizer and pesticide usage
- Yield metrics and production statistics

## Deployment

### Using Docker

\`\`\`bash
# Build and run with docker-compose
docker-compose up -d

# Or build manually
docker build -t crop-recommendation .
docker run -p 5000:5000 crop-recommendation
\`\`\`

See `DEPLOYMENT.md` for detailed deployment instructions.

## Troubleshooting

**Model not loading?**
- Run `python scripts/train_model.py` to train the model first

**Database connection error?**
- Check MySQL is running: `sudo service mysql status`
- Verify credentials in `.env` file

**API errors?**
- Check your OpenWeatherMap API key is valid
- Ensure you have internet connectivity

**Voice commands not working?**
- Use HTTPS or localhost (required for Web Speech API)
- Check browser microphone permissions

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
=======
# Crop-Recommendation-system-
>>>>>>> 6f5b5130f7d07447d43d12050c6aa95574ed8ce1
