<template>
  <div class="time-records">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>工时记录管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增记录
          </el-button>
        </div>
      </template>
      
      <div class="content">
        <p>工时记录功能正在开发中...</p>
        <p>将包含以下功能：</p>
        <ul>
          <li>工时记录的增删改查</li>
          <li>按日期查询记录</li>
          <li>工时统计和分析</li>
          <li>数据导出功能</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const handleAdd = () => {
  ElMessage.info('新增记录功能开发中')
}
</script>

<style lang="scss" scoped>
.time-records {
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
