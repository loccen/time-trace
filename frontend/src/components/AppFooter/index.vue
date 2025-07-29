<template>
  <footer class="footer">
    <div class="footer-left">
      <span>最后更新时间: {{ lastUpdateTime }}</span>
    </div>
    <div class="footer-right">
      <span>数据库状态: {{ databaseStatus }}</span>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'

const lastUpdateTime = ref('')
const databaseStatus = ref('正常')

// 更新时间
const updateTime = () => {
  lastUpdateTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  updateTime()
  // 每分钟更新一次时间
  setInterval(updateTime, 60000)
})
</script>

<style lang="scss" scoped>
.footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  padding: 0 20px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  font-size: 12px;
  color: #909399;
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
}
</style>
