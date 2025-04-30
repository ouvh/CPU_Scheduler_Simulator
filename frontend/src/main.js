import { createApp } from 'vue'
import { createPinia } from 'pinia'
import io from 'socket.io-client'
import App from './App.vue'

// Import Tailwind CSS
import './assets/css/main.css'

// Set up Socket.IO
const socket = io('http://localhost:5000')

// Create Vue app
const app = createApp(App)

// Provide socket to components
app.provide('socket', socket)

// Use Pinia store
app.use(createPinia())

// Mount the app
app.mount('#app')

// Log connection status
socket.on('connect', () => {
  console.log('Connected to server')
})

socket.on('disconnect', () => {
  console.log('Disconnected from server')
})