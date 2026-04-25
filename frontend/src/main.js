import { createApp } from 'vue'
import './style.css'
import './styles/global.css'
import App from './App.vue'
import router from "./router/index.js";
import { connectWS } from './api/ws'

createApp(App).use(router).mount('#app' )

connectWS()