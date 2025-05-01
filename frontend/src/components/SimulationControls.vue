<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\components\SimulationControls.vue -->
<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4">Simulation Controls</h2>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Scheduler Type</label>
        <select 
          v-model="schedulerType" 
          :disabled="disabled || store.isRunning"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="fcfs">First Come First Served (FCFS)</option>
          <option value="sjf">Shortest Job First (SJF)</option>
          <option value="priority">Priority</option>
          <option value="rr">Round Robin (RR)</option>
          <option value="priority_rr">Priority Round Robin</option>
        </select>
      </div>
      <div v-if="schedulerType === 'rr' || schedulerType === 'priority_rr'">
        <label class="block text-sm font-medium text-gray-700">Time Quantum</label>
        <input 
          v-model.number="timeQuantum" 
          type="number" 
          min="1" 
          :disabled="disabled || store.isRunning"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
      </div>
    </div>
    
    <div class="mt-4 flex gap-4">
      <button 
        @click="startSimulation" 
        :disabled="disabled || store.isRunning"
        class="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-green-300"
      >
        Start
      </button>
      <button 
        @click="resetSimulation" 
        :disabled="disabled && !store.history.length"
        class="flex-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-red-300"
      >
        Reset
      </button>
    </div>
    
    <div class="mt-4 border-t pt-4">
      <h3 class="text-lg font-medium mb-2">Process Management</h3>
      <div class="flex gap-4">
        <button 
          @click="saveProcesses" 
          :disabled="disabled || store.processes.length === 0"
          class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
        >
          Save Processes
        </button>
        <button 
          @click="loadProcessesForm" 
          :disabled="disabled || store.isRunning"
          class="flex-1 bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 disabled:bg-yellow-300"
        >
          Load Processes
        </button>
      </div>
      
      <div v-if="store.finalMetrics" class="mt-4 bg-blue-50 p-3 rounded">
        <h4 class="font-medium text-blue-800 mb-2">Final Simulation Results</h4>
        <p class="text-sm text-blue-700">CPU Utilization: {{ (store.finalMetrics.cpu_utilization).toFixed(2) }}%</p>
        <p class="text-sm text-blue-700">Avg Turnaround Time: {{ (store.finalMetrics.avg_turnaround).toFixed(2) }}</p>
        <p class="text-sm text-blue-700">Avg Waiting Time: {{ (store.finalMetrics.avg_waiting).toFixed(2) }}</p>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, inject, defineProps } from 'vue'
import { useSimulationStore } from '@/stores/simulation'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const socket = inject('socket')
const store = useSimulationStore()
const schedulerType = ref('fcfs')
const timeQuantum = ref(4)

const startSimulation = () => {
  socket.emit('start', {
    scheduler: schedulerType.value,
    quantum: timeQuantum.value
  })
}

const resetSimulation = () => {
  // If simulation is running, stop it first
  if (store.isRunning) {
    socket.emit('reset')
  } else {
    // If simulation is not running, just reset the UI
    socket.emit('reset')
    store.reset()
  }

  // fixing bug here
}

const saveProcesses = () => {
  // Create a JSON file to download
  const processes = JSON.stringify(store.processes, null, 2)
  const blob = new Blob([processes], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'processes.json'
  link.click()
  URL.revokeObjectURL(link.href)
}

const loadProcessesForm = () => {
  // Create an input element to load a file
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json,.csv'
  input.onchange = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = e.target.result
          // Try to parse as JSON
          const processes = JSON.parse(content)
          
          // Clear existing processes
          socket.emit('reset')
          
          // Add each process
          processes.forEach(process => {
            socket.emit('add_process', {
              arrival: process.arrival_time,
              burst: process.burst_time,
              priority: process.priority,
              io: process.io_chance
            })
          })
        } catch (err) {
          console.error('Error parsing file:', err)
          alert('Error loading processes file. Please check the format.')
        }
      }
      reader.readAsText(file)
    }
  }
  input.click()
}
</script>