<template>
  <el-dropdown trigger="click" @command="handleSetSize">
    <div>
      <el-icon>
        <Operation />
      </el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="large">大号</el-dropdown-item>
        <el-dropdown-item command="default">默认</el-dropdown-item>
        <el-dropdown-item command="small">小号</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { Operation } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const handleSetSize = (size) => {
  appStore.setSize(size)
}
</script>
