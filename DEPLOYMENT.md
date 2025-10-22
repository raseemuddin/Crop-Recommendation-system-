# Deployment Guide

## Prerequisites

1. **Python 3.8+** installed
2. **MySQL 8.0+** installed and running
3. **pip** package manager
4. API keys for:
   - OpenWeatherMap (for weather data)
   - Optional: Market data APIs

## Step-by-Step Deployment

### 1. Clone/Download the Project

\`\`\`bash
# If using git
git clone <repository-url>
cd crop-recommendation-app

# Or extract the ZIP file
unzip crop-recommendation-app.zip
cd crop-recommendation-app
\`\`\`

### 2. Set Up Virtual Environment

\`\`\`bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
\`\`\`

### 3. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Configure MySQL Database

\`\`\`bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE crop_recommendation;

# Exit MySQL
exit
\`\`\`

### 5. Set Up Environment Variables

\`\`\`bash
# Copy example env file
cp .env.example .env

# Edit .env file with your credentials
# Use any text editor (notepad, vim, nano, etc.)
nano .env
\`\`\`

Update the following in `.env`:
\`\`\`
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=crop_recommendation

WEATHER_API_KEY=your_openweathermap_api_key
SECRET_KEY=your_secret_key_here
\`\`\`

### 6. Initialize Database

\`\`\`bash
# Run database creation script
mysql -u root -p crop_recommendation < scripts/create_database.sql

# Or use Python script
python scripts/create_database.py
\`\`\`

### 7. Load Dataset

\`\`\`bash
# Analyze dataset
python scripts/analyze_dataset.py

# Load data into MySQL
python scripts/load_data_to_mysql.py
\`\`\`

### 8. Train ML Model

\`\`\`bash
# Train the crop recommendation model
python -c "from models.crop_predictor import CropPredictor; cp = CropPredictor(); cp.train()"
\`\`\`

### 9. Run the Application

\`\`\`bash
# Start Flask development server
python app.py
\`\`\`

The application will be available at: `http://localhost:5000`

## Production Deployment

### Using Gunicorn (Linux/Mac)

\`\`\`bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
\`\`\`

### Using Waitress (Windows)

\`\`\`bash
# Install waitress
pip install waitress

# Run with waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
\`\`\`

### Using Docker

\`\`\`bash
# Build Docker image
docker build -t crop-recommendation-app .

# Run container
docker run -p 5000:5000 --env-file .env crop-recommendation-app
\`\`\`

## API Keys Setup

### OpenWeatherMap API Key

1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file

### Optional: Market Data APIs

For production, integrate with:
- Agmarknet API (https://agmarknet.gov.in/)
- Data.gov.in APIs (https://data.gov.in/)

## Troubleshooting

### Database Connection Issues

\`\`\`bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
# Or check Windows Services for MySQL

# Test connection
mysql -u root -p -e "SHOW DATABASES;"
\`\`\`

### Port Already in Use

\`\`\`bash
# Change port in app.py
# Or kill process using port 5000
# Linux/Mac:
lsof -ti:5000 | xargs kill -9
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
\`\`\`

### Missing Dependencies

\`\`\`bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt
\`\`\`

## Performance Optimization

1. **Enable MySQL Query Cache**
2. **Use Redis for session management**
3. **Implement API response caching**
4. **Use CDN for static files**
5. **Enable gzip compression**

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong MySQL passwords
- [ ] Enable HTTPS in production
- [ ] Implement rate limiting
- [ ] Sanitize user inputs
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable CORS properly
- [ ] Implement authentication if needed

## Monitoring

Consider adding:
- Application logging
- Error tracking (Sentry)
- Performance monitoring
- Database query optimization
- API usage tracking

## Support

For issues or questions:
- Check logs in `app.log`
- Review error messages
- Consult documentation
- Contact support team
