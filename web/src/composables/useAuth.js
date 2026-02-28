/**
 * 認證狀態管理
 * 處理 JWT token 儲存、角色判斷、登入/登出邏輯
 */
import { ref, computed } from 'vue'
import api from '@/api/index'

const TOKEN_KEY = 'apexmath_token'
const USER_KEY = 'apexmath_user'

const token = ref(localStorage.getItem(TOKEN_KEY) || '')
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

export function useAuth() {
  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role || '')
  const displayName = computed(() => user.value?.display_name || '')
  const isAdmin = computed(() => role.value === 'admin')
  const isTeacher = computed(() => role.value === 'teacher')

  /** 帳密登入（Admin / Teacher） */
  async function login(username, password) {
    const data = await api.post('/auth/login', { username, password })
    token.value = data.access_token
    user.value = { role: data.role, display_name: data.display_name }
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    return data
  }

  /** 登出 */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  /** 取得當前 token */
  function getToken() {
    return token.value
  }

  return {
    token,
    user,
    isLoggedIn,
    role,
    displayName,
    isAdmin,
    isTeacher,
    login,
    logout,
    getToken,
  }
}
