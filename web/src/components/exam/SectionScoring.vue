<!--
  單元評分區塊元件
  - 顯示單一測驗單元（section）的所有題目
  - 每題提供 el-input-number 讓老師輸入得分率（0~1，步進 0.1）
  - 透過 update:score 事件將分數變更回傳給父元件
  Props:
    section — 單元資料（含 name, knowledge_point, questions[]）
    scores  — 所有題目的得分率物件（key: question_id）
-->
<script setup>
const props = defineProps({
  /** 單元定義，包含 section_id, name, knowledge_point, questions[] */
  section: { type: Object, required: true },
  /** 全域得分率物件，key 為 question_id，value 為 0~1 */
  scores: { type: Object, required: true },
})

const emit = defineEmits(['update:score'])

/** 當老師修改某題分數時，發送事件通知父元件更新 */
function onScoreChange(questionId, value) {
  emit('update:score', questionId, value)
}
</script>

<template>
  <el-card class="section-card" shadow="never">
    <!-- 卡片標題：單元名稱 + 知識點標籤 -->
    <template #header>
      <span class="section-title">{{ section.name }}</span>
      <el-tag size="small" type="info" style="margin-left: 8px">{{ section.knowledge_point }}</el-tag>
    </template>

    <!-- 題目表格 -->
    <el-table :data="section.questions" stripe style="width: 100%">
      <el-table-column prop="question_id" label="題號" width="100" />
      <el-table-column label="得分率（0 ~ 1）" width="200">
        <template #default="{ row }">
          <el-input-number
            :model-value="scores[row.question_id] ?? 0"
            :min="0"
            :max="1"
            :step="0.1"
            :precision="1"
            size="small"
            controls-position="right"
            @update:model-value="(val) => onScoreChange(row.question_id, val)"
          />
        </template>
      </el-table-column>
      <el-table-column label="難度權重" width="120">
        <template #default="{ row }">
          {{ row.difficulty_weight }}
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<style scoped>
.section-card {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
}
</style>