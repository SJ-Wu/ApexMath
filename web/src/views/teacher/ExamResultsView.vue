<!--
  學生成績列表頁
  - 顯示所有學生的測驗結果
  - 點擊可查看詳細報告（圖表 + AI 分析）
-->
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getExamResults, getSessionReport } from '@/api/teacher'
import KnowledgeBarChart from '@/components/charts/KnowledgeBarChart.vue'
import LiteracyRadarChart from '@/components/charts/LiteracyRadarChart.vue'

const sessions = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    sessions.value = await getExamResults()
  } catch {
    ElMessage.error('載入成績失敗')
  } finally {
    loading.value = false
  }
})

async function showDetail(sessionId) {
  try {
    detail.value = await getSessionReport(sessionId)
    detailVisible.value = true
  } catch {
    ElMessage.error('載入報告失敗')
  }
}

function statusLabel(status) {
  if (status === 'in_progress') return '測驗中'
  return '已完成'
}
</script>

<template>
  <div>
    <h2>學生成績</h2>

    <el-table :data="sessions" v-loading="loading" stripe @row-click="(row) => showDetail(row.session_id)">
      <el-table-column prop="student_name" label="學生姓名" width="120" />
      <el-table-column prop="exam_id" label="試卷" width="160" />
      <el-table-column prop="code" label="驗證碼" width="150" />
      <el-table-column label="狀態" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="開始時間" />
    </el-table>

    <!-- 詳細報告對話框 -->
    <el-dialog v-model="detailVisible" title="學生報告" width="800px" destroy-on-close>
      <template v-if="detail?.assessment">
        <h3>{{ detail.student_name }} — {{ detail.exam_id }}</h3>

        <div class="chart-row">
          <div class="chart-item">
            <h4>知識點能力</h4>
            <KnowledgeBarChart :scores="detail.assessment.knowledge_point_scores" />
          </div>
          <div class="chart-item">
            <h4>數學素養能力</h4>
            <LiteracyRadarChart :scores="detail.assessment.math_literacy_scores" />
          </div>
        </div>

        <template v-if="detail.ai_analysis">
          <el-card shadow="never" style="margin-top: 16px">
            <h4>弱點分析</h4>
            <p style="white-space: pre-line">{{ detail.ai_analysis.weakness_analysis }}</p>
          </el-card>
          <el-card shadow="never" style="margin-top: 12px">
            <h4>強化建議</h4>
            <p style="white-space: pre-line">{{ detail.ai_analysis.enhancement_suggestions }}</p>
          </el-card>
        </template>
      </template>
      <el-empty v-else description="尚無評估結果" />
    </el-dialog>
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
</style>
