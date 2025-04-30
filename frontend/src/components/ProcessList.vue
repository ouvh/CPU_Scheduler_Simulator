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
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="process in store.processes" :key="process.pid" class="hover:bg-gray-50">
              <td class="px-4 py-2 whitespace-nowrap">{{ process.pid }}</td>
              <td class="px-4 py-2 whitespace-nowrap">{{ process.arrival_time }}</td>
              <td class="px-4 py-2 whitespace-nowrap">{{ process.burst_time }}</td>
              <td class="px-4 py-2 whitespace-nowrap">{{ process.priority }}</td>
              <td class="px-4 py-2 whitespace-nowrap">{{ process.io_chance }}%</td>
            </tr>
            <tr v-if="store.processes.length === 0">
              <td colspan="5" class="px-4 py-4 text-center text-sm text-gray-500">
                No processes created yet
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useSimulationStore } from '@/stores/simulation'
  
  const store = useSimulationStore()
  </script>