/**
 * 管理者後台 API
 */
import api from './index'

// === 教師管理 ===
export function getTeachers() {
  return api.get('/admin/teachers')
}

export function createTeacher(payload) {
  return api.post('/admin/teachers', payload)
}

export function updateTeacher(teacherId, payload) {
  return api.put(`/admin/teachers/${teacherId}`, payload)
}

export function deleteTeacher(teacherId) {
  return api.delete(`/admin/teachers/${teacherId}`)
}

// === 試卷管理 ===
export function getExamTemplates() {
  return api.get('/admin/exams')
}

export function assignExamToTeacher(payload) {
  return api.post('/admin/exams/assign', payload)
}

// === 學生紀錄 ===
export function getAllSessions(params) {
  return api.get('/admin/sessions', { params })
}

// === 統計 ===
export function getDashboardStats() {
  return api.get('/admin/stats')
}
