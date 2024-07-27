# Unrelated Parallel Machine Scheduling Problem

## Introduction
Simulates the production process of unrelated parallel machines.

## Features
- Customize the number of machines and jobs, and randomly generate arrival times, machine processing times, and due dates
- Includes 7 different dispatching rules
- Displays the arrival, start processing, and completion times for each job and generates a Gantt chart
- Shows the tardiness for each job, machine utilization, and makespan

## Requirements
- Python
    - NumPy
    - Simpy
    - Matplotlib
    - Pandas
    - XlsxWriter

## Usage
1. **Install Dependencies**
    - Install basic dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. **Setup Parameters**  
    - In `test_instance_generator.py`, set the setup time limit, processing time limit, and arrival time factor:
    ```python
    SETUP_UL = 20
    PT_UL = 100
    AT_FACTOR = 50
    ```

    - In `main.py`, set the number of jobs and machines:
    ```python
    N = 8
    M = 3
    ```

3. **Decide Scheduling Rules**
   - Modify the `main.py` file to set the scheduling rule by changing the `action` variable.
   ```python
   action = 0
   ```
   
   - The scheduling rules corresponding to different numbers are as follows:
    ```python
    if action == 0:
        # First In First Out (FIFO)
    elif action == 1:
        # Last In First Out (LIFO)
    elif action == 2:
        # Shortest Processing Time (SPT)
    elif action == 3:
        # Minimize Setup Time (MST)
    elif action == 4:
        # Earliest Due Date (EDD)
    elif action == 5:
        # Latest Slack Time (LST)
    elif action == 6:
        # Critical Ratio (CR)
    ```

3. **Run the Simulation**
    ```bash
    python main.py
    ```

## Example
Production Process  
![pic1](/example_pic/process.JPG)

Gantt
![pic2](/example_pic/gantt.jpeg)

KPI  
![pic3](/example_pic/kpi.JPG)