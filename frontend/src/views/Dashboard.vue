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
  </div>
</template>

<script setup>
import { Clock, Calendar, TrendCharts, DataAnalysis, Bell, Setting } from '@element-plus/icons-vue'
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
