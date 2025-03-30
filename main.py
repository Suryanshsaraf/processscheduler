from job import Job
from machine import Machine
from scheduler import Scheduler

# Define jobs and machines
jobs = [
    Job(1, 5, 2, 1),
    Job(2, 3, 1, 2),
    Job(3, 2, 3, 1),
    Job(4, 6, 2, 2)
]
machines = [Machine(1), Machine(2)]

# Run the scheduler
scheduler = Scheduler(jobs, machines)
schedule = scheduler.schedule_jobs()

# Print schedule
print("Job Schedule:")
for job_id, start, end, machine in schedule:
    print(f"Job {job_id}: Start {start}, End {end}, Machine {machine}")