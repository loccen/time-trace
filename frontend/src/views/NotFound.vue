<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="not-found-content">
        <h1 class="error-code">404</h1>
        <h2 class="error-title">页面不存在</h2>
        <p class="error-description">抱歉，您访问的页面不存在或已被删除。</p>
        <div class="error-actions">
          <el-button type="primary" @click="goHome">
            <el-icon><HomeFilled /></el-icon>
            返回首页
          </el-button>
          <el-button @click="goBack">
            <el-icon><Back /></el-icon>
            返回上页
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { HomeFilled, Back } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;

  .not-found-container {
    text-align: center;
    padding: 40px;

    .not-found-content {
      .error-code {
        font-size: 120px;
        font-weight: bold;
        color: #409EFF;
        margin: 0;
        line-height: 1;
      }

      .error-title {
        font-size: 32px;
        color: #303133;
        margin: 20px 0 10px;
      }

      .error-description {
        font-size: 16px;
        color: #606266;
        margin-bottom: 30px;
      }

      .error-actions {
        .el-button {
          margin: 0 10px;
        }
      }
    }
  }
}
</style>
