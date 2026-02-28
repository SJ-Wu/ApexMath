/**
 * 學生測驗 API
 */
import api from './index'

/** 取得試卷題目 */
export function getExamQuestions(sessionId) {
  return api.get(`/student/exam/${sessionId}`)
}

/** 提交作答 */
export function submitAnswers(sessionId, payload) {
  return api.post(`/student/exam/${sessionId}/submit`, payload)
}

/** 取得測驗結果 */
export function getExamResult(sessionId) {
  return api.get(`/student/result/${sessionId}`)
}
