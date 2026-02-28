<!--
  教師首頁
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { getTeacherExams, getCodeList, getExamResults } from '@/api/teacher'

const { displayName } = useAuth()
const exams = ref([])
const codeCount = ref(0)
const resultCount = ref(0)

onMounted(async () => {
  try {
    const [examData, codeData, resultData] = await Promise.all([
      getTeacherExams(),
      getCodeList(),
      getExamResults(),
    ])
    exams.value = examData
    codeCount.value = codeData.length
    resultCount.value = resultData.length
  } catch {
    // 載入失敗靜默處理
  }
})
</script>

<template>
  <div>
    <h2>歡迎，{{ displayName }}</h2>
    <div class="stats-row">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ exams.length }}</div>
        <div class="stat-label">可用試卷</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ codeCount }}</div>
        <div class="stat-label">驗證碼</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ resultCount }}</div>
        <div class="stat-label">測驗紀錄</div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.stats-row {
  display: flex;
  gap: 20px;
  margin-top: 24px;
}

.stat-card {
  flex: 1;
  text-align: center;
  padding: 12px;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #909399;
  margin-top: 4px;
}
</style>
