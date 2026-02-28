<!--
  學生紀錄頁面
  - 查看所有學生測驗紀錄
-->
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAllSessions } from '@/api/admin'

const sessions = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    sessions.value = await getAllSessions()
  } catch {
    ElMessage.error('載入紀錄失敗')
  } finally {
    loading.value = false
  }
})

function statusLabel(status) {
  if (status === 'in_progress') return '測驗中'
  return '已完成'
}
</script>

<template>
  <div>
    <h2>學生測驗紀錄</h2>

    <el-table :data="sessions" v-loading="loading" stripe>
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
    </el-table>
  </div>
</template>
