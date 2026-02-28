/**
 * 學生 Session 管理
 * 處理驗證碼登入後的 session token 與狀態
 */
import { ref, computed } from 'vue'
import api from '@/api/index'

const STUDENT_TOKEN_KEY = 'apexmath_student_token'
const STUDENT_SESSION_KEY = 'apexmath_student_session'

const studentToken = ref(localStorage.getItem(STUDENT_TOKEN_KEY) || '')
const sessionInfo = ref(JSON.parse(localStorage.getItem(STUDENT_SESSION_KEY) || 'null'))

export function useStudentSession() {
  const hasSession = computed(() => !!studentToken.value)
  const examId = computed(() => sessionInfo.value?.exam_id || '')
  const sessionId = computed(() => sessionInfo.value?.session_id || '')
  const sessionStatus = computed(() => sessionInfo.value?.status || '')

  /** 驗證碼登入 */
  async function verifyCode(code, studentName) {
    const data = await api.post('/auth/verify-code', { code, student_name: studentName })
    studentToken.value = data.access_token
    sessionInfo.value = {
      exam_id: data.exam_id,
      session_id: data.session_id,
      status: data.status,
    }
    localStorage.setItem(STUDENT_TOKEN_KEY, data.access_token)
    localStorage.setItem(STUDENT_SESSION_KEY, JSON.stringify(sessionInfo.value))
    return data
  }

  /** 取得 student token */
  function getStudentToken() {
    return studentToken.value
  }

  /** 清除 session */
  function clearSession() {
    studentToken.value = ''
    sessionInfo.value = null
    localStorage.removeItem(STUDENT_TOKEN_KEY)
    localStorage.removeItem(STUDENT_SESSION_KEY)
  }

  /** 更新 session 狀態 */
  function updateStatus(status) {
    if (sessionInfo.value) {
      sessionInfo.value = { ...sessionInfo.value, status }
      localStorage.setItem(STUDENT_SESSION_KEY, JSON.stringify(sessionInfo.value))
    }
  }

  return {
    studentToken,
    sessionInfo,
    hasSession,
    examId,
    sessionId,
    sessionStatus,
    verifyCode,
    getStudentToken,
    clearSession,
    updateStatus,
  }
}
