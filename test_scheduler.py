import unittest
from job import Job
from machine import Machine
from scheduler import Scheduler

class TestScheduler(unittest.TestCase):
    def test_scheduler(self):
        jobs = [Job(1, 3, 1, 1), Job(2, 2, 2, 2)]
        machines = [Machine(1), Machine(2)]
        scheduler = Scheduler(jobs, machines)
        schedule = scheduler.schedule_jobs()
        self.assertEqual(len(schedule), 2)  # Ensure all jobs are scheduled

if __name__ == '__main__':
    unittest.main()