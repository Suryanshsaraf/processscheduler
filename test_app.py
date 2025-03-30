"""
Test script for the job shop scheduler application.
This performs a basic integration test by starting the app
and testing the API endpoints.
"""

import unittest
import json
import os
import sys
from app import app


class TestJobShopScheduler(unittest.TestCase):
    """Test cases for the Job Shop Scheduler application."""

    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        """Test the home route returns the frontend."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_algorithms_route(self):
        """Test the algorithms route returns valid data."""
        response = self.app.get('/algorithms')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('algorithms', data)
        self.assertIn('GBFS', data['algorithms'])
        self.assertIn('A*', data['algorithms'])
        
    def test_schedule_route(self):
        """Test the schedule route with sample data."""
        test_data = {
            "jobs": [
                {"operations": [{"machine": 0, "processing_time": 3}, 
                               {"machine": 1, "processing_time": 2}]},
                {"operations": [{"machine": 0, "processing_time": 2}, 
                               {"machine": 1, "processing_time": 4}]}
            ],
            "algorithm": "GBFS"
        }
        
        response = self.app.post('/schedule', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Basic validation of response structure
        self.assertIn('schedule', data)
        self.assertIn('makespan', data)
        self.assertIn('total_processing_time', data)
        self.assertIn('num_jobs', data)
        self.assertIn('num_machines', data)
        self.assertIn('visualization_data', data)
        
        # Validate the schedule length matches input jobs
        self.assertEqual(len(data['schedule']), len(test_data['jobs']))
        
        # Validate the number of jobs and machines
        self.assertEqual(data['num_jobs'], len(test_data['jobs']))


if __name__ == '__main__':
    unittest.main() 