/**
 * 论文详情相关的通用工具函数
 */

/**
 * 格式化日期
 * @param {string} dateString 日期字符串
 * @returns {string} 格式化后的日期 YYYY-MM-DD
 */
export function formatDate(dateString) {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    if (isNaN(date)) return dateString
    
    // Format as YYYY-MM-DD
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch (e) {
    console.error('Date formatting error:', e)
    return dateString
  }
}

/**
 * 复制文本到剪贴板
 * @param {string} text 要复制的文本
 * @param {object} proxy Vue实例的proxy对象，用于显示消息提示
 */
export function copyText(text, proxy) {
  if (!text) return
  navigator.clipboard.writeText(text).then(
    () => {
      proxy.$modal.msgSuccess('复制成功')
    },
    (err) => {
      console.error('复制失败:', err)
      proxy.$modal.msgError('复制失败')
    }
  )
}

/**
 * 获取发表状态的类型
 * @param {string} status 发表状态
 * @returns {string} Element UI的tag类型
 */
export function getPublishStatusType(status) {
  if (!status) return 'info'
  switch (status) {
    case '已出版':
      return 'success'
    case '预发表':
      return 'warning'
    case '待发表':
      return 'info'
    case '已撤回':
      return 'danger'
    default:
      return 'info'
  }
}

/**
 * 获取作者姓名首字母
 * @param {string} name 作者姓名
 * @returns {string} 首字母缩写
 */
export function getAuthorInitials(name) {
  if (!name) return '?'
  return name.split(' ')
    .map(part => part.charAt(0).toUpperCase())
    .join('')
    .substring(0, 2)
}

/**
 * 格式化JSON
 * @param {string|object} jsonString JSON字符串或对象
 * @returns {string} 格式化后的JSON字符串
 */
export function formatJSON(jsonString) {
  if (!jsonString) return ''
  try {
    const obj = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return jsonString
  }
} 