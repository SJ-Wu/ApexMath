<!--
  教師手動評分頁面
  - 輸入驗證碼、學生姓名
  - 載入試卷並逐題評分（複用 SectionScoring 元件）
  - 提交後顯示結果
-->
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTeacherExams, submitTeacherScoring } from '@/api/teacher'
import { getExamDetail } from '@/api/exam'
import SectionScoring from '@/components/exam/SectionScoring.vue'
import KnowledgeBarChart from '@/components/charts/KnowledgeBarChart.vue'
import LiteracyRadarChart from '@/components/charts/LiteracyRadarChart.vue'

const exams = ref([])
const verificationCode = ref('')
const studentName = ref('')
const selectedExamId = ref('')
const exam = ref(null)
const scores = ref({})
const submitting = ref(false)
const result = ref(null)

onMounted(async () => {
  try {
    exams.value = await getTeacherExams()
    if (exams.value.length > 0) selectedExamId.value = exams.value[0].exam_id
  } catch {
    ElMessage.error('載入試卷列表失敗')
  }
})

async function loadExam() {
  if (!selectedExamId.value) return
  try {
    exam.value = await getExamDetail(selectedExamId.value)
    scores.value = {}
    result.value = null
  } catch {
    ElMessage.error('載入試卷失敗')
  }
}

function onScoreUpdate(questionId, value) {
  scores.value[questionId] = value
}

async function handleSubmit() {
  if (!verificationCode.value.trim()) {
    ElMessage.warning('請輸入驗證碼')
    return
  }
  if (!studentName.value.trim()) {
    ElMessage.warning('請輸入學生姓名')
    return
  }

  const results = []
  for (const section of exam.value.sections) {
    for (const q of section.questions) {
      results.push({
        question_id: q.question_id,
        score: scores.value[q.question_id] ?? 0,
      })
    }
  }

  submitting.value = true
  try {
    result.value = await submitTeacherScoring({
      verification_code: verificationCode.value.trim(),
      student_name: studentName.value.trim(),
      exam_id: selectedExamId.value,
      results,
    })
    ElMessage.success('評分提交成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失敗')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <h2>手動評分</h2>

    <!-- 基本資訊 -->
    <el-form label-position="top" style="max-width: 600px; margin-bottom: 24px">
      <el-form-item label="驗證碼">
        <el-input v-model="verificationCode" placeholder="輸入學生驗證碼" />
      </el-form-item>
      <el-form-item label="學生姓名">
        <el-input v-model="studentName" placeholder="輸入學生姓名" />
      </el-form-item>
      <el-form-item label="試卷">
        <el-select v-model="selectedExamId" @change="loadExam" placeholder="選擇試卷">
          <el-option v-for="e in exams" :key="e.exam_id" :label="e.name" :value="e.exam_id" />
        </el-select>
        <el-button @click="loadExam" style="margin-left: 12px">載入試卷</el-button>
      </el-form-item>
    </el-form>

    <!-- 評分區塊 -->
    <template v-if="exam">
      <SectionScoring
        v-for="section in exam.sections"
        :key="section.section_id"
        :section="section"
        :scores="scores"
        @update:score="onScoreUpdate"
      />

      <div style="text-align: center; padding: 24px 0">
        <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
          提交評分
        </el-button>
      </div>
    </template>

    <!-- 結果顯示 -->
    <template v-if="result?.assessment">
      <el-divider>評估結果</el-divider>
      <div class="chart-row">
        <div class="chart-item">
          <h4>知識點能力</h4>
          <KnowledgeBarChart :scores="result.assessment.knowledge_point_scores" />
        </div>
        <div class="chart-item">
          <h4>數學素養能力</h4>
          <LiteracyRadarChart :scores="result.assessment.math_literacy_scores" />
        </div>
      </div>

      <template v-if="result.ai_analysis">
        <el-card shadow="never" style="margin-top: 16px">
          <h4>弱點分析</h4>
          <p style="white-space: pre-line">{{ result.ai_analysis.weakness_analysis }}</p>
        </el-card>
        <el-card shadow="never" style="margin-top: 12px">
          <h4>強化建議</h4>
          <p style="white-space: pre-line">{{ result.ai_analysis.enhancement_suggestions }}</p>
        </el-card>
      </template>
    </template>
  </div>
</template>

<style scoped>
.chart-row {
  display: flex;
  gap: 24px;
}

.chart-item {
  flex: 1;
}
</style>
