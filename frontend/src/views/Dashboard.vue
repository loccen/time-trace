<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>今日概览</h1>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatHours(dashboardData.stats.today_hours) }}</div>
          <div class="stat-label">今日工时</div>
          <div class="stat-status" :class="getStatusClass(dashboardData.stats.today_status)">
            {{ getStatusText(dashboardData.stats.today_status) }}
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatHours(dashboardData.stats.week_hours) }}</div>
          <div class="stat-label">本周工时</div>
          <div class="stat-status positive">📊 {{ dashboardData.stats.week_change }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatHours(dashboardData.stats.month_hours) }}</div>
          <div class="stat-label">本月工时</div>
          <div class="stat-status positive">📈 {{ dashboardData.stats.month_change }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatHours(dashboardData.stats.avg_hours) }}</div>
          <div class="stat-label">平均工时</div>
          <div class="stat-status" :class="getStatusClass(dashboardData.stats.avg_status)">
            {{ getStatusText(dashboardData.stats.avg_status) }}
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatHours(dashboardData.stats.month_overtime) }}</div>
          <div class="stat-label">本月加班</div>
          <div class="stat-status" :class="getStatusClass(dashboardData.stats.month_overtime_status)">
            {{ getStatusText(dashboardData.stats.month_overtime_status) }}
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatHours(dashboardData.stats.last_month_overtime) }}</div>
          <div class="stat-label">上月加班</div>
          <div class="stat-status positive">📉 {{ dashboardData.stats.overtime_change }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>每日工时柱状图</h3>
        <div class="chart-placeholder bar-chart">
          <div class="bar-container">
            <div
              v-for="(item, index) in dashboardData.charts.bar_chart"
              :key="index"
              class="bar"
              :class="{ overtime: item.is_overtime }"
              :style="{ height: Math.max(item.hours / 10 * 100, 5) + '%' }"
              :data-value="formatHours(item.hours)"
              :data-hours="item.hours"
            ></div>
          </div>
          <div class="chart-labels">
            <span v-for="(item, index) in dashboardData.charts.bar_chart" :key="index">
              {{ item.day_name }}
            </span>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <h3>工时分布饼图</h3>
        <div class="chart-placeholder pie-chart">
          <div class="pie-segment"></div>
        </div>
        <div class="pie-legend">
          <div
            v-for="(item, index) in dashboardData.charts.pie_chart"
            :key="index"
            class="legend-item"
          >
            <span
              class="legend-color"
              :style="{ background: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'][index] }"
            ></span>
            <span>{{ item.label }} ({{ item.percentage }}%)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速操作</h2>
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/time-records')">
          <el-icon><Clock /></el-icon>
          工时记录
        </el-button>
        <el-button type="success" @click="$router.push('/statistics')">
          <el-icon><DataAnalysis /></el-icon>
          统计分析
        </el-button>
        <el-button type="info" @click="$router.push('/system-events')">
          <el-icon><Bell /></el-icon>
          系统事件
        </el-button>
        <el-button type="warning" @click="$router.push('/settings')">
          <el-icon><Setting /></el-icon>
          系统设置
        </el-button>
      </div>
    </div>

    <!-- 工作模式分析 -->
    <div class="analysis-section">
      <h2>工作模式分析</h2>
      <div class="analysis-grid">
        <div class="analysis-item">
          <span class="analysis-label">最常见上班时间:</span>
          <span class="analysis-value">{{ dashboardData.analysis.most_common_start_time }}</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">最常见下班时间:</span>
          <span class="analysis-value">{{ dashboardData.analysis.most_common_end_time }}</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">平均午休时长:</span>
          <span class="analysis-value">{{ dashboardData.analysis.avg_break_duration }}</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">加班频率:</span>
          <span class="analysis-value">{{ dashboardData.analysis.overtime_frequency }}</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">工作效率最高时段:</span>
          <span class="analysis-value">{{ dashboardData.analysis.peak_efficiency_time }}</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">平均通勤时间:</span>
          <span class="analysis-value">{{ dashboardData.analysis.avg_commute_time }}</span>
        </div>
      </div>
    </div>

    <!-- 今日时间轴 -->
    <div class="timeline-section">
      <div class="section-header">
        <h2>今日时间轴</h2>
      </div>
      <div class="timeline">
        <div
          v-for="(item, index) in dashboardData.timeline"
          :key="index"
          class="timeline-item"
          :class="{ current: item.is_current }"
        >
          <div class="timeline-time">{{ item.time }}</div>
          <div class="timeline-dot" :class="{ current: item.is_current }"></div>
          <div class="timeline-content">
            <div class="timeline-title">{{ item.title }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Clock, Calendar, TrendCharts, DataAnalysis, Bell, Setting, Timer } from '@element-plus/icons-vue'
import { statisticsApi } from '@/api/statistics'
import { ElMessage } from 'element-plus'

// 响应式数据
const loading = ref(false)
const dashboardData = ref({
  stats: {
    today_hours: 0,
    today_status: 'no_record',
    week_hours: 0,
    week_change: '+0%',
    month_hours: 0,
    month_change: '+0%',
    avg_hours: 0,
    avg_status: 'stable',
    month_overtime: 0,
    month_overtime_status: 'normal',
    last_month_overtime: 0,
    overtime_change: '+0%'
  },
  charts: {
    bar_chart: [],
    pie_chart: []
  },
  analysis: {
    most_common_start_time: "09:00 (占比 68%)",
    most_common_end_time: "18:30 (占比 45%)",
    avg_break_duration: "1小时15分钟",
    overtime_frequency: "15% (超过9小时的工作日)",
    peak_efficiency_time: "上午 10:00-12:00",
    avg_commute_time: "45分钟"
  },
  timeline: [
    { time: "09:00", title: "上班打卡", is_current: false },
    { time: "12:00", title: "午休开始", is_current: false },
    { time: "13:00", title: "午休结束", is_current: false },
    { time: "15:30", title: "当前时间", is_current: true }
  ]
})

// 格式化工时显示
const formatHours = (hours) => {
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  return `${h}h ${m}m`
}

// 获取状态显示文本
const getStatusText = (status) => {
  const statusMap = {
    'working': '🕐 正在工作',
    'no_record': '📊 无记录',
    'stable': '📊 稳定',
    'warning': '⚠️ 偏高',
    'normal': '📉 正常'
  }
  return statusMap[status] || status
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classMap = {
    'working': 'working',
    'stable': 'stable',
    'warning': 'warning',
    'normal': 'positive'
  }
  return classMap[status] || 'stable'
}

// 加载仪表板数据
const loadDashboardData = async () => {
  loading.value = true
  try {
    // 先使用测试API
    const response = await statisticsApi.getDashboardOverview()
    if (response.success) {
      const data = response.data

      // 更新统计数据
      dashboardData.value.stats.today_hours = data.today?.hours || 0
      dashboardData.value.stats.today_status = data.today?.status === 'normal' ? 'working' : 'no_record'
      dashboardData.value.stats.week_hours = data.this_week?.total_hours || 0
      dashboardData.value.stats.month_hours = data.this_month?.total_hours || 0
      dashboardData.value.stats.avg_hours = data.this_week?.avg_daily_hours || 0

      // 生成图表数据
      if (data.recent_trend) {
        dashboardData.value.charts.bar_chart = data.recent_trend.map((item, index) => ({
          date: item.date,
          hours: item.hours,
          is_overtime: item.hours > 8,
          day_name: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][index % 7]
        }))
      }

      // 生成饼图数据（模拟）
      dashboardData.value.charts.pie_chart = [
        { label: "8-9小时", value: 10, percentage: 45 },
        { label: "7-8小时", value: 5, percentage: 25 },
        { label: "9-10小时", value: 4, percentage: 20 },
        { label: "其他", value: 2, percentage: 10 }
      ]
    }
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  // 页面头部
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h1 {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  // 统计卡片网格
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
  }

  .stat-card {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    background: #409eff;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 20px;
  }

  .stat-content {
    flex: 1;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-status {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 12px;
    background: #f0f9ff;
    color: #409eff;

    &.working {
      background: #f0f9ff;
      color: #409eff;
    }

    &.positive {
      background: #f0f9ff;
      color: #67c23a;
    }

    &.stable {
      background: #f5f7fa;
      color: #909399;
    }

    &.warning {
      background: #fdf6ec;
      color: #e6a23c;
    }
  }

  // 快速操作
  .quick-actions {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;

    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 20px 0;
    }
  }

  .action-buttons {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  // 图表区域
  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
  }

  .chart-card {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 20px 0;
    }
  }

  .chart-placeholder {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f7fa;
    border-radius: 4px;
    position: relative;
  }

  // 柱状图样式
  .bar-chart {
    display: flex;
    flex-direction: column;
    padding: 20px;
    height: 200px;
    position: relative;
    background: transparent;
    border: none;
    align-items: stretch;
    justify-content: stretch;
  }

  .bar-container {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex: 1;
    margin-bottom: 10px;
    position: relative;
    padding: 0 15px;

    // 8小时基准线
    &::before {
      content: '';
      position: absolute;
      left: 15px;
      right: 15px;
      top: 20%; // 80%高度对应8小时
      height: 1px;
      background: #e6a23c;
      border-top: 1px dashed #e6a23c;
      z-index: 1;
    }

    &::after {
      content: '8h';
      position: absolute;
      left: 0;
      top: 20%;
      transform: translateY(-50%);
      font-size: 12px;
      color: #e6a23c;
      background: #fff;
      padding: 0 4px;
      z-index: 2;
    }
  }

  .bar {
    width: 25px;
    background: #409eff;
    border-radius: 2px 2px 0 0;
    min-height: 20px;
    transition: opacity 0.3s;
    position: relative;
    flex-shrink: 0;
    z-index: 3;

    &.overtime {
      background: #f56c6c;
    }

    &:hover {
      opacity: 0.8;
    }

    &:hover::after {
      content: attr(data-value);
      position: absolute;
      top: -25px;
      left: 50%;
      transform: translateX(-50%);
      background: #303133;
      color: #fff;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12px;
      white-space: nowrap;
    }
  }

  .chart-labels {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #909399;
    padding: 0 15px;

    span {
      flex: 1;
      text-align: center;
      font-size: 12px;
    }
  }

  // 饼图样式
  .pie-chart {
    flex-direction: row;
    gap: 20px;
    align-items: center;
    justify-content: center;
  }

  .pie-segment {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: conic-gradient(
      #409eff 0deg 162deg,
      #67c23a 162deg 252deg,
      #e6a23c 252deg 324deg,
      #f56c6c 324deg 360deg
    );
    margin: 0 auto;
  }

  .pie-legend {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 16px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #606266;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }

  // 工作模式分析
  .analysis-section {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;
    margin-bottom: 32px;

    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 20px 0;
    }
  }

  .analysis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
  }

  .analysis-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 6px;
    border-left: 3px solid #409eff;
  }

  .analysis-label {
    font-size: 14px;
    color: #606266;
    font-weight: 500;
  }

  .analysis-value {
    font-size: 14px;
    color: #303133;
    font-weight: 600;
  }

  // 时间轴
  .timeline-section {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;

    .section-header h2 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 20px 0;
    }
  }

  .timeline {
    position: relative;
    padding-left: 20px;

    &::before {
      content: '';
      position: absolute;
      left: 8px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #e4e7ed;
    }
  }

  .timeline-item {
    position: relative;
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    &:last-child {
      margin-bottom: 0;
    }

    &.current {
      .timeline-dot {
        background: #409eff;
        box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
      }

      .timeline-title {
        color: #409eff;
        font-weight: 600;
      }
    }
  }

  .timeline-time {
    width: 60px;
    font-size: 12px;
    color: #909399;
    text-align: right;
    margin-right: 20px;
  }

  .timeline-dot {
    width: 8px;
    height: 8px;
    background: #c0c4cc;
    border-radius: 50%;
    position: absolute;
    left: -24px;
    transition: all 0.3s ease;
  }

  .timeline-content {
    flex: 1;
  }

  .timeline-title {
    font-size: 14px;
    color: #303133;
    margin: 0;
  }

  // 响应式设计
  @media (max-width: 768px) {
    .page-header h1 {
      font-size: 20px;
    }

    .stats-grid {
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .stat-card {
      padding: 16px;
      flex-direction: column;
      text-align: center;
      gap: 12px;
    }

    .stat-icon {
      width: 40px;
      height: 40px;
      font-size: 18px;
    }

    .stat-value {
      font-size: 24px;
    }

    .action-buttons {
      flex-direction: column;
    }
  }
}
</style>
