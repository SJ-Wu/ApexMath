/**
 * Axios 共用實例
 * - 本機開發：baseURL = /api（透過 Vite proxy 轉發至 FastAPI）
 * - Render 部署：VITE_API_BASE_URL = API 服務外部 URL，自動附加 /api
 * - response 攔截器自動解包 response.data，讓呼叫端直接取得 JSON 資料
 */
import axios from 'axios'

// Render 的 RENDER_EXTERNAL_URL 格式為 https://xxx.onrender.com（不含 /api）
const externalUrl = import.meta.env.VITE_API_BASE_URL
const baseURL = externalUrl ? `${externalUrl.replace(/\/+$/, '')}/api` : '/api'

const api = axios.create({ baseURL })



// 回應攔截器：成功時直接回傳 data；失敗時拋出錯誤供呼叫端 catch
api.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error),
)

export default api