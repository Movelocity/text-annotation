<template>
  <div class="label-stats-chart">
    <div v-if="!hasData" class="no-data">
      <el-empty description="暂无统计数据" />
    </div>
    <div v-else class="chart-container">
      <div class="chart-header">
        <div class="chart-controls">
          <el-radio-group v-model="chartType" size="small">
            <el-radio-button value="bar">柱状图</el-radio-button>
            <el-radio-button value="pie">饼图</el-radio-button>
          </el-radio-group>
          <el-select 
            v-model="displayCount" 
            size="small" 
            style="width: 120px; margin-left: 12px;"
          >
            <el-option label="显示前5个" :value="5" />
            <el-option label="显示前10个" :value="10" />
            <el-option label="显示前20个" :value="20" />
            <el-option label="显示全部" :value="0" />
          </el-select>
        </div>
      </div>
      
      <div class="chart-content">
        <v-chart 
          class="chart" 
          :option="chartOption" 
          :autoresize="true"
          @click="handleChartClick"
        />
      </div>

      <div class="chart-summary">
        <el-row :gutter="16">
          <el-col :span="8">
            <div class="summary-item">
              <div class="summary-label">最常用标签</div>
              <div class="summary-value">{{ topLabel?.label || '-' }}</div>
              <div class="summary-count">{{ topLabel?.count || 0 }} 次</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-item">
              <div class="summary-label">平均使用次数</div>
              <div class="summary-value">{{ averageUsage }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-item">
              <div class="summary-label">使用率</div>
              <div class="summary-value">{{ usageRate }}%</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import type { LabelStats } from '@/types/api'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

interface Props {
  stats: LabelStats[]
}

const props = defineProps<Props>()

// 响应式数据
const chartType = ref<'bar' | 'pie'>('bar')
const displayCount = ref(10)

// 计算属性
const hasData = computed(() => props.stats && props.stats.length > 0)

const sortedStats = computed(() => {
  return [...props.stats].sort((a, b) => b.count - a.count)
})

const displayStats = computed(() => {
  if (displayCount.value === 0) {
    return sortedStats.value
  }
  return sortedStats.value.slice(0, displayCount.value)
})

const topLabel = computed(() => sortedStats.value[0] || null)

const averageUsage = computed(() => {
  if (!hasData.value) return 0
  const total = props.stats.reduce((sum, stat) => sum + stat.count, 0)
  return Math.round(total / props.stats.length)
})

const usageRate = computed(() => {
  if (!hasData.value) return 0
  const usedLabels = props.stats.filter(stat => stat.count > 0).length
  return Math.round((usedLabels / props.stats.length) * 100)
})

// 图表配置
const chartOption = computed(() => {
  if (!hasData.value) return {}

  const data = displayStats.value

  if (chartType.value === 'bar') {
    return {
      title: {
        text: '标签使用频率统计',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params: any) => {
          const item = params[0]
          return `${item.name}<br/>使用次数: ${item.value}`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.label),
        axisLabel: {
          rotate: data.length > 10 ? 45 : 0,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: '使用次数'
      },
      series: [
        {
          name: '使用次数',
          type: 'bar',
          data: data.map(item => ({
            value: item.count,
            itemStyle: {
              color: getBarColor(item.count, data[0].count)
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  } else {
    return {
      title: {
        text: '标签使用分布',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        type: 'scroll',
        orient: 'vertical',
        right: 10,
        top: 20,
        bottom: 20
      },
      series: [
        {
          name: '标签使用',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: data.map((item, index) => ({
            value: item.count,
            name: item.label,
            itemStyle: {
              color: getPieColor(index)
            }
          }))
        }
      ]
    }
  }
})

// 方法
const getBarColor = (value: number, maxValue: number) => {
  const ratio = value / maxValue
  if (ratio >= 0.8) return '#67c23a'
  if (ratio >= 0.6) return '#409eff'
  if (ratio >= 0.4) return '#e6a23c'
  if (ratio >= 0.2) return '#f56c6c'
  return '#909399'
}

const getPieColor = (index: number) => {
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#ff9f7f',
    '#87d068', '#40a9ff', '#36cfc9', '#b37feb', '#ffadd2'
  ]
  return colors[index % colors.length]
}

const handleChartClick = (params: any) => {
  console.log('Chart clicked:', params)
  // 这里可以添加点击事件处理，比如跳转到该标签的详情页面
}

// 监听图表类型变化，重置显示数量
watch(chartType, () => {
  if (chartType.value === 'pie' && displayCount.value > 15) {
    displayCount.value = 10
  }
})
</script>

<style scoped>
.label-stats-chart {
  width: 100%;
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.chart-container {
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.chart-controls {
  display: flex;
  align-items: center;
}

.chart-content {
  width: 100%;
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-summary {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.summary-count {
  font-size: 12px;
  color: #606266;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .chart-controls {
    justify-content: center;
  }

  .chart-content {
    height: 300px;
  }
}
</style> 