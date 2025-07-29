<template>
  <div @click="click">
    <el-icon>
      <FullScreen />
    </el-icon>
  </div>
</template>

<script setup>
import { FullScreen } from '@element-plus/icons-vue'

const click = () => {
  // TODO: 实现全屏功能
  console.log('全屏功能待实现')
}
</script>
