<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎使用时迹工时追踪系统</span>
            </div>
          </template>
          <div class="welcome-content">
            <p>这是一个智能的工时追踪和管理系统，帮助您更好地管理时间和提高工作效率。</p>
            <el-row :gutter="20" class="stats-row">
              <el-col :span="6">
                <div class="stat-item">
                  <el-icon class="stat-icon"><Clock /></el-icon>
                  <div class="stat-content">
                    <div class="stat-value">8.5</div>
                    <div class="stat-label">今日工时</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <el-icon class="stat-icon"><Calendar /></el-icon>
                  <div class="stat-content">
                    <div class="stat-value">42.5</div>
                    <div class="stat-label">本周工时</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <el-icon class="stat-icon"><DataAnalysis /></el-icon>
                  <div class="stat-content">
                    <div class="stat-value">168</div>
                    <div class="stat-label">本月工时</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <el-icon class="stat-icon"><TrendCharts /></el-icon>
                  <div class="stat-content">
                    <div class="stat-value">95%</div>
                    <div class="stat-label">出勤率</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
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
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="system-status">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="API服务">
                <el-tag type="success">正常</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据库">
                <el-tag type="success">连接正常</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="事件监听">
                <el-tag type="warning">已禁用</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="系统版本">
                <el-tag>v1.0.0</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Clock, Calendar, DataAnalysis, TrendCharts, Bell, Setting } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 20px;
}

.welcome-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .welcome-content {
    p {
      margin-bottom: 20px;
      color: #666;
      font-size: 16px;
    }
  }
}

.stats-row {
  margin-top: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  
  .stat-icon {
    font-size: 32px;
    color: #409EFF;
    margin-right: 15px;
  }
  
  .stat-content {
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 5px;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  
  .el-button {
    flex: 1;
    min-width: 120px;
  }
}

.system-status {
  .el-descriptions {
    margin-top: 10px;
  }
}
</style>
