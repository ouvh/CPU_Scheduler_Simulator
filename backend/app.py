from flask import Flask, request
from flask_socketio import SocketIO, emit
from process import Process
from schedulers import *
from simulation import CPUSimulation
from process_manager import ProcessManager
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulation state
simulation_thread = None
simulation = None
processes = []
running = False

def background_simulation(scheduler_type, time_quantum):
    global simulation, running
    try:
        # Create scheduler
        if scheduler_type == 'fcfs':
            scheduler = FCFSScheduler(processes)
        elif scheduler_type == 'sjf':
            scheduler = SJFScheduler(processes)
        elif scheduler_type == 'priority':
            scheduler = PriorityScheduler(processes)
        elif scheduler_type == 'rr':
            scheduler = RoundRobinScheduler(processes, time_quantum)
        elif scheduler_type == 'priority_rr':
            scheduler = PriorityRRScheduler(processes, time_quantum)
        else:
            raise ValueError("Invalid scheduler type")

        simulation = CPUSimulation(scheduler)
        running = True
        # made a change here to fix a bug 
        while running and (simulation.scheduler.processes or simulation.current_process or simulation.scheduler.ready_queue or simulation.blocked or (not simulation.scheduler.queue.empty() if  isinstance(simulation.scheduler, (RoundRobinScheduler, PriorityRRScheduler)) else False)):
            print(running)
            flag = simulation.step()
            
            # Emit update
            if isinstance(simulation.scheduler, (RoundRobinScheduler, PriorityRRScheduler)):
                socketio.emit('update', {
                    "time": simulation.scheduler.current_time - 1,
                    "running": simulation.current_process.pid if simulation.current_process else None,
                    "ready": [p.pid for temp,temp1,p in simulation.scheduler.queue.queue if p != simulation.current_process],
                    "blocked": [p.pid for p in simulation.blocked],
                    "metrics": simulation.calculate_final_metrics()
                })

            else:

                socketio.emit('update', {
                    "time": simulation.scheduler.current_time - 1,
                    "running": simulation.current_process.pid if simulation.current_process else None,
                    "ready": [p.pid for p in simulation.scheduler.ready_queue if p != simulation.current_process],
                    "blocked": [p.pid for p in simulation.blocked],
                    "metrics": simulation.calculate_final_metrics()
                })
            if flag:
                simulation.current_process = None
            
            time.sleep(0.5)  # Slow down simulation


        print("the simulation is done")
        # Final metrics
        if running:
            socketio.emit('complete', simulation.calculate_final_metrics())
            running = False

    except Exception as e:
        socketio.emit('error', {'message': str(e)})
        running = False

@socketio.on('connect')
def handle_connect():
    emit('status', {'processes': len(processes), 'running': running})

@socketio.on('add_process')
def handle_add_process(data):
    try:
        process = Process(
            pid=len(processes) + 1,
            arrival_time=int(data['arrival']),
            burst_time=int(data['burst']),
            priority=int(data['priority']),
            io_chance=int(data.get('io', 0))
        )
        processes.append(process)
        emit('process_added', process.__dict__)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('start')
def handle_start(data):
    global simulation_thread
    if not running:
        simulation_thread = threading.Thread(
            target=background_simulation,
            args=(data['scheduler'], data.get('quantum', 4))
        )
        simulation_thread.start()
        emit('started', {'scheduler': data['scheduler']})

@socketio.on('reset')
def handle_reset():
    
    global processes, running
    for process in processes:
        process.reset()
    #processes = []
    running = False
    print("reset done")
    emit('reset_done')

@socketio.on('load_file')
def handle_load_file(data):
    try:
        global processes
        processes = ProcessManager.load_from_file(data['filename'])
        emit('file_loaded', {'count': len(processes)})
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('remove_process')
def handle_remove_process(data):
    try:
        pid = int(data['pid'])
        # Find and remove the process
        global processes
        for i, process in enumerate(processes):
            if process.pid == pid:
                processes.pop(i)
                print("process removed")
                emit('process_removed', {'pid': pid})
                return
        print("process not found")

        # Process not found
        emit('error', {'message': f'Process with PID {pid} not found'})
    except Exception as e:
        print("something went wrong")

        emit('error', {'message': str(e)})


@socketio.on('compare_schedulers')
def handle_compare_schedulers():
    print("starting the comparaison")
    global processes
    
    if not processes:
        emit('error', {'message': 'No processes to simulate'})
        return
    
    # Save original process list to restore later
    original_processes = processes.copy()
    comparison_results = {}
    
    scheduler_configs = [
        {'name': 'First Come First Served (FCFS)', 'type': 'fcfs', 'quantum': None},
        {'name': 'Shortest Job First (SJF)', 'type': 'sjf', 'quantum': None},
        {'name': 'Priority', 'type': 'priority', 'quantum': None},
        {'name': 'Round Robin', 'type': 'rr', 'quantum': 4},
        {'name': 'Priority Round Robin', 'type': 'priority_rr', 'quantum': 4}
    ]
    
    # Run each scheduler algorithm
    for config in scheduler_configs:
        print("running")
        # Reset processes for each run
        process_copy = [Process(p.pid, p.arrival_time, p.burst_time, 
                               p.priority, p.io_chance) for p in original_processes]
        for process in process_copy:
            process.reset()
        # Create the appropriate scheduler
        if config['type'] == 'fcfs':
            scheduler = FCFSScheduler(process_copy)
        elif config['type'] == 'sjf':
            scheduler = SJFScheduler(process_copy)
        elif config['type'] == 'priority':
            scheduler = PriorityScheduler(process_copy)
        elif config['type'] == 'rr':
            scheduler = RoundRobinScheduler(process_copy, config['quantum'])
        elif config['type'] == 'priority_rr':
            scheduler = PriorityRRScheduler(process_copy, config['quantum'])
        
        # Run simulation
        simulation = CPUSimulation(scheduler)
        
        # Run until completion
        running = True
        # made a change here to fix a bug 
        while running and (simulation.scheduler.processes or simulation.current_process or simulation.scheduler.ready_queue or simulation.blocked or (not simulation.scheduler.queue.empty() if  isinstance(simulation.scheduler, (RoundRobinScheduler, PriorityRRScheduler)) else False)):
            print(running)
            flag = simulation.step()
            if flag:
                simulation.current_process = None
            
            #time.sleep(0.5)  # Slow down simulation
        
        # Get final metrics
        metrics = simulation.calculate_final_metrics()
        
        # Store results
        comparison_results[config['name']] = {
            'metrics': metrics,
            'history_length': len(simulation.history)
        }
        print("stoping")

    
    # Restore original processes
    processes = original_processes
    
    # Send results to client
    emit('comparison_results', comparison_results)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)