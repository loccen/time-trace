import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: '/api', // 基础URL，会被vite代理到后端
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加请求时间戳
    config.metadata = { startTime: new Date() }

    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 计算请求耗时
    const endTime = new Date()
    const duration = endTime - response.config.metadata.startTime
    console.log(`API请求耗时: ${duration}ms - ${response.config.url}`)

    const { data } = response

    // 检查业务状态码
    if (data.success === false) {
      // 业务错误
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }

    return data
  },
  (error) => {
    console.error('响应拦截器错误:', error)

    // 处理HTTP错误状态码
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          ElMessage.error(data.message || '请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请重新登录')
          // 清除token并跳转到登录页
          localStorage.removeItem('access_token')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422:
          ElMessage.error(data.message || '数据验证失败')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        case 502:
          ElMessage.error('网关错误')
          break
        case 503:
          ElMessage.error('服务不可用')
          break
        case 504:
          ElMessage.error('网关超时')
          break
        default:
          ElMessage.error(data.message || `请求失败 (${status})`)
      }
    } else if (error.request) {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      // 其他错误
      ElMessage.error(error.message || '请求失败')
    }

    return Promise.reject(error)
  }
)

// 封装常用的请求方法
export const http = {
  // GET请求
  get(url, params = {}, config = {}) {
    return request({
      method: 'GET',
      url,
      params,
      ...config
    })
  },

  // POST请求
  post(url, data = {}, config = {}) {
    return request({
      method: 'POST',
      url,
      data,
      ...config
    })
  },

  // PUT请求
  put(url, data = {}, config = {}) {
    return request({
      method: 'PUT',
      url,
      data,
      ...config
    })
  },

  // DELETE请求
  delete(url, config = {}) {
    return request({
      method: 'DELETE',
      url,
      ...config
    })
  },

  // PATCH请求
  patch(url, data = {}, config = {}) {
    return request({
      method: 'PATCH',
      url,
      data,
      ...config
    })
  },

  // 上传文件
  upload(url, formData, config = {}) {
    return request({
      method: 'POST',
      url,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },

  // 下载文件
  download(url, params = {}, filename = '') {
    return request({
      method: 'GET',
      url,
      params,
      responseType: 'blob'
    }).then(response => {
      // 创建下载链接
      const blob = new Blob([response])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

export default request
