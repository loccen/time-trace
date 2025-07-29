<template>
  <div class="time-records">
    <div class="page-header">
      <h1>工时记录管理</h1>
      <div class="page-actions">
        <div class="view-toggle">
          <el-button
            :type="currentView === 'table' ? 'primary' : 'default'"
            @click="currentView = 'table'"
          >
            <el-icon><Grid /></el-icon>
            表格视图
          </el-button>
          <el-button
            :type="currentView === 'calendar' ? 'primary' : 'default'"
            @click="currentView = 'calendar'"
          >
            <el-icon><Calendar /></el-icon>
            日历视图
          </el-button>
        </div>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增记录
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <div class="filter-group">
        <label>日期范围:</label>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </div>
      <div class="filter-group">
        <label>状态:</label>
        <el-select v-model="statusFilter" placeholder="请选择状态">
          <el-option label="全部" value="" />
          <el-option label="正常" value="normal" />
          <el-option label="异常" value="abnormal" />
          <el-option label="手动" value="manual" />
        </el-select>
      </div>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <!-- 表格视图 -->
    <div v-show="currentView === 'table'" class="table-view">
      <div class="table-section">
        <el-table :data="tableData" style="width: 100%" v-loading="loading">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="clockIn" label="上班时间" width="120" />
          <el-table-column prop="clockOut" label="下班时间" width="120" />
          <el-table-column prop="workHours" label="实际工时" width="120" />
          <el-table-column prop="idleTime" label="摸鱼时长" width="120" />
          <el-table-column prop="meetingTime" label="会议时长" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag
                :type="getStatusType(scope.row.status)"
                size="small"
              >
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click="handleEdit(scope.row)"
                link
              >
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button
                type="warning"
                size="small"
                @click="handleTag(scope.row)"
                link
              >
                <el-icon><PriceTag /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 日历视图 -->
    <div v-show="currentView === 'calendar'" class="calendar-view">
      <div class="calendar-header">
        <el-button @click="prevMonth">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h3>{{ currentMonthText }}</h3>
        <el-button @click="nextMonth">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="calendar-grid">
        <div class="calendar-weekdays">
          <div class="weekday">周日</div>
          <div class="weekday">周一</div>
          <div class="weekday">周二</div>
          <div class="weekday">周三</div>
          <div class="weekday">周四</div>
          <div class="weekday">周五</div>
          <div class="weekday">周六</div>
        </div>
        <div class="calendar-days">
          <div
            v-for="day in calendarDays"
            :key="day.date"
            class="calendar-day"
            :class="{
              'other-month': day.otherMonth,
              'has-record': day.hasRecord,
              'today': day.isToday
            }"
          >
            <div class="day-number">{{ day.day }}</div>
            <div v-if="day.workHours" class="day-hours">{{ day.workHours }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-show="currentView === 'table'" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Plus, Download, Grid, Calendar, Edit, PriceTag,
  ArrowLeft, ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { timeRecordApi } from '@/api/timeRecord'

// 响应式数据
const currentView = ref('table')
const dateRange = ref([dayjs().subtract(30, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const currentMonth = ref(dayjs())
const loading = ref(false)

// 表格数据
const tableData = ref([])

// 格式化工时显示
const formatDuration = (minutes) => {
  if (!minutes || minutes === 0) return '--'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
}

// 格式化时间显示
const formatTime = (datetime) => {
  if (!datetime) return '--:--:--'
  return dayjs(datetime).format('HH:mm:ss')
}

// 加载工时记录数据
const loadTimeRecords = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      status: statusFilter.value || undefined,
      page: currentPage.value,
      size: pageSize.value
    }

    const response = await timeRecordApi.getTimeRecords(params)
    if (response.success) {
      const data = response.data

      // 转换数据格式
      tableData.value = data.items.map(record => ({
        id: record.id,
        date: record.date,
        clockIn: formatTime(record.clock_in),
        clockOut: formatTime(record.clock_out),
        workHours: formatDuration(record.duration),
        idleTime: formatDuration(record.break_duration),
        meetingTime: '--', // 暂时没有会议时间数据
        status: record.status
      }))

      total.value = data.total
    }
  } catch (error) {
    console.error('加载工时记录失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 计算属性
const currentMonthText = computed(() => {
  return currentMonth.value.format('YYYY年M月')
})

const calendarDays = computed(() => {
  const startOfMonth = currentMonth.value.startOf('month')
  const endOfMonth = currentMonth.value.endOf('month')
  const startOfCalendar = startOfMonth.startOf('week')
  const endOfCalendar = endOfMonth.endOf('week')

  const days = []
  let current = startOfCalendar

  while (current.isBefore(endOfCalendar) || current.isSame(endOfCalendar)) {
    const isCurrentMonth = current.isSame(currentMonth.value, 'month')
    const isToday = current.isSame(dayjs(), 'day')

    days.push({
      date: current.format('YYYY-MM-DD'),
      day: current.date(),
      otherMonth: !isCurrentMonth,
      isToday,
      hasRecord: isCurrentMonth && Math.random() > 0.7, // 模拟数据
      workHours: isCurrentMonth && Math.random() > 0.7 ? '8h' : null
    })

    current = current.add(1, 'day')
  }

  return days
})

// 方法
const getStatusType = (status) => {
  const types = {
    normal: 'success',
    abnormal: 'danger',
    manual: 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    normal: '正常',
    abnormal: '异常',
    manual: '手动'
  }
  return texts[status] || '未知'
}

const handleAdd = () => {
  ElMessage.info('新增记录功能开发中')
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

const handleSearch = () => {
  currentPage.value = 1
  loadTimeRecords()
}

const handleEdit = (row) => {
  ElMessage.info(`编辑记录: ${row.date}`)
}

const handleTag = (row) => {
  ElMessage.info(`时间标记: ${row.date}`)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadTimeRecords()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadTimeRecords()
}

const prevMonth = () => {
  currentMonth.value = currentMonth.value.subtract(1, 'month')
}

const nextMonth = () => {
  currentMonth.value = currentMonth.value.add(1, 'month')
}

onMounted(() => {
  loadTimeRecords()
})
</script>

<style lang="scss" scoped>
.time-records {
  // 页面头部
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h1 {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .page-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .view-toggle {
    display: flex;
    gap: 0;
    border-radius: 4px;
    overflow: hidden;

    .el-button {
      border-radius: 0;

      &:first-child {
        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
      }

      &:last-child {
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
      }
    }
  }

  // 筛选区域
  .filter-section {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }

  .filter-group {
    display: flex;
    align-items: center;
    gap: 8px;

    label {
      font-size: 14px;
      color: #606266;
      white-space: nowrap;
    }
  }

  // 表格视图
  .table-view {
    margin-bottom: 20px;
  }

  .table-section {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;
  }

  // 日历视图
  .calendar-view {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;
    margin-bottom: 20px;
  }

  .calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .calendar-grid {
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    overflow: hidden;
  }

  .calendar-weekdays {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: #fafbfc;

    .weekday {
      padding: 12px;
      text-align: center;
      font-size: 14px;
      font-weight: 600;
      color: #606266;
      border-right: 1px solid #e4e7ed;

      &:last-child {
        border-right: none;
      }
    }
  }

  .calendar-days {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
  }

  .calendar-day {
    min-height: 80px;
    padding: 8px;
    border-right: 1px solid #e4e7ed;
    border-bottom: 1px solid #e4e7ed;
    position: relative;

    &:nth-child(7n) {
      border-right: none;
    }

    &.other-month {
      background: #fafbfc;
      color: #c0c4cc;
    }

    &.today {
      background: #f0f9ff;

      .day-number {
        color: #409eff;
        font-weight: 600;
      }
    }

    &.has-record {
      background: #f0f9ff;
    }
  }

  .day-number {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .day-hours {
    font-size: 12px;
    color: #67c23a;
    background: #f0f9ff;
    padding: 2px 6px;
    border-radius: 4px;
    text-align: center;
  }

  // 分页
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }

  // 响应式设计
  @media (max-width: 768px) {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;

      h1 {
        font-size: 20px;
      }
    }

    .page-actions {
      width: 100%;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }

    .view-toggle {
      order: -1;
      width: 100%;

      .el-button {
        flex: 1;
      }
    }

    .filter-section {
      padding: 16px;
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }

    .filter-group {
      width: 100%;
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;

      .el-date-picker,
      .el-select {
        width: 100%;
      }
    }

    .calendar-days {
      font-size: 12px;
    }

    .calendar-day {
      min-height: 60px;
      padding: 4px;
    }

    .day-hours {
      font-size: 10px;
      padding: 1px 4px;
    }
  }

  @media (max-width: 480px) {
    .page-actions {
      flex-direction: column;

      .el-button {
        width: 100%;
      }
    }

    .calendar-day {
      min-height: 50px;
      padding: 2px;
    }

    .day-number {
      font-size: 12px;
    }

    .calendar-weekdays .weekday {
      padding: 8px 4px;
      font-size: 12px;
    }
  }
}
</style>
