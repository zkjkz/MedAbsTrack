import { request } from '@/utils/hsj/service/index'

// 查询抽取任务列表
export function listExtractionTask(query) {
  return request({
    url: '/literature/extraction_task/list',
    method: 'get',
    params: query
  })
}

// 查询抽取任务详细
export function getExtractionTask(taskId) {
  return request({
    url: '/literature/extraction_task/' + taskId,
    method: 'get'
  })
}

// 新增抽取任务
export function addExtractionTask(data) {
  return request({
    url: '/literature/extraction_task',
    method: 'post',
    data: data
  })
}

// 修改抽取任务
export function updateExtractionTask(data) {
  return request({
    url: '/literature/extraction_task',
    method: 'put',
    data: data
  })
}

// 删除抽取任务
export function delExtractionTask(taskIds) {
  return request({
    url: '/literature/extraction_task/' + taskIds,
    method: 'delete'
  })
}

// 导出抽取任务
export function exportExtractionTask(query) {
  return request({
    url: '/literature/extraction_task/export',
    method: 'post',
    data: query
  })
}

// 更新任务论文关联关系
export function updateTaskPaper(data) {
  return request({
    url: '/literature/extraction_task/authPaper',
    method: 'put',
    params: data
  })
}

// 执行抽取任务
export function executeExtraction(data) {
  return request({
    url: '/literature/extraction_task/extract',
    method: 'post',
    data: data
  })
}
