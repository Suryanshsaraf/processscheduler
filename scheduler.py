import heapq
import numpy as np
import time
import math
from collections import defaultdict, namedtuple
from ortools.sat.python import cp_model

# Node representation for search algorithms
class ScheduleNode:
    def __init__(self, jobs, machines, scheduled_jobs=None, unscheduled_jobs=None, parent=None, cost=0, action=None):
        self.jobs = jobs
        self.machines = machines
        self.scheduled_jobs = scheduled_jobs or []
        self.unscheduled_jobs = unscheduled_jobs or list(range(len(jobs)))
        self.parent = parent
        self.cost = cost  # g(n) in A*
        self.action = action  # The job that was scheduled to reach this state
        
    def get_path(self):
        """Get the path from the root to this node"""
        path = []
        current = self
        while current.parent:
            path.append(current.action)
            current = current.parent
        return list(reversed(path))
    
    def get_machine_times(self):
        """Get the current time for each machine"""
        machine_times = [0] * len(self.machines)
        for job_idx, start_time, machine_idx in self.scheduled_jobs:
            job = self.jobs[job_idx]
            end_time = start_time + job.processing_time
            machine_times[machine_idx] = max(machine_times[machine_idx], end_time)
        return machine_times
    
    def get_makespan(self):
        """Get the makespan of the current schedule"""
        if not self.scheduled_jobs:
            return 0
        return max(start_time + self.jobs[job_idx].processing_time 
                   for job_idx, start_time, _ in self.scheduled_jobs)
    
    def is_goal(self):
        """Check if all jobs are scheduled"""
        return len(self.unscheduled_jobs) == 0
    
    def get_successors(self):
        """Generate all possible next states by scheduling one of the unscheduled jobs"""
        successors = []
        machine_times = self.get_machine_times()
        
        for job_idx in self.unscheduled_jobs:
            job = self.jobs[job_idx]
            machine_idx = job.machine_id - 1  # Convert 1-based to 0-based
            
            # Start time is the current time of the machine
            start_time = machine_times[machine_idx]
            
            # Create new lists for the next state
            new_scheduled = self.scheduled_jobs + [(job_idx, start_time, machine_idx)]
            new_unscheduled = [j for j in self.unscheduled_jobs if j != job_idx]
            
            # Create the successor node
            successor = ScheduleNode(
                self.jobs,
                self.machines,
                new_scheduled,
                new_unscheduled,
                self,
                self.cost + job.processing_time,  # Incremental cost
                (job_idx, start_time, machine_idx)
            )
            
            successors.append(successor)
        
        return successors
    
    def __lt__(self, other):
        """Comparison for priority queue"""
        return self.cost < other.cost


class Scheduler:
    """Base Scheduler class defining common interface"""
    def __init__(self, jobs, machines):
        self.jobs = jobs
        self.machines = machines
        self.algorithm_name = "Base Scheduler"
        self.visualization_data = {
            "algorithm_name": self.algorithm_name,
            "search_iterations": 0,
            "nodes_expanded": 0,
            "solution_path": [],
            "execution_time": 0,
            "heuristic_values": []
        }
    
    def schedule_jobs(self):
        # This should be implemented by subclasses
        raise NotImplementedError
    
    def format_schedule(self, node):
        """Convert the internal schedule to the expected output format"""
        schedule = []
        for job_idx, start_time, machine_idx in node.scheduled_jobs:
            job = self.jobs[job_idx]
            job.start_time = start_time
            job.end_time = start_time + job.processing_time
            # Return format: (job_id, start_time, end_time, machine_id)
            schedule.append((job.job_id, start_time, job.end_time, machine_idx + 1))
        return sorted(schedule, key=lambda x: x[1])  # Sort by start time


class GBFSScheduler(Scheduler):
    """Greedy Best-First Search Scheduler"""
    def __init__(self, jobs, machines):
        super().__init__(jobs, machines)
        self.algorithm_name = "Greedy Best-First Search (GBFS)"
        self.visualization_data["algorithm_name"] = self.algorithm_name
    
    def heuristic(self, node):
        """
        Heuristic function for GBFS: Estimate of remaining completion time
        This is a combination of:
        1. Makespan so far
        2. Sum of processing times of unscheduled jobs
        3. Maximum processing time of unscheduled jobs
        """
        if node.is_goal():
            return 0
        
        # Calculate basic metrics
        current_makespan = node.get_makespan()
        
        # Sum of unscheduled processing times
        unscheduled_processing_time = sum(self.jobs[job_idx].processing_time 
                                        for job_idx in node.unscheduled_jobs)
        
        # Maximum processing time of unscheduled jobs
        max_unscheduled_time = max(self.jobs[job_idx].processing_time 
                                  for job_idx in node.unscheduled_jobs) if node.unscheduled_jobs else 0
        
        # Machine utilization imbalance (standard deviation of machine times)
        machine_times = node.get_machine_times()
        machine_std = np.std(machine_times) if len(machine_times) > 1 else 0
        
        # Combine factors - weighted sum
        h_value = (
            0.5 * current_makespan + 
            0.3 * (unscheduled_processing_time / len(self.machines)) +
            0.2 * max_unscheduled_time +
            0.1 * machine_std
        )
        
        return h_value
    
    def schedule_jobs(self):
        """Implement Greedy Best-First Search to find a schedule"""
        start_time = time.time()
        self.visualization_data["nodes_expanded"] = 0
        self.visualization_data["search_iterations"] = 0
        self.visualization_data["heuristic_values"] = []
        
        # Initialize the search with the starting node
        initial_node = ScheduleNode(self.jobs, self.machines)
        
        # Priority queue for GBFS (using heuristic values)
        frontier = [(self.heuristic(initial_node), 0, initial_node)]  # (heuristic, tiebreaker, node)
        frontier_set = {tuple(initial_node.unscheduled_jobs)}
        
        # Counter for tiebreaking nodes with the same heuristic
        counter = 1
        
        # For visualization: track nodes explored at each level
        self.visualization_data["exploration_by_level"] = defaultdict(int)
        
        while frontier:
            # Get the node with the lowest heuristic value
            h_value, _, current_node = heapq.heappop(frontier)
            frontier_set.remove(tuple(current_node.unscheduled_jobs))
            
            # Record the heuristic value for visualization
            current_level = len(self.jobs) - len(current_node.unscheduled_jobs)
            self.visualization_data["heuristic_values"].append({
                "level": current_level,
                "heuristic": h_value,
                "makespan": current_node.get_makespan()
            })
            self.visualization_data["exploration_by_level"][current_level] += 1
            
            # Increment nodes expanded counter
            self.visualization_data["nodes_expanded"] += 1
            
            # Check if we've reached the goal
            if current_node.is_goal():
                self.visualization_data["execution_time"] = time.time() - start_time
                self.visualization_data["solution_path"] = current_node.get_path()
                return self.format_schedule(current_node)
            
            # Expand the current node
            for successor in current_node.get_successors():
                # Skip if we've seen this state before
                successor_key = tuple(successor.unscheduled_jobs)
                if successor_key in frontier_set:
                    continue
                
                # Add to frontier with heuristic value
                successor_h = self.heuristic(successor)
                heapq.heappush(frontier, (successor_h, counter, successor))
                frontier_set.add(successor_key)
                counter += 1
            
            self.visualization_data["search_iterations"] += 1
        
        # If we exhaust the frontier without finding a solution
        self.visualization_data["execution_time"] = time.time() - start_time
        return []


class AStarScheduler(Scheduler):
    """A* Search Scheduler"""
    def __init__(self, jobs, machines):
        super().__init__(jobs, machines)
        self.algorithm_name = "A* Search"
        self.visualization_data["algorithm_name"] = self.algorithm_name
    
    def heuristic(self, node):
        """
        Heuristic function for A*: Admissible estimate of remaining completion time
        """
        if node.is_goal():
            return 0
        
        # Machine load balancing heuristic
        machine_times = node.get_machine_times()
        
        # Calculate remaining work per machine
        remaining_work_per_machine = defaultdict(int)
        for job_idx in node.unscheduled_jobs:
            job = self.jobs[job_idx]
            machine_idx = job.machine_id - 1
            remaining_work_per_machine[machine_idx] += job.processing_time
        
        # For each machine, estimate completion time
        estimated_completion_times = []
        for machine_idx, current_time in enumerate(machine_times):
            # Time to complete all remaining jobs on this machine
            completion_time = current_time + remaining_work_per_machine.get(machine_idx, 0)
            estimated_completion_times.append(completion_time)
        
        # A* heuristic: maximum estimated completion time
        h_value = max(estimated_completion_times) if estimated_completion_times else 0
        
        return h_value
    
    def schedule_jobs(self):
        """Implement A* Search to find optimal schedule"""
        start_time = time.time()
        self.visualization_data["nodes_expanded"] = 0
        self.visualization_data["search_iterations"] = 0
        self.visualization_data["heuristic_values"] = []
        
        # Initialize the search with the starting node
        initial_node = ScheduleNode(self.jobs, self.machines)
        
        # Priority queue for A* (using f(n) = g(n) + h(n))
        frontier = [(self.heuristic(initial_node), 0, initial_node)]  # (f_value, tiebreaker, node)
        frontier_set = {tuple(initial_node.unscheduled_jobs): 0}  # Maps state to g-value
        
        # Counter for tiebreaking nodes with the same f-value
        counter = 1
        
        # For visualization: track nodes explored at each level
        self.visualization_data["exploration_by_level"] = defaultdict(int)
        
        while frontier:
            # Get the node with the lowest f value
            f_value, _, current_node = heapq.heappop(frontier)
            current_state = tuple(current_node.unscheduled_jobs)
            
            # Skip if we've found a better path to this state
            if current_state in frontier_set and frontier_set[current_state] < current_node.cost:
                continue
            
            # Remove from frontier set
            if current_state in frontier_set:
                del frontier_set[current_state]
            
            # Record the f-value for visualization
            current_level = len(self.jobs) - len(current_node.unscheduled_jobs)
            h_value = f_value - current_node.cost  # h(n) = f(n) - g(n)
            self.visualization_data["heuristic_values"].append({
                "level": current_level,
                "f_value": f_value,
                "g_value": current_node.cost,
                "h_value": h_value,
                "makespan": current_node.get_makespan()
            })
            self.visualization_data["exploration_by_level"][current_level] += 1
            
            # Increment nodes expanded counter
            self.visualization_data["nodes_expanded"] += 1
            
            # Check if we've reached the goal
            if current_node.is_goal():
                self.visualization_data["execution_time"] = time.time() - start_time
                self.visualization_data["solution_path"] = current_node.get_path()
                return self.format_schedule(current_node)
            
            # Expand the current node
            for successor in current_node.get_successors():
                successor_state = tuple(successor.unscheduled_jobs)
                
                # If we've seen this state before with a better g value, skip
                if successor_state in frontier_set and frontier_set[successor_state] <= successor.cost:
                    continue
                
                # Add to frontier with f value = g + h
                successor_h = self.heuristic(successor)
                successor_f = successor.cost + successor_h
                heapq.heappush(frontier, (successor_f, counter, successor))
                frontier_set[successor_state] = successor.cost
                counter += 1
            
            self.visualization_data["search_iterations"] += 1
        
        # If we exhaust the frontier without finding a solution
        self.visualization_data["execution_time"] = time.time() - start_time
        return []

# Alias for backward compatibility
OptimizedScheduler = AStarScheduler

class OptimizedScheduler:
    """Advanced scheduler using Google OR-Tools CP-SAT solver"""
    
    def __init__(self, jobs, machines):
        self.jobs = jobs
        self.machines = machines
        
    def schedule_jobs(self):
        # Create the model
        model = cp_model.CpModel()
        
        # Define variables
        all_jobs = range(len(self.jobs))
        all_machines = range(len(self.machines))
        
        # Maximum possible horizon (sum of all processing times)
        horizon = sum(job.processing_time for job in self.jobs)
        
        # Create job start variables for each machine
        starts = {}
        ends = {}
        intervals = {}
        
        # Create job intervals and add machine constraints
        for j in all_jobs:
            job = self.jobs[j]
            for m in all_machines:
                machine = self.machines[m]
                
                # If job can be processed on this machine
                if job.machine_id == machine.machine_id:
                    suffix = f'_{j}_{m}'
                    starts[(j, m)] = model.NewIntVar(0, horizon, f'start{suffix}')
                    ends[(j, m)] = model.NewIntVar(0, horizon, f'end{suffix}')
                    intervals[(j, m)] = model.NewIntervalVar(
                        starts[(j, m)], 
                        job.processing_time, 
                        ends[(j, m)], 
                        f'interval{suffix}'
                    )
        
        # Add no-overlap constraints for machines
        for m in all_machines:
            machine_intervals = []
            for j in all_jobs:
                job = self.jobs[j]
                if (j, m) in intervals and job.machine_id == self.machines[m].machine_id:
                    machine_intervals.append(intervals[(j, m)])
            model.AddNoOverlap(machine_intervals)
        
        # Objective function: Minimize makespan (maximum end time)
        makespan = model.NewIntVar(0, horizon, 'makespan')
        for j in all_jobs:
            for m in all_machines:
                if (j, m) in ends:
                    model.Add(ends[(j, m)] <= makespan)
        
        model.Minimize(makespan)
        
        # Solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        schedule = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for j in all_jobs:
                job = self.jobs[j]
                for m in all_machines:
                    if (j, m) in starts and job.machine_id == self.machines[m].machine_id:
                        start_time = solver.Value(starts[(j, m)])
                        end_time = solver.Value(ends[(j, m)])
                        job.start_time = start_time
                        job.end_time = end_time
                        schedule.append((job.job_id, start_time, end_time, self.machines[m].machine_id))
        
        # Sort the schedule by start time for better visualization
        schedule.sort(key=lambda x: x[1])
        return schedule