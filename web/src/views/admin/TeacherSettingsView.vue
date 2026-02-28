<!--
  教師管理頁面
  - 列出所有教師
  - 新增/編輯/停用教師帳號
  - 分配試卷權限
-->
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTeachers, createTeacher, updateTeacher, deleteTeacher, getExamTemplates, assignExamToTeacher } from '@/api/admin'

const teachers = ref([])
const exams = ref([])
const loading = ref(false)

// 新增對話框
const showCreateDialog = ref(false)
const createForm = ref({ username: '', password: '', display_name: '' })
const creating = ref(false)

// 分配試卷對話框
const showAssignDialog = ref(false)
const assignForm = ref({ teacher_id: '', exam_template_id: '' })

onMounted(async () => {
  loading.value = true
  try {
    const [t, e] = await Promise.all([getTeachers(), getExamTemplates()])
    teachers.value = t
    exams.value = e
  } catch {
    ElMessage.error('載入資料失敗')
  } finally {
    loading.value = false
  }
})

async function handleCreate() {
  if (!createForm.value.username || !createForm.value.password || !createForm.value.display_name) {
    ElMessage.warning('請填寫完整資訊')
    return
  }
  creating.value = true
  try {
    const teacher = await createTeacher(createForm.value)
    teachers.value.push(teacher)
    showCreateDialog.value = false
    createForm.value = { username: '', password: '', display_name: '' }
    ElMessage.success('教師建立成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '建立失敗')
  } finally {
    creating.value = false
  }
}

async function handleToggleActive(teacher) {
  try {
    if (teacher.is_active) {
      await deleteTeacher(teacher.id)
      teacher.is_active = false
      ElMessage.success('教師已停用')
    } else {
      await updateTeacher(teacher.id, { is_active: true })
      teacher.is_active = true
      ElMessage.success('教師已啟用')
    }
  } catch {
    ElMessage.error('操作失敗')
  }
}

async function handleAssign() {
  try {
    await assignExamToTeacher(assignForm.value)
    showAssignDialog.value = false
    ElMessage.success('試卷授權成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '授權失敗')
  }
}

function openAssignDialog(teacherId) {
  assignForm.value = { teacher_id: teacherId, exam_template_id: exams.value[0]?.id || '' }
  showAssignDialog.value = true
}
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2>教師管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">新增教師</el-button>
    </div>

    <el-table :data="teachers" v-loading="loading" stripe>
      <el-table-column prop="username" label="帳號" width="150" />
      <el-table-column prop="display_name" label="顯示名稱" width="150" />
      <el-table-column label="狀態" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '啟用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="openAssignDialog(row.id)">分配試卷</el-button>
          <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="handleToggleActive(row)">
            {{ row.is_active ? '停用' : '啟用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增教師對話框 -->
    <el-dialog v-model="showCreateDialog" title="新增教師" width="400px">
      <el-form label-position="top" :model="createForm">
        <el-form-item label="帳號">
          <el-input v-model="createForm.username" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="createForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="顯示名稱">
          <el-input v-model="createForm.display_name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">建立</el-button>
      </template>
    </el-dialog>

    <!-- 分配試卷對話框 -->
    <el-dialog v-model="showAssignDialog" title="分配試卷" width="400px">
      <el-form label-position="top" :model="assignForm">
        <el-form-item label="試卷">
          <el-select v-model="assignForm.exam_template_id" placeholder="選擇試卷">
            <el-option v-for="e in exams" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAssign">授權</el-button>
      </template>
    </el-dialog>
  </div>
</template>
