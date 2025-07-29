<template>
  <header class="header">
    <div class="header-content">
      <div class="header-left">
        <div class="logo">
          <el-icon><Clock /></el-icon>
          <span>时迹</span>
        </div>
        <nav class="nav">
          <router-link 
            to="/dashboard" 
            class="nav-item" 
            :class="{ active: $route.path === '/dashboard' }"
          >
            <el-icon><Dashboard /></el-icon>
            仪表板
          </router-link>
          <router-link 
            to="/time-records" 
            class="nav-item"
            :class="{ active: $route.path === '/time-records' }"
          >
            <el-icon><List /></el-icon>
            工时记录
          </router-link>
          <router-link 
            to="/settings" 
            class="nav-item"
            :class="{ active: $route.path === '/settings' }"
          >
            <el-icon><Setting /></el-icon>
            设置
          </router-link>
        </nav>
      </div>
      <div class="header-right">
        <div class="status-indicator">
          <span class="status-dot"></span>
          <span>运行正常</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Clock, Dashboard, List, Setting } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-content {
  width: 100%;
  max-width: 1200px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  
  .el-icon {
    font-size: 24px;
  }
}

.nav {
  display: flex;
  gap: 30px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  text-decoration: none;
  color: #606266;
  border-radius: 4px;
  transition: all 0.3s;
  font-size: 14px;
  
  &:hover {
    background-color: #f5f7fa;
    color: #409eff;
  }
  
  &.active {
    background-color: #409eff;
    color: #fff;
  }
}

.header-right {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #67c23a;
}

.status-dot {
  width: 8px;
  height: 8px;
  background-color: #67c23a;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

// 响应式设计
@media (max-width: 768px) {
  .header {
    padding: 0 12px;
  }

  .header-left {
    gap: 20px;
  }

  .logo {
    font-size: 18px;

    .el-icon {
      font-size: 20px;
    }
  }

  .nav {
    gap: 16px;
  }

  .nav-item {
    padding: 6px 12px;
    font-size: 13px;

    span {
      display: none;
    }
  }

  .status-indicator {
    font-size: 12px;

    span:last-child {
      display: none;
    }
  }
}

@media (max-width: 480px) {
  .header-left {
    gap: 12px;
  }

  .nav {
    gap: 8px;
  }

  .nav-item {
    padding: 4px 8px;
  }
}
</style>
