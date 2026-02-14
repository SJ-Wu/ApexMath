/**
 * Vue Router 路由設定
 * 三條路由對應三個頁面：
 *   /                 → 測驗卷列表頁
 *   /exam/:examId     → 老師評分頁
 *   /result           → 結果報告頁（含圖表）
 *
 * 所有頁面元件皆使用動態 import 實現懶載入（lazy loading）
 */
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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

export default router