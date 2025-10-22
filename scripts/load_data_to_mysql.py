import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
}

def create_database_and_tables():
    """Create database and tables if they don't exist"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()

        print("[v0] Creating database if not exists...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS crop_recommendation")
        cursor.execute("USE crop_recommendation")

        print("[v0] Creating crop_yield table if not exists...")
        create_table_query = """
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
        )
        """
        cursor.execute(create_table_query)

        print("[v0] Creating crop_info table if not exists...")
        create_crop_info_query = """
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
        )
        """
        cursor.execute(create_crop_info_query)

        print("[v0] Creating user_queries table if not exists...")
        create_queries_table = """
        CREATE TABLE IF NOT EXISTS user_queries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            state VARCHAR(100),
            season VARCHAR(50),
            rainfall DECIMAL(10, 2),
            temperature DECIMAL(5, 2),
            soil_type VARCHAR(100),
            recommended_crops JSON,
            query_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_queries_table)

        connection.commit()
        cursor.close()
        connection.close()
        print("[v0]Database and tables created successfully!")

        return True

    except Error as e:
        print(f"[v0]Error creating database/tables: {e}")
        return False


def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='crop_recommendation'
        )
        if connection.is_connected():
            print("[v0]Connected to MySQL database")
            return connection
    except Error as e:
        print(f"[v0]Error connecting to MySQL: {e}")
        return None


def load_csv_data():
    """Load and process local CSV data"""
    # ⚠️ Change the path below to your CSV file location


    print(f"[v0]Loading dataset from: {"crop_yield.csv"}")
    df = pd.read_csv("crop_yield.csv")

    print(f"[v0]Loaded {len(df)} records from local CSV")
    print("[v0] Columns found:", list(df.columns))

    return df


def insert_data(connection, df):
    """Insert data into MySQL database"""
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM crop_yield")
    existing_count = cursor.fetchone()[0]

    if existing_count > 0:
        print(f"[v0]Table already contains {existing_count} records. Clearing old data...")
        cursor.execute("TRUNCATE TABLE crop_yield")
        connection.commit()

    insert_query = """
    INSERT INTO crop_yield 
    (crop, crop_year, season, state, area, production, annual_rainfall, fertilizer, pesticide, yield_value)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    records_inserted = 0
    for index, row in df.iterrows():
        try:
            values = (
                row['Crop'],
                int(row['Crop_Year']),
                row['Season'],
                row['State'],
                float(row['Area']) if pd.notna(row['Area']) else None,
                float(row['Production']) if pd.notna(row['Production']) else None,
                float(row['Annual_Rainfall']) if pd.notna(row['Annual_Rainfall']) else None,
                float(row['Fertilizer']) if pd.notna(row['Fertilizer']) else None,
                float(row['Pesticide']) if pd.notna(row['Pesticide']) else None,
                float(row['Yield']) if pd.notna(row['Yield']) else None
            )
            cursor.execute(insert_query, values)
            records_inserted += 1

            if records_inserted % 1000 == 0:
                print(f"[v0] Inserted {records_inserted} records...")

        except Exception as e:
            print(f"[v0]Error inserting row {index}: {e}")
            continue

    connection.commit()
    print(f"[v0]Successfully inserted {records_inserted} records into crop_yield table")
    cursor.close()


def main():
    print("[v0]Step 1: Creating database and tables...")
    if not create_database_and_tables():
        print("[v0]Failed to create database/tables. Exiting...")
        return

    print("\n[v0]Step 2: Loading local CSV data...")
    df = load_csv_data()

    print("\n[v0]Step 3: Connecting to database...")
    connection = create_connection()

    if connection:
        print("\n[v0]Step 4: Inserting data into database...")
        insert_data(connection, df)
        connection.close()
        print("\n[v0]Database setup completed successfully!")
        print("[v0] You can now run your Flask app.")
    else:
        print("[v0]Failed to connect to database")


if __name__ == "__main__":
    main()
