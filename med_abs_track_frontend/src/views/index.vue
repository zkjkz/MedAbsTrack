<template>
  <div class="dashboard-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="16">
      <el-col
        v-for="(item, index) in statisticsCards"
        :key="index"
        :xs="12"
        :sm="12"
        :md="6"
        :lg="6"
      >
        <el-card shadow="hover" class="stats-card">
          <div class="card-content">
            <div class="card-icon" :style="{ backgroundColor: item.color }">
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">{{ item.title }}</div>
              <div class="card-value">{{ item.value }}</div>
              <div class="card-footer">
                <div
                  :class="['growth-badge', item.growthRate > 0 ? 'up' : 'down']"
                >
                  <el-icon v-if="item.growthRate > 0"><ArrowUp /></el-icon>
                  <el-icon v-else><ArrowDown /></el-icon>
                  <span>{{ Math.abs(item.growthRate) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增上方左右布局的两个图表 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">热门关键词云图</span>
            </div>
          </template>
          <div ref="keywordCloudChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">摘要结构分析</span>
            </div>
          </template>
          <div ref="abstractStructureChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部期刊TOP10图表 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :sm="24" :md="24" :lg="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">TOP10期刊论文数量</span>
            </div>
          </template>
          <div
            ref="topJournalsChart"
            class="chart-container top-journals-chart"
          ></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="Dashboard">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { createChart, useChartResize } from '@/plugins/echarts.js'
import 'echarts-wordcloud'

import {
  Document,
  User,
  Search,
  DataAnalysis,
  ArrowDown,
  ArrowUp,
} from '@element-plus/icons-vue'
import {
  getTopJournals,
  getKeywordCloud,
  getAbstractStructureAnalysis,
} from '@/api/literature/statistics'

// 统计卡片数据
const statisticsCards = ref([
  {
    title: '文献总数',
    value: '2,538',
    icon: Document,
    color: '#409EFF',
    growthRate: 12.5,
  },
  {
    title: '系统用户数',
    value: '352',
    icon: User,
    color: '#67C23A',
    growthRate: 3.2,
  },
  {
    title: '检索次数',
    value: '4,671',
    icon: Search,
    color: '#E6A23C',
    growthRate: 16.8,
  },
  {
    title: '摘要结构化完成',
    value: '1,893',
    icon: DataAnalysis,
    color: '#F56C6C',
    growthRate: -2.4,
  },
])

// 新增图表引用
const keywordCloudChart = ref(null)
let keywordCloudChartInstance = null

const abstractStructureChart = ref(null)
let abstractStructureChartInstance = null

const topJournalsChart = ref(null)
let topJournalsChartInstance = null

// 初始化关键词云图
function initKeywordCloudChart() {
  if (!keywordCloudChartInstance) {
    keywordCloudChartInstance = createChart(keywordCloudChart.value)
  }

  // 默认加载中状态
  keywordCloudChartInstance.showLoading()

  // 获取关键词云数据
  getKeywordCloud(50)
    .then((response) => {
      keywordCloudChartInstance.hideLoading()

      const data = response.data || []
      const option = {
        tooltip: {
          show: true,
          formatter: function (params) {
            return params.name
          },
        },
        series: [
          {
            type: 'wordCloud',
            shape: 'circle',
            left: 'center',
            top: 'center',
            right: null,
            bottom: null,
            width: '90%',
            height: '90%',
            sizeRange: [14, 32],
            rotationRange: [-90, 90],
            rotationStep: 45,
            gridSize: 8,
            drawOutOfBound: false,
            textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            // Color can be a callback function or a color string
            color: function () {
                // Random color
                return 'rgb(' + [
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160)
                ].join(',') + ')';
              },
            },
            emphasis: {
              focus: 'self',
              textStyle: {
                shadowBlur: 10,
                shadowColor: '#333',
              },
            },
            data: data.map((item) => (
              {
              name: item.keyword,
              value: item.weight,
              textStyle: {
                color: 'rgb(' + 
                  [
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160),
                  ].join(',') + 
                  ')'
              },
            })),
          },
        ],
      }

      keywordCloudChartInstance.setOption(option)
    })
    .catch(() => {
      keywordCloudChartInstance.hideLoading()
    })
}

// 初始化摘要结构分析图表
function initAbstractStructureChart() {
  if (!abstractStructureChartInstance) {
    abstractStructureChartInstance = createChart(abstractStructureChart.value)
  }

  // 默认加载中状态
  abstractStructureChartInstance.showLoading()

  // 获取摘要结构分析数据
  getAbstractStructureAnalysis()
    .then((response) => {
      abstractStructureChartInstance.hideLoading()
      console.log(response)
      const data = response.data || {}

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}%',
        },
        legend: {
          orient: 'vertical',
          left: 10,
          top: 'center',
          textStyle: {
            fontSize: 12,
          },
        },
        series: [
          {
            name: '摘要结构比例',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2,
            },
            label: {
              show: false,
              position: 'center',
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold',
              },
            },
            labelLine: {
              show: false,
            },
            data: [
              { value: data.background.length || 20, name: '背景' },
              { value: data.methods.length || 30, name: '方法' },
              { value: data.results.length || 35, name: '结果' },
              { value: data.conclusion.length || 15, name: '结论' },
            ],
          },
        ],
      }

      abstractStructureChartInstance.setOption(option)
    })
    .catch(() => {
      abstractStructureChartInstance.hideLoading()
    })
}

// 初始化TOP10期刊论文数量图表
function initTopJournalsChart() {
  if (!topJournalsChartInstance) {
    topJournalsChartInstance = createChart(topJournalsChart.value)
  }

  // 默认加载中状态
  topJournalsChartInstance.showLoading()

  // 获取TOP10期刊数据
  getTopJournals()
    .then((response) => {
      topJournalsChartInstance.hideLoading()
      const data = response.data || []
      // 按论文数量排序（降序，显示数量最多的在顶部）
      data.sort((a, b) => b.paper_count - a.paper_count)  

      const journalNames = data.map((item) => item.journal_name)
      const paperCounts = data.map((item) => item.paper_count)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: journalNames,
          axisLabel: {
            rotate: 45,
            interval: 0,
            fontSize: 11,
            width: 100,
            overflow: 'break'
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '论文数量',
            type: 'bar',
            data: paperCounts,
            itemStyle: {
              color: function (params) {
                // 使用与统计卡片一致的颜色系统
                const colorList = [
                  '#409EFF', // 蓝色
                  '#4CABFF', 
                  '#67C23A', // 绿色
                  '#85CF5C',
                  '#E6A23C', // 橙色
                  '#F2B75E',
                  '#F56C6C', // 红色
                  '#F78989',
                  '#909399', // 灰色
                  '#B2B6BD'
                ]
                return colorList[params.dataIndex] || '#409EFF'
              },
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}',
            },
            barWidth: '50%'
          },
        ],
      }

      topJournalsChartInstance.setOption(option)
    })
    .catch((error) => {
      console.error('获取TOP10期刊数据失败:', error)
      topJournalsChartInstance.hideLoading()
      // 显示空数据状态
      topJournalsChartInstance.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center',
          textStyle: {
            color: '#999',
            fontSize: 14,
            fontWeight: 'normal'
          }
        }
      })
    })
}

// 监听窗口大小变化调整图表
function handleResize() {
  // 根据屏幕宽度动态调整图表高度
  const height = getChartHeight()
  const chartContainers = document.querySelectorAll('.chart-container')

  chartContainers.forEach((container) => {
    container.style.height = `${height}px`
  })

  // 重新调整图表大小
  if (keywordCloudChartInstance) keywordCloudChartInstance.resize()
  if (abstractStructureChartInstance) abstractStructureChartInstance.resize()
  if (topJournalsChartInstance) topJournalsChartInstance.resize()
}

// 根据屏幕宽度动态调整图表高度
function getChartHeight() {
  const width = window.innerWidth
  if (width <= 768) {
    return 250 // 小屏幕
  } else if (width <= 1200) {
    return 300 // 中等屏幕
  } else {
    return 350 // 大屏幕
  }
}

// 使用自定义的图表大小调整函数
let disposeChartResize

// 组件挂载后初始化图表
onMounted(() => {
  handleResize() // 初始化设置高度

  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)

  // 初始化新增的三个图表
  initKeywordCloudChart()
  initAbstractStructureChart()
  initTopJournalsChart()

  // 使用统一的图表大小调整功能
  const chartInstances = [
    keywordCloudChartInstance,
    abstractStructureChartInstance,
    topJournalsChartInstance,
  ]
  disposeChartResize = useChartResize({
    resize: () => {
      chartInstances.forEach((instance) => instance && instance.resize())
    },
    dispose: () => {
      chartInstances.forEach((instance) => instance && instance.dispose())
    },
  })
})

// 组件卸载前清理资源
onBeforeUnmount(() => {
  // 移除窗口大小变化监听
  window.removeEventListener('resize', handleResize)

  if (disposeChartResize) {
    disposeChartResize()
  }
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 1rem;

  // 行间距
  .el-row {
    margin-bottom: 1.25rem;

    &.chart-row {
      margin-bottom: 1.5rem;
    }
  }

  // 卡片基础样式
  .el-card {
    margin-bottom: 1rem;
    transition: all 0.3s;
    border-radius: 0.5rem;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    }
  }

  // 统计卡片
  .stats-card {
    height: auto;
    margin-bottom: 1rem;

    .card-content {
      display: flex;
      align-items: center;
      padding: 1rem;

      .card-icon {
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        flex-shrink: 0;

        .el-icon {
          font-size: 1.5rem;
          color: white;
        }
      }

      .card-info {
        flex: 1;
        min-width: 0;

        .card-title {
          font-size: 0.875rem;
          color: #606266;
          margin-bottom: 0.5rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .card-value {
          font-size: 1.5rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .card-footer {
          display: flex;
          align-items: center;

          .growth-badge {
            display: flex;
            align-items: center;
            font-size: 0.875rem;
            font-weight: 500;
            padding: 0.125rem 0.5rem;
            border-radius: 1rem;

            &.up {
              color: #67c23a;
              background-color: rgba(103, 194, 58, 0.1);
            }

            &.down {
              color: #f56c6c;
              background-color: rgba(245, 108, 108, 0.1);
            }

            .el-icon {
              margin-right: 0.25rem;
              font-size: 0.875rem;
            }
          }
        }
      }
    }
  }

  // 图表卡片
  .chart-card {
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__header) {
      padding: 0.75rem 1rem;
    }

    :deep(.el-card__body) {
      flex: 1;
      padding: 0.75rem;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #303133;
      }
    }

    .chart-container {
      flex: 1;
      min-height: 250px;
      width: 100%;

      &.top-journals-chart {
        min-height: 400px; // 为TOP10期刊图表设置更高高度
      }
    }
  }

  // 响应式调整
  @media screen and (max-width: 768px) {
    padding: 0.5rem;

    .stats-card {
      .card-content {
        padding: 0.75rem;

        .card-icon {
          width: 2.5rem;
          height: 2.5rem;

          .el-icon {
            font-size: 1.25rem;
          }
        }

        .card-info {
          .card-title {
            font-size: 0.75rem;
          }

          .card-value {
            font-size: 1.25rem;
          }

          .growth-badge {
            font-size: 0.75rem;
          }
        }
      }
    }
  }
}
</style>
