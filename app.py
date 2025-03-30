from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from src.job import Job
from src.machine import Machine
from src.scheduler import Scheduler, GBFSScheduler, AStarScheduler

app = Flask(__name__, static_folder='frontend')
CORS(app)  # Enable CORS for all routes

# Serve frontend files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    # Check if path exists in frontend folder
    if os.path.exists(os.path.join('frontend', path)):
        return send_from_directory('frontend', path)
    else:
        return send_from_directory('frontend', 'index.html')

@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.json
    jobs = []
    
    for job_data in data.get("jobs", []):
        job_id = job_data.get("jobId")
        processing_time = int(job_data.get("processingTime"))
        priority = int(job_data.get("priority", 1))  # Default priority to 1 if not provided
        machine_id = int(job_data.get("machine"))
        
        jobs.append(Job(job_id, processing_time, priority, machine_id))
    
    # Create machines based on the number requested
    num_machines = int(data.get("numMachines", 2))  # Default to 2 machines
    machines = [Machine(i+1) for i in range(num_machines)]
    
    # Select scheduler based on request
    scheduler_type = data.get("schedulerType", "gbfs")
    
    if scheduler_type == "astar":
        scheduler = AStarScheduler(jobs, machines)
    else:  # Default to GBFS
        scheduler = GBFSScheduler(jobs, machines)
    
    # Run the scheduler
    schedule_result = scheduler.schedule_jobs()
    
    # Return more comprehensive scheduling information including visualization data
    return jsonify({
        "schedule": schedule_result,
        "makespan": max([job.end_time for job in jobs]) if jobs else 0,
        "totalProcessingTime": sum([job.processing_time for job in jobs]),
        "numJobs": len(jobs),
        "numMachines": len(machines),
        "visualization": scheduler.visualization_data
    })

@app.route("/algorithms", methods=["GET"])
def get_algorithms():
    # Provide information about available scheduling algorithms
    return jsonify({
        "algorithms": [
            {
                "id": "gbfs",
                "name": "Greedy Best-First Search (GBFS)",
                "description": "AI search algorithm that uses a heuristic to determine the next best node to explore."
            },
            {
                "id": "astar",
                "name": "A* Search Algorithm",
                "description": "AI search algorithm that uses both path cost and heuristic to find the optimal solution."
            }
        ]
    })

if __name__ == "__main__":
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)