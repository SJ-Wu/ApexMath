<!--
  管理者後台 Layout
  左側導覽列 + 右側內容區
-->
<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { displayName, logout } = useAuth()

function handleLogout() {
  logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <el-container class="admin-layout">
    <el-aside width="220px">
      <div class="logo">峰數學 - 管理</div>
      <el-menu :router="true" :default-active="$route.name" class="side-menu">
        <el-menu-item index="admin-dashboard" :route="{ name: 'admin-dashboard' }">
          首頁總覽
        </el-menu-item>
        <el-menu-item index="admin-exams" :route="{ name: 'admin-exams' }">
          試卷管理
        </el-menu-item>
        <el-menu-item index="admin-teachers" :route="{ name: 'admin-teachers' }">
          教師管理
        </el-menu-item>
        <el-menu-item index="admin-students" :route="{ name: 'admin-students' }">
          學生紀錄
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="top-bar">
        <span>{{ displayName }}</span>
        <el-button text @click="handleLogout">登出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.el-aside {
  background: #304156;
}

.logo {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  padding: 20px;
  text-align: center;
}

.side-menu {
  border-right: none;
  background: #304156;
}

.side-menu .el-menu-item {
  color: #bfcbd9;
}

.side-menu .el-menu-item.is-active {
  color: #409eff;
  background: #263445;
}

.top-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #e4e7ed;
}
</style>
