/**
 * ECharts 圖表配置工廠
 * 提供兩種圖表的 option 產生函式：
 *   1. getKnowledgeBarOptions — 知識點能力長條圖（10 個類別，Y 軸 0~5 分）
 *   2. getLiteracyRadarOptions — 數學素養雷達圖（4 個維度，最大值 5 分）
 */

/** 十大知識點類別（對應後端 KnowledgePointCategory 列舉） */
const knowledgeCategories = [
  '正整數', '小數', '分數', '容積', '距離問題',
  '時間問題', '解題策略', '規律推演', '面積/立方體', '資優挑戰',
]

/** 四大數學素養維度（對應後端 MathLiteracyDimension 列舉） */
const literacyDimensions = [
  '概念理解', '計算流暢度', '情境策略與脈絡素養', '邏輯推理',
]

/**
 * 產生知識點能力長條圖的 ECharts option
 * @param {number[]} scores - 長度為 10 的分數陣列（0~5），順序對應 knowledgeCategories
 * @returns {Object} ECharts option 物件
 */
export function getKnowledgeBarOptions(scores) {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, bottom: 80, top: 30 },
    xAxis: {
      type: 'category',
      data: knowledgeCategories,
      axisLabel: { rotate: 30, fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 5,
      interval: 1,
      name: '分數',
    },
    series: [
      {
        type: 'bar',
        data: scores,
        barMaxWidth: 40,
        // 依分數高低給予不同顏色：≥4 綠、≥3 藍、≥2 橘、<2 紅
        itemStyle: {
          color: (params) => {
            const value = params.value
            if (value >= 4) return '#67C23A'
            if (value >= 3) return '#409EFF'
            if (value >= 2) return '#E6A23C'
            return '#F56C6C'
          },
        },
        label: {
          show: true,
          position: 'top',
          formatter: ({ value }) => value.toFixed(1),
        },
      },
    ],
  }
}

/**
 * 產生數學素養雷達圖的 ECharts option
 * @param {number[]} scores - 長度為 4 的分數陣列（0~5），順序對應 literacyDimensions
 * @returns {Object} ECharts option 物件
 */
export function getLiteracyRadarOptions(scores) {
  return {
    tooltip: {},
    radar: {
      indicator: literacyDimensions.map((name) => ({ name, max: 5 })),
      shape: 'polygon',
      radius: '65%',
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: scores,
            name: '數學素養',
            areaStyle: { opacity: 0.3 },
            lineStyle: { width: 2 },
          },
        ],
      },
    ],
  }
}