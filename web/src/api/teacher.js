/**
 * 教師後台 API
 */
import api from './index'

/** 取得教師可用的試卷列表 */
export function getTeacherExams() {
  return api.get('/teacher/exams')
}

/** 產生驗證碼 */
export function generateCodes(payload) {
  return api.post('/teacher/codes/generate', payload)
}

/** 取得驗證碼列表 */
export function getCodeList(params) {
  return api.get('/teacher/codes', { params })
}

/** 取得學生成績列表 */
export function getExamResults(params) {
  return api.get('/teacher/results', { params })
}

/** 取得個別學生報告 */
export function getSessionReport(sessionId) {
  return api.get(`/teacher/results/${sessionId}`)
}

/** 教師手動提交評分 */
export function submitTeacherScoring(payload) {
  return api.post('/teacher/scoring', payload)
}
