-- Create database for crop recommendation system
CREATE DATABASE IF NOT EXISTS crop_recommendation;
USE crop_recommendation;

-- Table for crop yield data
CREATE TABLE IF NOT EXISTS crop_yield (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop VARCHAR(100) NOT NULL,
    crop_year INT NOT NULL,
    season VARCHAR(50) NOT NULL,
    state VARCHAR(100) NOT NULL,
    area DECIMAL(15, 2),
    production DECIMAL(15, 2),
    annual_rainfall DECIMAL(10, 2),
    fertilizer DECIMAL(15, 2),
    pesticide DECIMAL(15, 2),
    yield_value DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_crop (crop),
    INDEX idx_state (state),
    INDEX idx_season (season),
    INDEX idx_year (crop_year)
);

-- Table for crop information and recommendations
CREATE TABLE IF NOT EXISTS crop_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) UNIQUE NOT NULL,
    optimal_rainfall_min DECIMAL(10, 2),
    optimal_rainfall_max DECIMAL(10, 2),
    optimal_temp_min DECIMAL(5, 2),
    optimal_temp_max DECIMAL(5, 2),
    soil_type VARCHAR(200),
    growing_season VARCHAR(100),
    pros TEXT,
    cons TEXT,
    market_demand VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for user queries and recommendations
CREATE TABLE IF NOT EXISTS user_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    season VARCHAR(50),
    rainfall DECIMAL(10, 2),
    temperature DECIMAL(5, 2),
    soil_type VARCHAR(100),
    recommended_crops JSON,
    query_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample crop information
INSERT INTO crop_info (crop_name, optimal_rainfall_min, optimal_rainfall_max, optimal_temp_min, optimal_temp_max, soil_type, growing_season, pros, cons, market_demand) VALUES
('Rice', 1000, 2000, 20, 35, 'Clay loam, Alluvial', 'Kharif', 'High yield, Staple food, Good market demand, Multiple varieties available', 'High water requirement, Labor intensive, Pest susceptible, Long growing period', 'High'),
('Wheat', 400, 800, 10, 25, 'Loamy, Clay loam', 'Rabi', 'Staple crop, Good storage life, Mechanized farming possible, Stable market', 'Requires irrigation, Susceptible to rust diseases, Price fluctuations', 'High'),
('Cotton', 600, 1200, 21, 30, 'Black soil, Alluvial', 'Kharif', 'High commercial value, Export potential, Multiple uses, Good income', 'Pest prone, High input cost, Water intensive, Market volatility', 'High'),
('Sugarcane', 1500, 2500, 20, 35, 'Loamy, Clay loam', 'Year-round', 'High returns, Long crop duration, Multiple products, Assured market', 'Very high water need, Heavy fertilizer requirement, Long maturity period', 'High'),
('Maize', 500, 1000, 18, 27, 'Well-drained loam', 'Kharif/Rabi', 'Fast growing, Versatile crop, Good fodder value, Multiple uses', 'Pest attacks, Storage issues, Price variations, Requires good drainage', 'Medium'),
('Pulses', 400, 800, 20, 30, 'Loamy, Sandy loam', 'Rabi/Kharif', 'Nitrogen fixing, Low water need, Good protein source, Improves soil', 'Low yield, Pest susceptible, Market price fluctuations, Storage pests', 'Medium'),
('Groundnut', 500, 1250, 20, 30, 'Sandy loam, Red soil', 'Kharif', 'Oil seed crop, Good returns, Export quality, Multiple products', 'Pest diseases, Requires well-drained soil, Labor intensive harvesting', 'Medium'),
('Soybean', 600, 1000, 20, 30, 'Well-drained loam', 'Kharif', 'High protein, Oil extraction, Nitrogen fixing, Good market', 'Pest problems, Requires good drainage, Processing needed, Price volatility', 'High');
