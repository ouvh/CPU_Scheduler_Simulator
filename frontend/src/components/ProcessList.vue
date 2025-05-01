<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\components\ProcessList.vue -->
<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">Process List</h2>
      <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
        Total: {{ store.processes.length }}
      </span>
    </div>
    
    <div class="overflow-x-auto">
      <table class="min-w-full bg-white rounded-lg overflow-hidden">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PID</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Arrival</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Burst</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">I/O</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="process in store.processes" :key="process.pid" class="hover:bg-gray-50">
            <td class="px-4 py-2 whitespace-nowrap">{{ process.pid }}</td>
            <td class="px-4 py-2 whitespace-nowrap">{{ process.arrival_time }}</td>
            <td class="px-4 py-2 whitespace-nowrap">{{ process.burst_time }}</td>
            <td class="px-4 py-2 whitespace-nowrap">{{ process.priority }}</td>
            <td class="px-4 py-2 whitespace-nowrap">{{ process.io_chance }}%</td>
            <td class="px-4 py-2 whitespace-nowrap">
              <button 
                @click="removeProcess(process.pid)" 
                :disabled="store.isRunning"
                class="text-red-600 hover:text-red-800 disabled:text-gray-400"
                title="Remove process"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="store.processes.length === 0">
            <td colspan="6" class="px-4 py-4 text-center text-sm text-gray-500">
              No processes created yet
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'
import { useSimulationStore } from '@/stores/simulation'

const store = useSimulationStore()
const socket = inject('socket')

// Function to remove a process
const removeProcess = (pid) => {
  socket.emit('remove_process', { pid })
}
</script>