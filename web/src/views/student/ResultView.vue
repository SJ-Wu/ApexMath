<!--
  學生結果報告頁面
  - 顯示知識點長條圖 + 數學素養雷達圖 + AI 分析
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExamResult } from '@/api/student'
import KnowledgeBarChart from '@/components/charts/KnowledgeBarChart.vue'
import LiteracyRadarChart from '@/components/charts/LiteracyRadarChart.vue'

const route = useRoute()
const sessionId = route.params.sessionId
const loading = ref(true)
const result = ref(null)

onMounted(async () => {
  try {
    result.value = await getExamResult(sessionId)
  } catch {
    ElMessage.error('載入結果失敗')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-loading="loading">
    <template v-if="result?.assessment">
      <h2>測驗結果</h2>
      <p>學生：{{ result.student_name }} ｜ 試卷：{{ result.exam_id }}</p>

      <div class="chart-row">
        <div class="chart-item">
          <h3>知識點能力</h3>
          <KnowledgeBarChart :scores="result.assessment.knowledge_point_scores" />
        </div>
        <div class="chart-item">
          <h3>數學素養能力</h3>
          <LiteracyRadarChart :scores="result.assessment.math_literacy_scores" />
        </div>
      </div>

      <template v-if="result.ai_analysis">
        <el-card shadow="never" style="margin-top: 24px">
          <h3>弱點分析</h3>
          <p style="white-space: pre-line">{{ result.ai_analysis.weakness_analysis }}</p>
        </el-card>
        <el-card shadow="never" style="margin-top: 12px">
          <h3>強化建議</h3>
          <p style="white-space: pre-line">{{ result.ai_analysis.enhancement_suggestions }}</p>
        </el-card>
      </template>
    </template>

    <template v-else-if="result && result.status === 'in_progress'">
      <el-empty description="測驗尚未完成" />
    </template>

    <el-empty v-else-if="!loading" description="找不到測驗結果" />
  </div>
</template>

<style scoped>
.chart-row {
  display: flex;
  gap: 24px;
  margin-top: 16px;
}

.chart-item {
  flex: 1;
}

@media (max-width: 768px) {
  .chart-row {
    flex-direction: column;
  }
}
</style>
