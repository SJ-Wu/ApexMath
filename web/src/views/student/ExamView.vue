<!--
  學生線上作答頁面
  - 依單元分頁展示題目
  - 支援選擇題、判斷題、填充題、應用題
  - 目前使用簡化模式：每題以 0~1 分數輸入評分（與教師手動評分相同）
-->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExamQuestions, submitAnswers } from '@/api/student'
import { useStudentSession } from '@/composables/useStudentSession'
import SectionScoring from '@/components/exam/SectionScoring.vue'

const route = useRoute()
const router = useRouter()
const { updateStatus } = useStudentSession()

const sessionId = route.params.sessionId
const loading = ref(true)
const examData = ref(null)
const scores = ref({})
const submitting = ref(false)

onMounted(async () => {
  try {
    examData.value = await getExamQuestions(sessionId)
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail === '此測驗已完成，請查看結果') {
      router.replace({ name: 'student-result', params: { sessionId } })
      return
    }
    ElMessage.error(detail || '載入測驗失敗')
  } finally {
    loading.value = false
  }
})

const template = computed(() => examData.value?.template || null)

function onScoreUpdate(questionId, value) {
  scores.value[questionId] = value
}

async function handleSubmit() {
  try {
    await ElMessageBox.confirm('確定要提交作答嗎？提交後無法修改。', '確認提交', {
      confirmButtonText: '確定提交',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return // 取消
  }

  const results = []
  if (template.value) {
    for (const section of template.value.sections) {
      for (const q of section.questions) {
        results.push({
          question_id: q.question_id,
          score: scores.value[q.question_id] ?? 0,
        })
      }
    }
  }

  submitting.value = true
  try {
    await submitAnswers(sessionId, { results })
    updateStatus('completed')
    ElMessage.success('作答已提交')
    router.push({ name: 'student-result', params: { sessionId } })
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失敗')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-loading="loading">
    <template v-if="template">
      <h2>{{ examData.name }}</h2>
      <p>學生：{{ examData.student_name }}</p>

      <SectionScoring
        v-for="section in template.sections"
        :key="section.section_id"
        :section="section"
        :scores="scores"
        @update:score="onScoreUpdate"
      />

      <div style="text-align: center; padding: 24px 0 40px">
        <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
          提交作答
        </el-button>
      </div>
    </template>
  </div>
</template>
