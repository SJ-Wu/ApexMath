<!--
  學生測驗 Layout
  簡潔的頂部標題 + 內容區
-->
<script setup>
import { useStudentSession } from '@/composables/useStudentSession'
import { useRouter } from 'vue-router'

const router = useRouter()
const { clearSession } = useStudentSession()

function handleExit() {
  clearSession()
  router.push({ name: 'verify-code' })
}
</script>

<template>
  <div class="student-layout">
    <div class="student-header">
      <h2>峰數學能力檢測</h2>
      <el-button text size="small" @click="handleExit">離開</el-button>
    </div>
    <div class="student-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.student-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.student-header h2 {
  margin: 0;
  font-size: 18px;
}

.student-content {
  max-width: 900px;
  margin: 24px auto;
  padding: 0 20px;
}
</style>
