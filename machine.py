class Machine:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.available_time = 0  # Keeps track of when the machine is free