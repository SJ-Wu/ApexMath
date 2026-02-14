/**
 * Axios 共用實例
 * - baseURL 預設為 /api，透過 Vite proxy 轉發至後端 FastAPI (localhost:8000)
 * - Render 部署時透過環境變數 VITE_API_BASE_URL 指定 API 完整位址
 * - response 攔截器自動解包 response.data，讓呼叫端直接取得 JSON 資料
 */
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})


// 回應攔截器：成功時直接回傳 data；失敗時拋出錯誤供呼叫端 catch
api.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error),
)

export default api