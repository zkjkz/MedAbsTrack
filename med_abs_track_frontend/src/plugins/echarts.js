// 引入 echarts 核心模块
import * as echarts from 'echarts/core'

// 引入常用图表组件
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  GaugeChart
} from 'echarts/charts'

// 引入词云图扩展
import 'echarts-wordcloud'

// 引入常用组件配置项
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent
} from 'echarts/components'


// 引入渲染器
import { SVGRenderer, CanvasRenderer } from 'echarts/renderers'

// 注册必须的组件
echarts.use([
  // 图表类型
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  GaugeChart,
  
  // 组件配置
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent,
  
  // 渲染器
  CanvasRenderer,
  SVGRenderer
])

// 自动调整图表大小的方法
export function useChartResize(chartInstance) {
  const resizeHandler = () => {
    chartInstance && chartInstance.resize()
  }
  
  window.addEventListener('resize', resizeHandler)
  
  return () => {
    window.removeEventListener('resize', resizeHandler)
    chartInstance && chartInstance.dispose()
  }
}

// 创建图表实例的方法
export function createChart(el) {
  return echarts.init(el)
}

// 导出echarts核心以便访问其他API
export { echarts }

// 默认导出
export default echarts 