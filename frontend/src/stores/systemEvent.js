import { defineStore } from 'pinia'
import { systemEventApi } from '@/api'

export const useSystemEventStore = defineStore('systemEvent', {
  state: () => ({
    // 系统事件列表
    events: [],
    // 当前事件
    currentEvent: null,
    // 分页信息
    pagination: {
      page: 1,
      size: 50,
      total: 0
    },
    // 查询参数
    queryParams: {
      eventType: null,
      startTime: null,
      endTime: null,
      processed: null
    },
    // 加载状态
    loading: false,
    // 统计信息
    statistics: null
  }),

  getters: {
    // 未处理事件数量
    unprocessedCount: (state) => {
      return state.events.filter(event => !event.processed).length
    },
    
    // 今日事件
    todayEvents: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.events.filter(event => {
        return event.event_time.startsWith(today)
      })
    },
    
    // 按类型分组的事件
    eventsByType: (state) => {
      const grouped = {}
      state.events.forEach(event => {
        if (!grouped[event.event_type]) {
          grouped[event.event_type] = []
        }
        grouped[event.event_type].push(event)
      })
      return grouped
    }
  },

  actions: {
    // 获取系统事件列表
    async fetchEvents(params = {}) {
      try {
        this.loading = true
        const queryParams = {
          ...this.queryParams,
          ...params,
          page: this.pagination.page,
          size: this.pagination.size
        }
        
        const response = await systemEventApi.getSystemEvents(queryParams)
        
        if (response.success) {
          this.events = response.data.items
          this.pagination.total = response.data.total
          this.pagination.page = response.data.page
          this.pagination.size = response.data.size
        }
        
        return response
      } catch (error) {
        console.error('获取系统事件失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取单个事件
    async fetchEvent(id) {
      try {
        const response = await systemEventApi.getSystemEvent(id)
        if (response.success) {
          this.currentEvent = response.data
        }
        return response
      } catch (error) {
        console.error('获取系统事件失败:', error)
        throw error
      }
    },

    // 创建事件
    async createEvent(eventData) {
      try {
        const response = await systemEventApi.createSystemEvent(eventData)
        if (response.success) {
          // 刷新列表
          await this.fetchEvents()
        }
        return response
      } catch (error) {
        console.error('创建系统事件失败:', error)
        throw error
      }
    },

    // 标记事件为已处理
    async markEventProcessed(id) {
      try {
        const response = await systemEventApi.markEventProcessed(id)
        if (response.success) {
          // 更新本地状态
          const event = this.events.find(e => e.id === id)
          if (event) {
            event.processed = true
          }
          if (this.currentEvent && this.currentEvent.id === id) {
            this.currentEvent.processed = true
          }
        }
        return response
      } catch (error) {
        console.error('标记事件处理状态失败:', error)
        throw error
      }
    },

    // 批量标记事件为已处理
    async markEventsProcessedBatch(eventIds) {
      try {
        const response = await systemEventApi.markEventsProcessedBatch(eventIds)
        if (response.success) {
          // 更新本地状态
          this.events.forEach(event => {
            if (eventIds.includes(event.id)) {
              event.processed = true
            }
          })
        }
        return response
      } catch (error) {
        console.error('批量标记事件处理状态失败:', error)
        throw error
      }
    },

    // 获取未处理事件
    async fetchUnprocessedEvents(limit = 50) {
      try {
        const response = await systemEventApi.getUnprocessedEvents(limit)
        return response
      } catch (error) {
        console.error('获取未处理事件失败:', error)
        throw error
      }
    },

    // 获取最近事件
    async fetchRecentEvents(limit = 20) {
      try {
        const response = await systemEventApi.getRecentEvents(limit)
        return response
      } catch (error) {
        console.error('获取最近事件失败:', error)
        throw error
      }
    },

    // 获取事件统计
    async fetchEventStatistics(params = {}) {
      try {
        const response = await systemEventApi.getEventStatistics(params)
        if (response.success) {
          this.statistics = response.data
        }
        return response
      } catch (error) {
        console.error('获取事件统计失败:', error)
        throw error
      }
    },

    // 设置查询参数
    setQueryParams(params) {
      this.queryParams = { ...this.queryParams, ...params }
    },

    // 设置分页
    setPagination(pagination) {
      this.pagination = { ...this.pagination, ...pagination }
    },

    // 重置状态
    resetState() {
      this.events = []
      this.currentEvent = null
      this.pagination = {
        page: 1,
        size: 50,
        total: 0
      }
      this.queryParams = {
        eventType: null,
        startTime: null,
        endTime: null,
        processed: null
      }
      this.statistics = null
    }
  }
})
