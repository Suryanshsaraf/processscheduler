# Advanced Job Shop Scheduler

An advanced job shop scheduling application with multiple optimization algorithms and visual scheduling representations.

## Features

- **Multiple Scheduling Algorithms**:
  - Standard priority-based scheduler with heuristics
  - Optimized scheduler using Google OR-Tools constraint programming
  
- **Interactive Interface**:
  - Define custom jobs with processing times, priorities, and machine assignments
  - Generate random jobs for testing
  - Visualize schedules with Gantt charts
  - Export results for further analysis

- **Performance Metrics**:
  - Makespan (total completion time)
  - Resource utilization
  - Total processing time

## Getting Started

### Prerequisites

- Python 3.8+
- Flask
- OR-Tools (Google's optimization library)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/job-shop-scheduler.git
   cd job-shop-scheduler
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Using the Scheduler

1. **Configure the Schedule**:
   - Select the scheduling algorithm
   - Set the number of jobs and machines
   - Click "Generate Job Inputs"

2. **Define Jobs**:
   - For each job, specify the processing time, priority, and machine assignment
   - Or click "Random Jobs" to generate sample data

3. **Generate Schedule**:
   - Click "Schedule Jobs" to run the algorithm
   - View the Gantt chart visualization and detailed results
   - Export the schedule if needed

## Scheduling Algorithms

### Standard Scheduler
Uses a priority queue to schedule jobs based on processing time and priority. Jobs with shorter processing time and higher priority are scheduled first.

### Optimized Scheduler (OR-Tools)
Uses Google's OR-Tools constraint programming solver to find the optimal schedule that minimizes makespan. This is more powerful for complex job shop problems.

## Example Use Cases

- Manufacturing production scheduling
- IT task scheduling
- Project resource allocation
- Service appointment scheduling

## License

MIT License
