<template>
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-bold mb-4">Simulation Controls</h2>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Scheduler Type</label>
          <select 
            v-model="schedulerType" 
            :disabled="disabled || store.isRunning"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
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
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
        </div>
      </div>
      <div class="mt-4 flex gap-4">
        <button 
          @click="startSimulation" 
          :disabled="disabled || store.isRunning"
          class="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-green-300">
          Start
        </button>
        <button 
          @click="stopSimulation" 
          :disabled="disabled || !store.isRunning"
          class="flex-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-red-300">
          Reset
        </button>
      </div>
      
      <div class="mt-4 border-t pt-4">
        <h3 class="text-lg font-medium mb-2">Process Management</h3>
        <div class="flex gap-4">
          <button 
            @click="saveProcesses" 
            :disabled="disabled || store.processes.length === 0"
            class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300">
            Save Processes
          </button>
          <button 
            @click="loadProcessesForm" 
            :disabled="disabled || store.isRunning"
            class="flex-1 bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 disabled:bg-yellow-300">
            Load Processes
          </button>
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
  const fileInput = ref(null)
  
  const startSimulation = () => {
    socket.emit('start', {
      scheduler: schedulerType.value,
      quantum: timeQuantum.value
    })
  }
  
  const stopSimulation = () => {
    socket.emit('reset')
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
        socket.emit('load_file', { filename: file.name })
      }
    }
    input.click()
  }
  </script>