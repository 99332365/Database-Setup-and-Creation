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
