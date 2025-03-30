class Job:
    def __init__(self, job_id, processing_time, priority, machine_id):
        self.job_id = job_id
        self.processing_time = processing_time
        self.priority = priority
        self.machine_id = machine_id
        self.start_time = None
        self.end_time = None