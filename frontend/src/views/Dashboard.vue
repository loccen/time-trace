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
          <div class="stat-value">8h 30m</div>
          <div class="stat-label">今日工时</div>
          <div class="stat-status working">🕐 正在工作</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">42h 15m</div>
          <div class="stat-label">本周工时</div>
          <div class="stat-status positive">📊 +5.2%</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">168h 45m</div>
          <div class="stat-label">本月工时</div>
          <div class="stat-status positive">📈 +12.8%</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">8h 15m</div>
          <div class="stat-label">平均工时</div>
          <div class="stat-status stable">📊 稳定</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">25h 30m</div>
          <div class="stat-label">本月加班</div>
          <div class="stat-status warning">⚠️ 偏高</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">18h 45m</div>
          <div class="stat-label">上月加班</div>
          <div class="stat-status positive">📉 -27%</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>每日工时柱状图</h3>
        <div class="chart-placeholder bar-chart">
          <div class="bar-container">
            <div class="bar" style="height: 60%;" data-value="7.5h" data-hours="7.5"></div>
            <div class="bar overtime" style="height: 82%;" data-value="8.2h" data-hours="8.2"></div>
            <div class="bar" style="height: 70%;" data-value="7.8h" data-hours="7.8"></div>
            <div class="bar overtime" style="height: 90%;" data-value="8.5h" data-hours="8.5"></div>
            <div class="bar" style="height: 80%;" data-value="8.0h" data-hours="8.0"></div>
            <div class="bar overtime" style="height: 85%;" data-value="8.3h" data-hours="8.3"></div>
            <div class="bar" style="height: 65%;" data-value="7.2h" data-hours="7.2"></div>
          </div>
          <div class="chart-labels">
            <span>周一</span>
            <span>周二</span>
            <span>周三</span>
            <span>周四</span>
            <span>周五</span>
            <span>周六</span>
            <span>周日</span>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <h3>工时分布饼图</h3>
        <div class="chart-placeholder pie-chart">
          <div class="pie-segment"></div>
        </div>
        <div class="pie-legend">
          <div class="legend-item">
            <span class="legend-color" style="background: #409EFF;"></span>
            <span>8-9小时 (45%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #67C23A;"></span>
            <span>7-8小时 (25%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #E6A23C;"></span>
            <span>9-10小时 (20%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #F56C6C;"></span>
            <span>其他 (10%)</span>
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
          <span class="analysis-value">09:00 (占比 68%)</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">最常见下班时间:</span>
          <span class="analysis-value">18:30 (占比 45%)</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">平均午休时长:</span>
          <span class="analysis-value">1小时15分钟</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">加班频率:</span>
          <span class="analysis-value">15% (超过9小时的工作日)</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">工作效率最高时段:</span>
          <span class="analysis-value">上午 10:00-12:00</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">平均通勤时间:</span>
          <span class="analysis-value">45分钟</span>
        </div>
      </div>
    </div>

    <!-- 今日时间轴 -->
    <div class="timeline-section">
      <div class="section-header">
        <h2>今日时间轴</h2>
      </div>
      <div class="timeline">
        <div class="timeline-item">
          <div class="timeline-time">09:00</div>
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <div class="timeline-title">上班打卡</div>
          </div>
        </div>
        <div class="timeline-item">
          <div class="timeline-time">12:00</div>
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <div class="timeline-title">午休开始</div>
          </div>
        </div>
        <div class="timeline-item">
          <div class="timeline-time">13:00</div>
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <div class="timeline-title">午休结束</div>
          </div>
        </div>
        <div class="timeline-item current">
          <div class="timeline-time">15:30</div>
          <div class="timeline-dot current"></div>
          <div class="timeline-content">
            <div class="timeline-title">当前时间</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Clock, Calendar, TrendCharts, DataAnalysis, Bell, Setting, Timer } from '@element-plus/icons-vue'
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
