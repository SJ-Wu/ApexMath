<!--
  數學素養雷達圖元件
  - 使用 ECharts 按需引入（RadarChart + Radar + Tooltip）
  - 接收 scores 陣列（長度 4，對應四大數學素養維度，值 0~5）
  - 透過 vue-echarts 的 VChart 渲染，支援自動調整大小
-->
<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart } from 'echarts/charts'
import { TooltipComponent, RadarComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getLiteracyRadarOptions } from '@/utils/chartOptions'

// 註冊 ECharts 所需模組（按需引入以減少打包體積）
use([CanvasRenderer, RadarChart, TooltipComponent, RadarComponent])

const props = defineProps({
  /** 四大數學素養維度的分數陣列，順序對應 chartOptions 中的 literacyDimensions */
  scores: { type: Array, required: true },
})

const option = computed(() => getLiteracyRadarOptions(props.scores))
</script>

<template>
  <VChart :option="option" autoresize style="height: 350px; width: 100%" />
</template>