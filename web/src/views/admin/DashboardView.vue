<!--
  管理者首頁 — 統計概覽
-->
<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '@/api/admin'

const stats = ref(null)

onMounted(async () => {
  try {
    stats.value = await getDashboardStats()
  } catch {
    // 靜默處理
  }
})
</script>

<template>
  <div>
    <h2>管理者總覽</h2>
    <div v-if="stats" class="stats-row">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ stats.teacher_count }}</div>
        <div class="stat-label">教師</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ stats.exam_count }}</div>
        <div class="stat-label">試卷</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ stats.session_count }}</div>
        <div class="stat-label">測驗紀錄</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-number">{{ stats.code_count }}</div>
        <div class="stat-label">驗證碼</div>
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
