<template>
  <div class="settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <div class="content">
        <p>系统设置功能正在开发中...</p>
        <p>将包含以下功能：</p>
        <ul>
          <li>工作时间配置</li>
          <li>事件监听设置</li>
          <li>系统参数配置</li>
          <li>用户偏好设置</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 系统设置页面
</script>

<style lang="scss" scoped>
.settings {
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
