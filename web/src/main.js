/**
 * 應用程式入口
 * - 掛載 Element Plus UI 框架（正體中文語系）
 * - 掛載 Vue Router 路由
 * - 載入全域樣式
 */
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhTw from 'element-plus/es/locale/lang/zh-tw'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
app.use(ElementPlus, { locale: zhTw })
app.use(router)
app.mount('#app')