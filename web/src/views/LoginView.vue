<!--
  登入頁面
  Admin / Teacher 共用帳密登入，登入後依角色導向對應後台
-->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.warning('請輸入帳號與密碼')
    return
  }

  loading.value = true
  try {
    const data = await login(username.value, password.value)
    ElMessage.success(`歡迎，${data.display_name}`)
    if (data.role === 'admin') {
      router.push({ name: 'admin-dashboard' })
    } else {
      router.push({ name: 'teacher-dashboard' })
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    ElMessage.error(detail || '登入失敗，請確認帳號密碼')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card" shadow="always">
      <h1>峰數學能力檢測平台</h1>
      <p class="subtitle">教師 / 管理者登入</p>

      <el-form @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="帳號">
          <el-input v-model="username" placeholder="請輸入帳號" :prefix-icon="'User'" />
        </el-form-item>

        <el-form-item label="密碼">
          <el-input
            v-model="password"
            type="password"
            placeholder="請輸入密碼"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%">
          登入
        </el-button>
      </el-form>

      <div class="student-link">
        <router-link :to="{ name: 'verify-code' }">學生測驗入口 →</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f7fa;
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-card h1 {
  text-align: center;
  margin: 0 0 4px;
  font-size: 24px;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin: 0 0 24px;
}

.student-link {
  text-align: center;
  margin-top: 16px;
}
</style>
