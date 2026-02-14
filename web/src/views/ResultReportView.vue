<!--
  結果報告頁
  - 從 history.state 讀取評估結果（由評分頁透過 router state 傳入）
  - 顯示學生基本資訊（姓名、測驗卷）
  - 知識點能力長條圖（10 個類別，0~5 分）
  - 數學素養雷達圖（4 個維度，0~5 分）
  - AI 分析區塊（預留，功能開發中）
  - 支援瀏覽器列印
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import KnowledgeBarChart from '@/components/charts/KnowledgeBarChart.vue'
import LiteracyRadarChart from '@/components/charts/LiteracyRadarChart.vue'

const router = useRouter()
const result = ref(null)              // 完整評估結果（AssessmentResultOut）
const knowledgeScores = ref([])       // 知識點分數陣列（長度 10）
const literacyScores = ref([])        // 數學素養分數陣列（長度 4）
const aiAnalysis = ref(null)          // AI 分析結果

onMounted(() => {
  // 從 router state 取得評估結果 JSON 字串
  const raw = history.state.assessmentResult
  if (!raw) {
    // 若無資料（例如直接造訪此頁），導回首頁
    router.replace('/')
    return
  }
  result.value = JSON.parse(raw)
  knowledgeScores.value = result.value.knowledge_point_scores.map((s) => s.score)
  literacyScores.value = result.value.math_literacy_scores.map((s) => s.score)
  aiAnalysis.value = result.value.ai_analysis || null
})

/** 觸發瀏覽器列印對話框 */
function handlePrint() {
  window.print()
}
</script>

<template>
  <div v-if="result" class="report-page">
    <!-- 操作按鈕列（列印時隱藏） -->
    <div class="no-print page-actions">
      <el-button @click="router.push('/')" plain>← 返回列表</el-button>
      <el-button type="primary" @click="handlePrint">列印報告</el-button>
    </div>

    <h1 class="report-title">數學能力檢測報告</h1>

    <!-- 學生基本資訊 -->
    <el-descriptions title="學生資訊" :column="2" border>
      <el-descriptions-item label="學生姓名">{{ result.student_name }}</el-descriptions-item>
      <el-descriptions-item label="測驗卷">{{ result.exam_id }}</el-descriptions-item>
    </el-descriptions>

    <!-- 知識點能力長條圖 -->
    <section class="chart-section">
      <h2>各項知識點能力</h2>
      <KnowledgeBarChart :scores="knowledgeScores" />
    </section>

    <!-- 數學素養雷達圖 -->
    <section class="chart-section">
      <h2>數學素養能力雷達圖</h2>
      <LiteracyRadarChart :scores="literacyScores" />
    </section>

    <!-- AI 分析與建議 -->
    <section class="chart-section">
      <h2>分析與建議</h2>
      <template v-if="aiAnalysis">
        <el-card shadow="never" class="ai-card">
          <h3>弱點分析</h3>
          <p class="ai-text">{{ aiAnalysis.weakness_analysis }}</p>
        </el-card>
        <el-card shadow="never" class="ai-card">
          <h3>強化建議</h3>
          <p class="ai-text">{{ aiAnalysis.enhancement_suggestions }}</p>
        </el-card>
      </template>
      <el-card v-else shadow="never">
        <el-empty description="無 AI 分析資料" :image-size="80" />
      </el-card>
    </section>
  </div>
</template>

<style scoped>
.report-page {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 20px 40px;
}

.page-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.report-title {
  text-align: center;
  margin-bottom: 24px;
}

.chart-section {
  margin-top: 32px;
}

.chart-section h2 {
  margin-bottom: 12px;
}

.ai-card {
  margin-bottom: 16px;
}

.ai-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.ai-text {
  white-space: pre-wrap;
  margin: 0;
  line-height: 1.6;
}

/* 列印時隱藏操作按鈕 */
@media print {
  .no-print {
    display: none;
  }
}
</style>