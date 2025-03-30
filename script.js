// DOM elements
const jobForm = document.getElementById("job-form");
const generateBtn = document.getElementById("generate-btn");
const randomBtn = document.getElementById("random-btn");
const downloadBtn = document.getElementById("download-btn");
const showAlgoVizBtn = document.getElementById("show-algo-viz-btn");
const themeToggleBtn = document.getElementById("theme-toggle");
const jobInputsContainer = document.getElementById("job-inputs");
const scheduleOutput = document.getElementById("schedule-output");
const ganttChart = document.getElementById("gantt-chart");
const navTabs = document.querySelectorAll(".nav-tabs li");
const tabContents = document.querySelectorAll(".tab-content");

// Charts
let heuristicChart = null;
let explorationChart = null;

// Global state
let lastScheduleData = null;

// API URL will be relative in production or absolute in development
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? `http://${window.location.hostname}:5000` 
    : ''; 

const colors = [
    '#4285F4', '#EA4335', '#FBBC05', '#34A853', '#8E24AA', 
    '#0097A7', '#FF9800', '#795548', '#607D8B', '#1E88E5'
];

// Event listeners
document.addEventListener('DOMContentLoaded', initApp);
jobForm.addEventListener("submit", handleFormSubmit);
generateBtn.addEventListener("click", generateJobInputs);
randomBtn.addEventListener("click", generateRandomJobs);
downloadBtn.addEventListener("click", downloadResults);
showAlgoVizBtn.addEventListener("click", () => activateTab('visualization'));
themeToggleBtn.addEventListener("click", toggleTheme);
navTabs.forEach(tab => tab.addEventListener("click", () => activateTab(tab.dataset.tab)));

// Initialize the application
function initApp() {
    generateJobInputs();
    setThemeFromPreference();
}

// Theme functions
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update button icon and text
    const icon = themeToggleBtn.querySelector('i');
    const text = themeToggleBtn.querySelector('span');
    
    if (newTheme === 'dark') {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light Mode';
    } else {
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark Mode';
    }
    
    // Update charts if they exist
    updateChartsTheme();
}

function setThemeFromPreference() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const icon = themeToggleBtn.querySelector('i');
    const text = themeToggleBtn.querySelector('span');
    
    if (savedTheme === 'dark') {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light Mode';
    }
}

// Tab navigation
function activateTab(tabId) {
    // Update tab highlighting
    navTabs.forEach(tab => {
        if (tab.dataset.tab === tabId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Show selected tab content
    tabContents.forEach(content => {
        if (content.id === `${tabId}-tab`) {
            content.classList.add('active');
            
            // Initialize or update visualizations if on visualization tab
            if (tabId === 'visualization' && lastScheduleData) {
                updateAlgorithmVisualization(lastScheduleData.visualization);
            }
        } else {
            content.classList.remove('active');
        }
    });
}

// Main form submission handler
function handleFormSubmit(event) {
    event.preventDefault();
    
    const numJobs = parseInt(document.getElementById("num-jobs").value);
    const numMachines = parseInt(document.getElementById("num-machines").value);
    const schedulerType = document.getElementById("scheduler-type").value;
    
    // Collect job data
    const jobs = [];
    for (let i = 0; i < numJobs; i++) {
        const jobId = i + 1;
        const processingTime = parseInt(document.getElementById(`processing-time-${i}`).value);
        const priority = parseInt(document.getElementById(`priority-${i}`).value || 1);
        const machine = parseInt(document.getElementById(`machine-${i}`).value);
        
        jobs.push({ jobId, processingTime, priority, machine });
    }

    // Show loading state
    scheduleOutput.innerHTML = `<div class="loading">Running ${schedulerType.toUpperCase()} algorithm...</div>`;
    ganttChart.innerHTML = '<div class="loading">Generating visualization...</div>';
    
    // Display API URL being used (for debugging)
    console.log(`Connecting to backend at: ${API_BASE_URL}/schedule`);
    
    // Send job data to backend
    fetch(`${API_BASE_URL}/schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            jobs,
            numMachines,
            schedulerType
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        lastScheduleData = data;
        displayResults(data);
        
        // Populate the algorithm visualization tab
        updateAlgorithmVisualization(data.visualization);
    })
    .catch(error => {
        console.error("Error:", error);
        
        // Provide more specific error messages
        let errorMessage = error.message;
        
        // Check if it's a network error
        if (error.message === 'Failed to fetch') {
            errorMessage = `Unable to connect to the server at ${API_BASE_URL}. Please ensure that:
            <ul>
                <li>The Flask server is running on port 5000</li>
                <li>You've installed all required dependencies (flask, flask-cors, etc.)</li>
                <li>There are no firewall issues blocking the connection</li>
            </ul>
            <p>Try running <code>python3 app.py</code> in your terminal if the server isn't running.</p>`;
        }
        
        scheduleOutput.innerHTML = `<div class="error">
            <h4>Failed to schedule jobs:</h4>
            <p>${errorMessage}</p>
        </div>`;
        ganttChart.innerHTML = '';
    });
}

// Generate input fields for jobs
function generateJobInputs() {
    const numJobs = parseInt(document.getElementById("num-jobs").value);
    const numMachines = parseInt(document.getElementById("num-machines").value);
    
    jobInputsContainer.innerHTML = "";

    for (let i = 0; i < numJobs; i++) {
        const jobDiv = document.createElement("div");
        jobDiv.className = "job-entry";
        jobDiv.innerHTML = `
            <h4>Job ${i + 1}</h4>
            <div class="form-row">
                <div class="form-group">
                    <label>Processing Time:</label>
                    <input type="number" id="processing-time-${i}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Priority:</label>
                    <input type="number" id="priority-${i}" min="1" max="10" value="1">
                </div>
            </div>
            <div class="form-group">
                <label>Machine:</label>
                <select id="machine-${i}" required>
                    ${generateMachineOptions(numMachines)}
                </select>
            </div>
        `;
        jobInputsContainer.appendChild(jobDiv);
    }
}

// Generate options for machine select
function generateMachineOptions(numMachines) {
    let options = '';
    for (let i = 1; i <= numMachines; i++) {
        options += `<option value="${i}">Machine ${i}</option>`;
    }
    return options;
}

// Generate random job data
function generateRandomJobs() {
    const numJobs = parseInt(document.getElementById("num-jobs").value);
    const numMachines = parseInt(document.getElementById("num-machines").value);
    
    for (let i = 0; i < numJobs; i++) {
        // Random processing time between 2 and 20
        document.getElementById(`processing-time-${i}`).value = Math.floor(Math.random() * 19) + 2;
        
        // Random priority between 1 and 10
        document.getElementById(`priority-${i}`).value = Math.floor(Math.random() * 10) + 1;
        
        // Random machine assignment
        document.getElementById(`machine-${i}`).value = Math.floor(Math.random() * numMachines) + 1;
    }
}

// Display scheduling results
function displayResults(data) {
    // Update metrics
    document.getElementById("makespan").textContent = data.makespan;
    document.getElementById("num-jobs-metric").textContent = data.numJobs;
    document.getElementById("num-machines-metric").textContent = data.numMachines;
    document.getElementById("total-processing").textContent = data.totalProcessingTime;
    
    // Display schedule details
    const scheduleHtml = data.schedule.map(job => 
        `<div class="job-detail">
            <span class="job-id">Job ${job[0]}</span>: 
            Start: ${job[1]}, End: ${job[2]}, 
            Machine: ${job[3]}
        </div>`
    ).join('');
    
    scheduleOutput.innerHTML = scheduleHtml || "<p>No feasible schedule found.</p>";
    
    // Generate Gantt chart
    generateGanttChart(data);
}

// Generate Gantt chart visualization
function generateGanttChart(data) {
    ganttChart.innerHTML = '';
    
    if (!data.schedule || data.schedule.length === 0) {
        ganttChart.innerHTML = '<p>No schedule data to display</p>';
        return;
    }
    
    // Find makespan to set chart width
    const makespan = data.makespan;
    const timeScale = Math.max(500, makespan * 30); // At least 500px wide
    
    // Group jobs by machine
    const machineJobs = {};
    for (const job of data.schedule) {
        const [jobId, startTime, endTime, machineId] = job;
        if (!machineJobs[machineId]) {
            machineJobs[machineId] = [];
        }
        machineJobs[machineId].push({
            jobId,
            startTime,
            endTime,
            duration: endTime - startTime
        });
    }
    
    // Create timeline header
    const timelineHeader = document.createElement('div');
    timelineHeader.className = 'timeline-header';
    timelineHeader.style.width = `${timeScale}px`;
    
    // Add time markers
    const timeStep = Math.max(1, Math.ceil(makespan / 10));
    for (let t = 0; t <= makespan; t += timeStep) {
        const marker = document.createElement('div');
        marker.className = 'time-marker';
        marker.textContent = t;
        marker.style.left = `${(t / makespan) * timeScale}px`;
        timelineHeader.appendChild(marker);
    }
    
    ganttChart.appendChild(timelineHeader);
    
    // Create machine rows
    Object.keys(machineJobs).sort((a, b) => a - b).forEach((machineId) => {
        const machineRow = document.createElement('div');
        machineRow.className = 'machine-row';
        
        const machineLabel = document.createElement('div');
        machineLabel.className = 'machine-label';
        machineLabel.textContent = `Machine ${machineId}`;
        
        const timeline = document.createElement('div');
        timeline.className = 'timeline';
        timeline.style.width = `${timeScale}px`;
        
        // Add job blocks
        machineJobs[machineId].forEach(job => {
            const jobBlock = document.createElement('div');
            jobBlock.className = 'job-block';
            jobBlock.textContent = `Job ${job.jobId}`;
            jobBlock.style.left = `${(job.startTime / makespan) * timeScale}px`;
            jobBlock.style.width = `${(job.duration / makespan) * timeScale}px`;
            jobBlock.style.backgroundColor = colors[job.jobId % colors.length];
            
            // Add tooltip with details
            jobBlock.title = `Job ${job.jobId}: Start ${job.startTime}, End ${job.endTime}, Duration ${job.duration}`;
            
            timeline.appendChild(jobBlock);
        });
        
        machineRow.appendChild(machineLabel);
        machineRow.appendChild(timeline);
        ganttChart.appendChild(machineRow);
    });
}

// Update algorithm visualization with search details
function updateAlgorithmVisualization(vizData) {
    if (!vizData) return;
    
    // Update basic metrics
    document.getElementById("algorithm-name").textContent = vizData.algorithm_name;
    document.getElementById("search-iterations").textContent = vizData.search_iterations;
    document.getElementById("nodes-expanded").textContent = vizData.nodes_expanded;
    document.getElementById("execution-time").textContent = `${vizData.execution_time.toFixed(4)} seconds`;
    
    // Create or update the heuristic chart
    updateHeuristicChart(vizData);
    
    // Create or update the exploration chart
    updateExplorationChart(vizData);
    
    // Display solution path
    displaySolutionPath(vizData.solution_path);
}

// Update heuristic visualization chart
function updateHeuristicChart(vizData) {
    // Destroy existing chart
    if (heuristicChart) {
        heuristicChart.destroy();
    }
    
    // Get data points from the visualization data
    const heuristicValues = vizData.heuristic_values || [];
    
    // Check if we have data
    if (heuristicValues.length === 0) {
        document.getElementById("heuristic-chart").parentNode.innerHTML = 
            '<div class="chart-container"><p>No heuristic data available</p></div>';
        return;
    }
    
    // Format data for Chart.js
    const data = {
        labels: heuristicValues.map((_, i) => i + 1),
        datasets: []
    };
    
    // For A* algorithm, we have f, g, and h values
    if ('f_value' in heuristicValues[0]) {
        data.datasets = [
            {
                label: 'f(n) = g(n) + h(n)',
                data: heuristicValues.map(val => val.f_value),
                borderColor: '#EA4335',
                backgroundColor: 'rgba(234, 67, 53, 0.1)',
                borderWidth: 2,
                tension: 0.1
            },
            {
                label: 'g(n) - Path Cost',
                data: heuristicValues.map(val => val.g_value),
                borderColor: '#4285F4',
                backgroundColor: 'rgba(66, 133, 244, 0.1)',
                borderWidth: 2,
                tension: 0.1
            },
            {
                label: 'h(n) - Heuristic',
                data: heuristicValues.map(val => val.h_value),
                borderColor: '#FBBC05',
                backgroundColor: 'rgba(251, 188, 5, 0.1)',
                borderWidth: 2,
                tension: 0.1
            }
        ];
    } 
    // For GBFS, we just have the heuristic value
    else {
        data.datasets = [
            {
                label: 'h(n) - Heuristic Value',
                data: heuristicValues.map(val => val.heuristic),
                borderColor: '#4285F4',
                backgroundColor: 'rgba(66, 133, 244, 0.1)',
                borderWidth: 2,
                tension: 0.1
            }
        ];
    }
    
    // Get chart context
    const ctx = document.getElementById('heuristic-chart').getContext('2d');
    
    // Create the chart
    heuristicChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: getChartOptions('Heuristic Values During Search')
    });
}

// Update exploration chart
function updateExplorationChart(vizData) {
    // Destroy existing chart
    if (explorationChart) {
        explorationChart.destroy();
    }
    
    // Get exploration by level data
    const explorationByLevel = vizData.exploration_by_level || {};
    
    // Check if we have data
    if (Object.keys(explorationByLevel).length === 0) {
        document.getElementById("exploration-chart").parentNode.innerHTML = 
            '<div class="chart-container"><p>No exploration data available</p></div>';
        return;
    }
    
    // Format data for Chart.js
    const labels = Object.keys(explorationByLevel).sort((a, b) => parseInt(a) - parseInt(b));
    const values = labels.map(level => explorationByLevel[level]);
    
    // Get chart context
    const ctx = document.getElementById('exploration-chart').getContext('2d');
    
    // Create the chart
    explorationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => `Level ${l}`),
            datasets: [{
                label: 'Nodes Explored',
                data: values,
                backgroundColor: '#34A853',
                borderColor: '#28a745',
                borderWidth: 1
            }]
        },
        options: getChartOptions('Search Space Exploration by Level')
    });
}

// Display the solution path
function displaySolutionPath(solutionPath) {
    const solutionPathElement = document.getElementById('solution-path');
    
    if (!solutionPath || solutionPath.length === 0) {
        solutionPathElement.innerHTML = '<p>No solution path available.</p>';
        return;
    }
    
    let pathHtml = '<div class="solution-steps">';
    solutionPath.forEach((step, index) => {
        const [jobIdx, startTime, machineIdx] = step;
        pathHtml += `
            <div class="solution-step">
                <div class="step-number">${index + 1}</div>
                <div class="step-details">
                    <strong>Schedule Job ${jobIdx + 1}</strong> on 
                    Machine ${machineIdx + 1} at time ${startTime}
                </div>
            </div>
        `;
    });
    pathHtml += '</div>';
    
    solutionPathElement.innerHTML = pathHtml;
}

// Get chart options with proper theming
function getChartOptions(title) {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const isDark = currentTheme === 'dark';
    
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: title,
                color: isDark ? '#e0e0e0' : '#333333',
                font: {
                    size: 16
                }
            },
            legend: {
                position: 'top',
                labels: {
                    color: isDark ? '#b0b0b0' : '#666666'
                }
            },
            tooltip: {
                backgroundColor: isDark ? '#2c3440' : 'rgba(0, 0, 0, 0.7)'
            }
        },
        scales: {
            x: {
                ticks: {
                    color: isDark ? '#b0b0b0' : '#666666'
                },
                grid: {
                    color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                }
            },
            y: {
                ticks: {
                    color: isDark ? '#b0b0b0' : '#666666'
                },
                grid: {
                    color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                }
            }
        }
    };
}

// Update charts theme when theme changes
function updateChartsTheme() {
    if (heuristicChart) {
        const options = getChartOptions('Heuristic Values During Search');
        heuristicChart.options = options;
        heuristicChart.update();
    }
    
    if (explorationChart) {
        const options = getChartOptions('Search Space Exploration by Level');
        explorationChart.options = options;
        explorationChart.update();
    }
}

// Download results as JSON
function downloadResults() {
    if (!lastScheduleData) {
        alert('No scheduling data available to download');
        return;
    }
    
    const dataStr = JSON.stringify(lastScheduleData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'schedule_results.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}