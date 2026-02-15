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
 * 若 AI 分析服務未啟用，自動 fallback 到 submitAssessment
 * @param {string} examId - 測驗卷 ID
 * @param {Object} payload - { student_name, exam_id, results: [{ question_id, score }] }
 * @returns {Promise<AssessmentResultOut>} 知識點分數 + 數學素養分數 + AI 分析（若可用）
 */
export async function submitAssessmentWithAnalysis(examId, payload) {
  try {
    return await api.post(`/exams/${examId}/assess-with-analysis`, payload)
  } catch (error) {
    // 若 AI 服務未啟用（503 Service Unavailable 或特定錯誤訊息），fallback 到基本評分
    if (error.response?.status === 503 ||
        error.response?.data?.detail?.includes('AI') ||
        error.response?.data?.detail?.includes('analysis service')) {
      console.warn('AI 分析服務未啟用，使用基本評分功能', error.response?.data?.detail)
      return await submitAssessment(examId, payload)
    }
    // 其他錯誤直接拋出
    throw error
  }
}