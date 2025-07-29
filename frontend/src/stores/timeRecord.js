import { defineStore } from 'pinia'
import { timeRecordApi } from '@/api'

export const useTimeRecordStore = defineStore('timeRecord', {
  state: () => ({
    // 工时记录列表
    records: [],
    // 当前记录
    currentRecord: null,
    // 分页信息
    pagination: {
      page: 1,
      size: 20,
      total: 0
    },
    // 查询参数
    queryParams: {
      startDate: null,
      endDate: null,
      status: null
    },
    // 加载状态
    loading: false
  }),

  getters: {
    // 今日记录
    todayRecord: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.records.find(record => record.date === today)
    },
    
    // 本周记录
    weekRecords: (state) => {
      const now = new Date()
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
      const weekEnd = new Date(now.setDate(now.getDate() - now.getDay() + 6))
      
      return state.records.filter(record => {
        const recordDate = new Date(record.date)
        return recordDate >= weekStart && recordDate <= weekEnd
      })
    },
    
    // 总工时统计
    totalHours: (state) => {
      return state.records.reduce((total, record) => {
        return total + (record.duration || 0) / 60
      }, 0)
    }
  },

  actions: {
    // 获取工时记录列表
    async fetchRecords(params = {}) {
      try {
        this.loading = true
        const queryParams = {
          ...this.queryParams,
          ...params,
          page: this.pagination.page,
          size: this.pagination.size
        }
        
        const response = await timeRecordApi.getTimeRecords(queryParams)
        
        if (response.success) {
          this.records = response.data.items
          this.pagination.total = response.data.total
          this.pagination.page = response.data.page
          this.pagination.size = response.data.size
        }
        
        return response
      } catch (error) {
        console.error('获取工时记录失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取单个记录
    async fetchRecord(id) {
      try {
        const response = await timeRecordApi.getTimeRecord(id)
        if (response.success) {
          this.currentRecord = response.data
        }
        return response
      } catch (error) {
        console.error('获取工时记录失败:', error)
        throw error
      }
    },

    // 根据日期获取记录
    async fetchRecordByDate(date) {
      try {
        const response = await timeRecordApi.getTimeRecordByDate(date)
        if (response.success) {
          this.currentRecord = response.data
        }
        return response
      } catch (error) {
        console.error('获取工时记录失败:', error)
        throw error
      }
    },

    // 创建记录
    async createRecord(recordData) {
      try {
        const response = await timeRecordApi.createTimeRecord(recordData)
        if (response.success) {
          // 刷新列表
          await this.fetchRecords()
        }
        return response
      } catch (error) {
        console.error('创建工时记录失败:', error)
        throw error
      }
    },

    // 更新记录
    async updateRecord(id, recordData) {
      try {
        const response = await timeRecordApi.updateTimeRecord(id, recordData)
        if (response.success) {
          // 更新当前记录
          if (this.currentRecord && this.currentRecord.id === id) {
            this.currentRecord = response.data
          }
          // 刷新列表
          await this.fetchRecords()
        }
        return response
      } catch (error) {
        console.error('更新工时记录失败:', error)
        throw error
      }
    },

    // 删除记录
    async deleteRecord(id) {
      try {
        const response = await timeRecordApi.deleteTimeRecord(id)
        if (response.success) {
          // 从列表中移除
          this.records = this.records.filter(record => record.id !== id)
          // 清除当前记录
          if (this.currentRecord && this.currentRecord.id === id) {
            this.currentRecord = null
          }
        }
        return response
      } catch (error) {
        console.error('删除工时记录失败:', error)
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
      this.records = []
      this.currentRecord = null
      this.pagination = {
        page: 1,
        size: 20,
        total: 0
      }
      this.queryParams = {
        startDate: null,
        endDate: null,
        status: null
      }
    }
  }
})
