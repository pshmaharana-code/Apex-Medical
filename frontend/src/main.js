import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios' // Import axios globally

// --- THE GLOBAL INTERCEPTOR HACK ---
// This intercepts every network request before it leaves the browser
axios.interceptors.request.use((config) => {
  const backendUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
  
  if (config.url && config.url.includes('127.0.0.1:5000')) {
    // Dynamically swap the local IP with your live Render production URL
    config.url = config.url.replace('http://127.0.0.1:5000', backendUrl);
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

const app = createApp(App)

app.use(createPinia()) 
app.use(router)        

app.mount('#app')