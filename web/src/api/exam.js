/**
 * 測驗相關 API
 * 對應後端 FastAPI 三支端點：
 *   GET  /api/exams              — 取得所有測驗卷 ID 列表
 *   GET  /api/exams/{examId}     — 取得單一測驗卷完整模板（含各單元題目）
 *   POST /api/exams/{examId}/assess — 提交學生評分，回傳知識點分數 + 數學素養分數
 */
import api from './index'

/** 取得測驗卷列表，回傳 { exam_ids: string[] } */
export function getExamList() {
  return api.get('/exams')
}

/** 取得測驗卷詳情（含 sections / questions），回傳 ExamTemplate */
export function getExamDetail(examId) {
  return api.get(`/exams/${examId}`)
}

/**
 * 提交評分結果
 * @param {string} examId - 測驗卷 ID
 * @param {Object} payload - { student_name, exam_id, results: [{ question_id, score }] }
 * @returns {Promise<AssessmentResultOut>} 知識點分數 + 數學素養分數
 */
export function submitAssessment(examId, payload) {
  return api.post(`/exams/${examId}/assess`, payload)
}

/**
 * 提交評分結果並取得 AI 分析
 * @param {string} examId - 測驗卷 ID
 * @param {Object} payload - { student_name, exam_id, results: [{ question_id, score }] }
 * @returns {Promise<AssessmentResultOut>} 知識點分數 + 數學素養分數 + AI 分析
 */
export function submitAssessmentWithAnalysis(examId, payload) {
  return api.post(`/exams/${examId}/assess-with-analysis`, payload)
}