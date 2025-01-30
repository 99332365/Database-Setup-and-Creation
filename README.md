# Database-Setup-and-Creation
# TCP Communication and Temperature Position Visualization Node for ROS 2

This project implements a ROS2 (Robot Operating System 2) node that communicates with an external device (FiPy) over TCP/IP to send and receive temperature and position data. The received data is stored in an SQLite database, and a visualization marker is published in RViz to represent the temperature and position.

## Features

- **TCP Communication**: 
  - Sends temperature and position data to a remote FiPy device.
  - Receives temperature and position data from the FiPy device.
  
- **SQLite Database**: 
  - Stores received temperature and position data in a local SQLite database.
  
- **RViz Visualization**: 
  - Publishes markers to RViz, where the position is visualized as a sphere, with the color representing the temperature.

- **Data Generation**:
  - Can insert random data for testing purposes if the FiPy device is unavailable.

## Prerequisites

- ROS 2 (tested with `foxy`).
- Python 3.x.
- SQLite database (automatically managed by the code).
- RViz for visualization.
- FiPy device (optional for testing communication).

## Installation

1. **Install ROS 2**: Follow the official ROS 2 installation guide for your platform: https://docs.ros.org/en/foxy/Installation.html

2. **Create a ROS 2 Workspace**:
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws/src
   Database Setup and Creation
The project uses an SQLite database to store temperature and position data. Follow these steps to set up and create the database:

Create the database and table:
The database is automatically created when you run the code, but you can also create it manually by running the following Python script:
import sqlite3

# Connect to SQLite database (it will be created if it doesn't exist)
db_connection = sqlite3.connect('temperature_data.db')
db_cursor = db_connection.cursor()

# Create the table if it doesn't exist
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS temperature_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        position_x REAL,
        position_y REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Commit the changes and close the connection
db_connection.commit()
db_connection.close()

print("Database and table created successfully.")
This will create the temperature_data.db file and a table to store temperature and position data.
Insert random data:
If you don't have the FiPy device, you can generate random data using the insert_random_data() function. This will insert random temperature and position values into the database for testing:
import sqlite3
import random

def insert_random_data(num_entries=10):
    db_connection = sqlite3.connect('temperature_data.db')
    db_cursor = db_connection.cursor()

    for _ in range(num_entries):
        temperature = random.uniform(15.0, 35.0)  # Température entre 15 et 35°C
        position_x = random.uniform(-10.0, 10.0)  # Position x entre -10 et 10
        position_y = random.uniform(-10.0, 10.0)  # Position y entre -10 et 10
        db_cursor.execute('''
            INSERT INTO temperature_data (temperature, position_x, position_y)
            VALUES (?, ?, ?)
        ''', (temperature, position_x, position_y))

    db_connection.commit()
    db_connection.close()

    print(f"Inserted {num_entries} random data entries.")

