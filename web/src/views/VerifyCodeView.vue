<!--
  驗證碼輸入頁面
  學生輸入驗證碼與姓名後，系統驗證並導向測驗頁或結果頁
-->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useStudentSession } from '@/composables/useStudentSession'

const router = useRouter()
const { verifyCode } = useStudentSession()

const code = ref('')
const studentName = ref('')
const loading = ref(false)

async function handleVerify() {
  if (!code.value.trim()) {
    ElMessage.warning('請輸入驗證碼')
    return
  }
  if (!studentName.value.trim()) {
    ElMessage.warning('請輸入姓名')
    return
  }

  loading.value = true
  try {
    const data = await verifyCode(code.value.trim(), studentName.value.trim())
    if (data.status === 'completed') {
      ElMessage.info('此驗證碼已完成測驗，將顯示結果報告')
      router.push({ name: 'student-result', params: { sessionId: data.session_id } })
    } else {
      router.push({ name: 'student-exam', params: { sessionId: data.session_id } })
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    ElMessage.error(detail || '驗證碼驗證失敗')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="verify-page">
    <el-card class="verify-card" shadow="always">
      <h1>峰數學能力檢測</h1>
      <p class="subtitle">請輸入驗證碼開始測驗</p>

      <el-form @submit.prevent="handleVerify" label-position="top">
        <el-form-item label="驗證碼">
          <el-input v-model="code" placeholder="請輸入驗證碼" />
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="studentName" placeholder="請輸入姓名" @keyup.enter="handleVerify" />
        </el-form-item>

        <el-button type="primary" :loading="loading" @click="handleVerify" style="width: 100%">
          開始測驗
        </el-button>
      </el-form>

      <div class="teacher-link">
        <router-link :to="{ name: 'login' }">教師 / 管理者登入 →</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.verify-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f7fa;
}

.verify-card {
  width: 400px;
  padding: 20px;
}

.verify-card h1 {
  text-align: center;
  margin: 0 0 4px;
  font-size: 24px;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin: 0 0 24px;
}

.teacher-link {
  text-align: center;
  margin-top: 16px;
}
</style>
