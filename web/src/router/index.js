/**
 * Vue Router 路由設定
 * 包含公開頁面、管理者後台、教師後台、學生測驗平台
 * 使用 navigation guard 進行角色權限控制
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // === 公開頁面 ===
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/verify',
      name: 'verify-code',
      component: () => import('@/views/VerifyCodeView.vue'),
      meta: { guest: true },
    },

    // === 管理者後台 ===
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        { path: '', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'exams', name: 'admin-exams', component: () => import('@/views/admin/ExamSettingsView.vue') },
        { path: 'teachers', name: 'admin-teachers', component: () => import('@/views/admin/TeacherSettingsView.vue') },
        { path: 'students', name: 'admin-students', component: () => import('@/views/admin/StudentSettingsView.vue') },
      ],
    },

    // === 教師後台 ===
    {
      path: '/teacher',
      component: () => import('@/layouts/TeacherLayout.vue'),
      meta: { requiresAuth: true, role: 'teacher' },
      children: [
        { path: '', name: 'teacher-dashboard', component: () => import('@/views/teacher/DashboardView.vue') },
        { path: 'codes', name: 'teacher-codes', component: () => import('@/views/teacher/VerificationCodesView.vue') },
        { path: 'results', name: 'teacher-results', component: () => import('@/views/teacher/ExamResultsView.vue') },
        { path: 'scoring', name: 'teacher-scoring', component: () => import('@/views/teacher/ScoringView.vue') },
      ],
    },

    // === 學生測驗平台 ===
    {
      path: '/student',
      component: () => import('@/layouts/StudentLayout.vue'),
      children: [
        { path: 'exam/:sessionId', name: 'student-exam', component: () => import('@/views/student/ExamView.vue') },
        { path: 'result/:sessionId', name: 'student-result', component: () => import('@/views/student/ResultView.vue') },
      ],
    },

    // === 原有的公開評分流程（保留向下相容） ===
    {
      path: '/',
      name: 'exam-list',
      component: () => import('@/views/ExamListView.vue'),
    },
    {
      path: '/exam/:examId',
      name: 'exam-scoring',
      component: () => import('@/views/ExamScoringView.vue'),
    },
    {
      path: '/result',
      name: 'result-report',
      component: () => import('@/views/ResultReportView.vue'),
    },
  ],
})

// Navigation Guard
router.beforeEach((to) => {
  const { isLoggedIn, role } = useAuth()

  // 需要認證的頁面
  if (to.meta.requiresAuth) {
    if (!isLoggedIn.value) {
      return { name: 'login' }
    }
    // 角色檢查：admin 可存取 teacher 路由
    if (to.meta.role === 'admin' && role.value !== 'admin') {
      return { name: 'teacher-dashboard' }
    }
    if (to.meta.role === 'teacher' && role.value !== 'teacher' && role.value !== 'admin') {
      return { name: 'login' }
    }
  }

  // 已登入時不應再訪問登入頁
  if (to.meta.guest && isLoggedIn.value) {
    if (role.value === 'admin') return { name: 'admin-dashboard' }
    return { name: 'teacher-dashboard' }
  }
})

export default router
