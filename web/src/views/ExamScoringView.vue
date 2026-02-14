<!--
  老師評分頁
  - 根據路由參數 examId 載入測驗卷模板（含所有單元與題目）
  - 老師輸入學生姓名，並為每道題目輸入得分率（0~1）
  - 提交後呼叫後端 assess API，取得評估結果並導航至結果報告頁
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExamDetail, submitAssessmentWithAnalysis } from '@/api/exam'
import SectionScoring from '@/components/exam/SectionScoring.vue'

const route = useRoute()
const router = useRouter()

const examId = route.params.examId         // 從路由取得測驗卷 ID
const exam = ref(null)                     // 測驗卷模板資料
const studentName = ref('')                // 學生姓名
const scores = ref({})                     // 各題得分率，key: question_id, value: 0~1
const loading = ref(false)                 // 載入測驗資料中
const submitting = ref(false)              // 提交評分中

/** 載入測驗卷模板 */
onMounted(async () => {
  loading.value = true
  try {
    exam.value = await getExamDetail(examId)
  } catch (e) {
    ElMessage.error('無法載入測驗資料')
  } finally {
    loading.value = false
  }
})

/** 接收子元件 SectionScoring 的分數更新事件 */
function onScoreUpdate(questionId, value) {
  scores.value[questionId] = value
}

/** 組裝評分資料並提交至後端 */
async function handleSubmit() {
  if (!studentName.value.trim()) {
    ElMessage.warning('請輸入學生姓名')
    return
  }

  // 將所有題目的得分率組裝成 results 陣列，未填寫的題目預設為 0
  const results = []
  for (const section of exam.value.sections) {
    for (const q of section.questions) {
      results.push({
        question_id: q.question_id,
        score: scores.value[q.question_id] ?? 0,
      })
    }
  }

  const payload = {
    student_name: studentName.value.trim(),
    exam_id: examId,
    results,
  }

  submitting.value = true
  try {
    const result = await submitAssessmentWithAnalysis(examId, payload)
    // 將評估結果透過 router state 傳遞至結果報告頁
    router.push({ name: 'result-report', state: { assessmentResult: JSON.stringify(result) } })
  } catch (e) {
    const status = e.response?.status
    if (status === 503) {
      ElMessage.error('AI 分析服務尚未啟用，請聯繫管理員設定 LLM 服務')
    } else if (status === 502) {
      ElMessage.error('AI 分析呼叫失敗，請稍後再試')
    } else {
      ElMessage.error('提交失敗，請稍後再試')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="scoring-page" v-loading="loading">
    <div v-if="exam" class="scoring-content">
      <!-- 頁首：返回按鈕 + 測驗卷名稱 -->
      <div class="page-header">
        <el-button @click="router.push('/')" plain>← 返回列表</el-button>
        <h1>{{ exam.name }}</h1>
      </div>

      <!-- 學生姓名輸入 -->
      <el-form label-position="top" class="student-form">
        <el-form-item label="學生姓名">
          <el-input v-model="studentName" placeholder="請輸入學生姓名" style="max-width: 300px" />
        </el-form-item>
      </el-form>

      <!-- 各單元評分區塊 -->
      <SectionScoring
        v-for="section in exam.sections"
        :key="section.section_id"
        :section="section"
        :scores="scores"
        @update:score="onScoreUpdate"
      />

      <!-- 提交按鈕 -->
      <div class="submit-area">
        <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
          提交評分
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scoring-page {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 12px 0 0;
}

.student-form {
  margin-bottom: 24px;
}

.submit-area {
  text-align: center;
  padding: 24px 0 40px;
}
</style>