<template>
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-bold mb-4">Process Creation</h2>
      <form @submit.prevent="createProcess" class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Arrival Time</label>
          <input 
            v-model.number="newProcess.arrival" 
            type="number" 
            min="0"
            required 
            :disabled="disabled"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Burst Time</label>
          <input 
            v-model.number="newProcess.burst" 
            type="number" 
            min="1"
            required 
            :disabled="disabled"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Priority</label>
          <input 
            v-model.number="newProcess.priority" 
            type="number" 
            min="1"
            required 
            :disabled="disabled"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">I/O Chance (%)</label>
          <input 
            v-model.number="newProcess.io" 
            type="number" 
            min="0" 
            max="100" 
            :disabled="disabled"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
        </div>
        <div class="col-span-2">
          <button 
            type="submit" 
            :disabled="disabled"
            class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300">
            Add Process
          </button>
        </div>
      </form>
      <div class="mt-4 grid grid-cols-2 gap-4">
        <button 
          @click="generateRandom" 
          :disabled="disabled"
          class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-green-300">
          Generate Random Process
        </button>
        <button 
          @click="generateBatch" 
          :disabled="disabled"
          class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:bg-purple-300">
          Generate Batch (5)
        </button>
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
  const newProcess = ref({
    arrival: 0,
    burst: 1,
    priority: 1,
    io: 10
  })
  
  const createProcess = () => {
    socket.emit('add_process', { ...newProcess.value })
  }
  
  const generateRandom = () => {
    newProcess.value = {
      arrival: Math.floor(Math.random() * 10),
      burst: Math.floor(Math.random() * 10 + 1),
      priority: Math.floor(Math.random() * 5 + 1),
      io: Math.floor(Math.random() * 30)
    }
    createProcess()
  }
  
  const generateBatch = () => {
    for (let i = 0; i < 5; i++) {
      generateRandom()
    }
  }
  </script>