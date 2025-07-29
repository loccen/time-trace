<template>
  <div class="settings">
    <div class="page-header">
      <h1>系统设置</h1>
    </div>

    <div class="settings-grid">
      <!-- 基本设置 -->
      <div class="settings-section">
        <h2>基本设置</h2>
        <div class="setting-item">
          <label>当前班次:</label>
          <div class="input-group">
            <el-select v-model="settings.currentShift" placeholder="请选择班次">
              <el-option label="标准班次" value="normal" />
              <el-option label="早班" value="early" />
              <el-option label="晚班" value="late" />
              <el-option label="轮班" value="shift" />
            </el-select>
            <el-button @click="showShiftConfig">配置班次</el-button>
          </div>
        </div>
        <div class="setting-item">
          <label>标准工作时长:</label>
          <div class="input-group">
            <el-input-number
              v-model="settings.workHours"
              :min="1"
              :max="24"
              controls-position="right"
            />
            <span>小时</span>
            <el-input-number
              v-model="settings.workMinutes"
              :min="0"
              :max="59"
              controls-position="right"
            />
            <span>分钟</span>
          </div>
        </div>
        <div class="setting-item">
          <label>午休时间:</label>
          <div class="input-group">
            <el-time-picker
              v-model="settings.lunchStart"
              placeholder="开始时间"
              format="HH:mm"
              value-format="HH:mm"
            />
            <span>至</span>
            <el-time-picker
              v-model="settings.lunchEnd"
              placeholder="结束时间"
              format="HH:mm"
              value-format="HH:mm"
            />
          </div>
        </div>
        <div class="setting-item">
          <label>提醒设置:</label>
          <div class="checkbox-group">
            <el-checkbox v-model="settings.workStartReminder">
              启用上班提醒
            </el-checkbox>
            <el-checkbox v-model="settings.workEndReminder">
              启用下班提醒
            </el-checkbox>
            <el-checkbox v-model="settings.overtimeReminder">
              启用加班提醒 (超过 9 小时)
            </el-checkbox>
          </div>
        </div>
      </div>

      <!-- 工作日历设置 -->
      <div class="settings-section">
        <h2>工作日历</h2>
        <div class="setting-item">
          <label>工作日历导入:</label>
          <div class="button-group">
            <el-button @click="importWorkCalendar">导入日历文件</el-button>
            <el-button @click="showCalendarEditor">编辑日历</el-button>
          </div>
        </div>
        <div class="setting-item">
          <label>特殊工作日:</label>
          <div class="special-days">
            <div
              v-for="(day, index) in specialDays"
              :key="index"
              class="special-day-item"
            >
              <span class="day-date">{{ day.date }}</span>
              <el-tag
                :type="day.type === 'holiday' ? 'danger' : 'success'"
                size="small"
              >
                {{ day.label }}
              </el-tag>
              <el-button
                type="danger"
                size="small"
                @click="removeSpecialDay(index)"
                link
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button @click="addSpecialDay" class="add-special-day">
              <el-icon><Plus /></el-icon>
              添加特殊日期
            </el-button>
          </div>
        </div>
        <div class="setting-item">
          <label>工作制度:</label>
          <div class="input-group">
            <el-select v-model="settings.workSchedule" placeholder="请选择工作制度">
              <el-option label="标准工作制 (周一至周五)" value="standard" />
              <el-option label="大小周制" value="big-small-week" />
              <el-option label="单双周制" value="single-double-week" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 高级设置 -->
      <div class="settings-section">
        <h2>高级设置</h2>
        <div class="setting-item">
          <label>数据库路径:</label>
          <div class="input-group">
            <el-input
              v-model="settings.databasePath"
              readonly
              placeholder="数据库路径"
            />
            <el-button @click="browseDatabasePath">浏览</el-button>
          </div>
        </div>
        <div class="setting-item">
          <label>数据管理:</label>
          <div class="button-group">
            <el-button @click="backupData">备份数据</el-button>
            <el-button @click="restoreData">恢复数据</el-button>
            <el-button type="warning" @click="cleanData">清理数据</el-button>
          </div>
        </div>
        <div class="setting-item">
          <label>系统设置:</label>
          <div class="checkbox-group">
            <el-checkbox v-model="settings.autoStart">
              开机自启动
            </el-checkbox>
            <el-checkbox v-model="settings.minimizeToTray">
              最小化到系统托盘
            </el-checkbox>
          </div>
        </div>
      </div>

      <!-- 关于 -->
      <div class="settings-section">
        <h2>关于</h2>
        <div class="about-info">
          <h3>时迹 (TimeTrace) v1.0.0</h3>
          <p>个人工时记录软件</p>

          <div class="system-status">
            <h4>系统状态:</h4>
            <div class="status-item">
              <span class="status-icon success">✅</span>
              <span>事件监听: 正常</span>
            </div>
            <div class="status-item">
              <span class="status-icon success">✅</span>
              <span>数据库: 正常</span>
            </div>
            <div class="status-item">
              <span class="status-icon success">✅</span>
              <span>Web服务: 运行中 (端口: 5000)</span>
            </div>
          </div>

          <div class="button-group">
            <el-button @click="checkUpdate">检查更新</el-button>
            <el-button @click="viewLogs">查看日志</el-button>
            <el-button type="primary" @click="restartService">重启服务</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="settings-actions">
      <el-button type="primary" @click="saveSettings">保存设置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const settings = ref({
  currentShift: 'normal',
  workHours: 8,
  workMinutes: 0,
  lunchStart: '12:00',
  lunchEnd: '13:00',
  workStartReminder: false,
  workEndReminder: false,
  overtimeReminder: true,
  workSchedule: 'standard',
  databasePath: 'C:\\Users\\...\\TimeTrace\\data.db',
  autoStart: true,
  minimizeToTray: true
})

const specialDays = ref([
  {
    date: '2024-02-10',
    type: 'holiday',
    label: '春节调休'
  },
  {
    date: '2024-02-17',
    type: 'workday',
    label: '春节补班'
  }
])

// 方法
const showShiftConfig = () => {
  ElMessage.info('班次配置功能开发中')
}

const importWorkCalendar = () => {
  ElMessage.info('导入日历功能开发中')
}

const showCalendarEditor = () => {
  ElMessage.info('日历编辑功能开发中')
}

const addSpecialDay = () => {
  ElMessage.info('添加特殊日期功能开发中')
}

const removeSpecialDay = (index) => {
  ElMessageBox.confirm(
    '确定要删除这个特殊日期吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    specialDays.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

const browseDatabasePath = () => {
  ElMessage.info('浏览数据库路径功能开发中')
}

const backupData = () => {
  ElMessage.info('备份数据功能开发中')
}

const restoreData = () => {
  ElMessage.info('恢复数据功能开发中')
}

const cleanData = () => {
  ElMessageBox.confirm(
    '确定要清理数据吗？此操作不可恢复！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('数据清理完成')
  }).catch(() => {
    ElMessage.info('已取消清理')
  })
}

const checkUpdate = () => {
  ElMessage.info('检查更新功能开发中')
}

const viewLogs = () => {
  ElMessage.info('查看日志功能开发中')
}

const restartService = () => {
  ElMessageBox.confirm(
    '确定要重启服务吗？',
    '确认重启',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('服务重启中...')
  }).catch(() => {
    ElMessage.info('已取消重启')
  })
}

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}

onMounted(() => {
  // 初始化设置
})
</script>

<style lang="scss" scoped>
.settings {
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

  // 设置网格
  .settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
    margin-bottom: 24px;
  }

  // 设置区块
  .settings-section {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid #e4e7ed;

    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 20px 0;
      padding-bottom: 12px;
      border-bottom: 1px solid #e4e7ed;
    }
  }

  // 设置项
  .setting-item {
    margin-bottom: 20px;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      font-size: 14px;
      color: #606266;
      margin-bottom: 8px;
      font-weight: 500;
    }
  }

  // 输入组
  .input-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    span {
      font-size: 14px;
      color: #606266;
      white-space: nowrap;
    }
  }

  // 按钮组
  .button-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  // 复选框组
  .checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  // 特殊工作日
  .special-days {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .special-day-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    background: #f5f7fa;
    border-radius: 4px;

    .day-date {
      font-size: 14px;
      color: #303133;
      font-weight: 500;
      min-width: 80px;
    }
  }

  .add-special-day {
    align-self: flex-start;
  }

  // 关于信息
  .about-info {
    h3 {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    p {
      font-size: 14px;
      color: #606266;
      margin: 0 0 20px 0;
    }
  }

  .system-status {
    margin: 20px 0;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 12px 0;
    }
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 14px;
    color: #606266;

    .status-icon {
      font-size: 16px;

      &.success {
        color: #67c23a;
      }

      &.warning {
        color: #e6a23c;
      }

      &.error {
        color: #f56c6c;
      }
    }
  }

  // 设置操作
  .settings-actions {
    display: flex;
    justify-content: center;
    padding: 24px 0;
  }

  // 响应式设计
  @media (max-width: 768px) {
    .page-header h1 {
      font-size: 20px;
    }

    .settings-grid {
      grid-template-columns: 1fr;
      gap: 16px;
    }

    .settings-section {
      padding: 16px;
    }

    .input-group {
      flex-direction: column;
      align-items: flex-start;

      .el-select,
      .el-input,
      .el-input-number,
      .el-time-picker {
        width: 100%;
      }

      span {
        margin-top: 4px;
      }
    }

    .button-group {
      flex-direction: column;

      .el-button {
        width: 100%;
      }
    }

    .checkbox-group {
      gap: 12px;
    }

    .special-day-item {
      flex-wrap: wrap;
      gap: 8px;

      .day-date {
        min-width: auto;
        width: 100%;
      }
    }
  }

  @media (max-width: 480px) {
    .settings-section {
      padding: 12px;

      h2 {
        font-size: 16px;
      }
    }

    .setting-item {
      margin-bottom: 16px;

      label {
        font-size: 13px;
      }
    }

    .about-info {
      h3 {
        font-size: 18px;
      }

      p {
        font-size: 13px;
      }
    }

    .system-status {
      h4 {
        font-size: 14px;
      }
    }

    .status-item {
      font-size: 13px;
    }
  }
}
</style>
