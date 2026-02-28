<!--
  試卷管理頁面
  - 列出所有試卷模板
  - 未來可擴充 CRUD 功能
-->
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getExamTemplates } from '@/api/admin'

const exams = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    exams.value = await getExamTemplates()
  } catch {
    ElMessage.error('載入試卷失敗')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h2>試卷管理</h2>

    <el-table :data="exams" v-loading="loading" stripe>
      <el-table-column prop="exam_id" label="試卷 ID" width="200" />
      <el-table-column prop="name" label="名稱" width="200" />
      <el-table-column label="狀態" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '啟用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-alert
      type="info"
      title="試卷 CRUD 功能將在未來版本開放"
      :closable="false"
      style="margin-top: 24px"
    />
  </div>
</template>
