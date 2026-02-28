<!--
  驗證碼管理頁面
  - 產生新驗證碼（指定試卷、前綴、數量）
  - 查看驗證碼清單及使用狀態
-->
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTeacherExams, generateCodes, getCodeList } from '@/api/teacher'

const exams = ref([])
const codes = ref([])
const loading = ref(false)

// 產生表單
const form = ref({ exam_id: '', prefix: '', count: 10, start_number: 1 })
const generating = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [examData, codeData] = await Promise.all([getTeacherExams(), getCodeList()])
    exams.value = examData
    codes.value = codeData
    if (examData.length > 0) form.value.exam_id = examData[0].exam_id
  } catch {
    ElMessage.error('載入資料失敗')
  } finally {
    loading.value = false
  }
})

async function handleGenerate() {
  if (!form.value.prefix.trim()) {
    ElMessage.warning('請輸入前綴')
    return
  }
  generating.value = true
  try {
    const newCodes = await generateCodes(form.value)
    codes.value = [...newCodes, ...codes.value]
    ElMessage.success(`成功產生 ${newCodes.length} 個驗證碼`)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '產生驗證碼失敗')
  } finally {
    generating.value = false
  }
}

function statusTag(status) {
  if (status === 'unused') return 'info'
  if (status === 'in_progress') return 'warning'
  return 'success'
}

function statusLabel(status) {
  if (status === 'unused') return '未使用'
  if (status === 'in_progress') return '測驗中'
  return '已完成'
}
</script>

<template>
  <div>
    <h2>驗證碼管理</h2>

    <!-- 產生表單 -->
    <el-card shadow="never" style="margin-bottom: 24px">
      <h3>產生新驗證碼</h3>
      <el-form :inline="true" :model="form">
        <el-form-item label="試卷">
          <el-select v-model="form.exam_id" placeholder="選擇試卷">
            <el-option v-for="e in exams" :key="e.exam_id" :label="e.name" :value="e.exam_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="前綴">
          <el-input v-model="form.prefix" placeholder="例如 APEX5A" style="width: 150px" />
        </el-form-item>
        <el-form-item label="數量">
          <el-input-number v-model="form.count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="起始編號">
          <el-input-number v-model="form.start_number" :min="1" :max="999" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="generating" @click="handleGenerate">產生</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 驗證碼列表 -->
    <el-table :data="codes" v-loading="loading" stripe>
      <el-table-column prop="code" label="驗證碼" width="180" />
      <el-table-column prop="exam_id" label="試卷" width="160" />
      <el-table-column label="狀態" width="120">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="建立時間" />
    </el-table>
  </div>
</template>
