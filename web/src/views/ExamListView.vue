<!--
  測驗卷列表頁
  - 進入頁面時呼叫 API 取得所有測驗卷 ID
  - 以卡片形式呈現每張測驗卷，點擊後導航至評分頁
  - 處理 loading 與 error 狀態
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getExamList } from '@/api/exam'

const router = useRouter()
const examIds = ref([])       // 測驗卷 ID 列表
const loading = ref(false)    // 資料載入中
const error = ref('')         // 錯誤訊息

onMounted(async () => {
  loading.value = true
  try {
    const data = await getExamList()
    examIds.value = data.exam_ids
  } catch (e) {
    error.value = '無法載入測驗列表，請確認後端服務是否啟動。'
  } finally {
    loading.value = false
  }
})

/** 導航至指定測驗卷的評分頁 */
function goToExam(examId) {
  router.push({ name: 'exam-scoring', params: { examId } })
}
</script>

<template>
  <div class="exam-list-page">
    <h1>峰數學能力檢測平台</h1>
    <p class="subtitle">請選擇測驗卷開始評分</p>

    <!-- 錯誤提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" style="margin-bottom: 20px" />

    <div v-loading="loading" class="card-container">
      <!-- 測驗卷卡片 -->
      <el-card
        v-for="id in examIds"
        :key="id"
        shadow="hover"
        class="exam-card"
        @click="goToExam(id)"
      >
        <h2>{{ id }}</h2>
        <p>點擊進入評分</p>
      </el-card>

      <!-- 空狀態 -->
      <el-empty v-if="!loading && examIds.length === 0 && !error" description="目前沒有可用的測驗卷" />
    </div>
  </div>
</template>

<style scoped>
.exam-list-page {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

h1 {
  text-align: center;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 32px;
}

.card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.exam-card {
  cursor: pointer;
  flex: 1 1 300px;
  transition: transform 0.2s;
}

.exam-card:hover {
  transform: translateY(-4px);
}

.exam-card h2 {
  margin: 0 0 8px;
}

.exam-card p {
  color: #909399;
  margin: 0;
}
</style>