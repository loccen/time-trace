<template>
  <div class="system-events">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统事件</span>
        </div>
      </template>
      
      <div class="content">
        <p>系统事件功能正在开发中...</p>
        <p>将包含以下功能：</p>
        <ul>
          <li>系统事件列表查看</li>
          <li>事件状态管理</li>
          <li>事件统计分析</li>
          <li>事件日志导出</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 系统事件页面
</script>

<style lang="scss" scoped>
.system-events {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .content {
    padding: 20px;
    
    ul {
      margin-top: 10px;
      padding-left: 20px;
      
      li {
        margin-bottom: 8px;
        color: #666;
      }
    }
  }
}
</style>
