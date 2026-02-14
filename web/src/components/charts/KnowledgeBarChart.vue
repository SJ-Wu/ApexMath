<!--
  知識點能力長條圖元件
  - 使用 ECharts 按需引入（BarChart + Grid + Tooltip）
  - 接收 scores 陣列（長度 10，對應十大知識點類別，值 0~5）
  - 透過 vue-echarts 的 VChart 渲染，支援自動調整大小
-->
<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getKnowledgeBarOptions } from '@/utils/chartOptions'

// 註冊 ECharts 所需模組（按需引入以減少打包體積）
use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const props = defineProps({
  /** 十大知識點的分數陣列，順序對應 chartOptions 中的 knowledgeCategories */
  scores: { type: Array, required: true },
})

const option = computed(() => getKnowledgeBarOptions(props.scores))
</script>

<template>
  <VChart :option="option" autoresize style="height: 350px; width: 100%" />
</template>