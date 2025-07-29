<template>
  <div :class="{'show': show}" class="header-search">
    <el-icon class="search-icon" @click.stop="click">
      <Search />
    </el-icon>
    <el-select
      ref="headerSearchSelect"
      v-model="search"
      :remote-method="querySearch"
      filterable
      default-first-option
      remote
      placeholder="搜索页面"
      class="header-search-select"
      @change="change"
    >
      <el-option v-for="option in options" :key="option.item.path" :value="option.item" :label="option.item.title.join(' > ')" />
    </el-select>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()

const search = ref('')
const options = ref([])
const searchPool = ref([])
const show = ref(false)
const headerSearchSelect = ref(null)

const routes = computed(() => router.getRoutes())

const click = () => {
  show.value = !show.value
  if (show.value) {
    headerSearchSelect.value && headerSearchSelect.value.focus()
  }
}

const change = (val) => {
  router.push(val.path)
  search.value = ''
  options.value = []
  nextTick(() => {
    show.value = false
  })
}

const querySearch = (query) => {
  if (query !== '') {
    options.value = searchPool.value.filter(item => {
      return item.item.title.some(title => {
        return title.toLowerCase().indexOf(query.toLowerCase()) > -1
      })
    })
  } else {
    options.value = []
  }
}

// 初始化搜索池
const initPool = () => {
  const pool = []
  routes.value.forEach(route => {
    const title = route.meta && route.meta.title
    if (title) {
      pool.push({
        item: {
          title: [title],
          path: route.path
        }
      })
    }
  })
  searchPool.value = pool
}

watch(routes, initPool, { immediate: true })
</script>

<style lang="scss" scoped>
.header-search {
  font-size: 0 !important;

  .search-icon {
    cursor: pointer;
    font-size: 18px;
    vertical-align: middle;
  }

  .header-search-select {
    font-size: 18px;
    transition: width 0.2s;
    width: 0;
    overflow: hidden;
    background: transparent;
    border-radius: 0;
    display: inline-block;
    vertical-align: middle;

    :deep(.el-input__inner) {
      border-radius: 0;
      border: 0;
      padding-left: 0;
      padding-right: 0;
      box-shadow: none !important;
      border-bottom: 1px solid #d9d9d9;
      vertical-align: middle;
    }
  }

  &.show {
    .header-search-select {
      width: 210px;
      margin-left: 10px;
    }
  }
}
</style>
