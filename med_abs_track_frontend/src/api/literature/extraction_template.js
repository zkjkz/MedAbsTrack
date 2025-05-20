import { request } from '@/utils/hsj/service/index'

// 查询摘要抽取模板列表
export function listExtraction_template(query) {
  return request({
    url: '/literature/extraction_template/list',
    method: 'get',
    params: query
  })
}

// 查询摘要抽取模板详细
export function getExtraction_template(templateId) {
  return request({
    url: '/literature/extraction_template/' + templateId,
    method: 'get'
  })
}

// 新增摘要抽取模板
export function addExtraction_template(data) {
  return request({
    url: '/literature/extraction_template',
    method: 'post',
    data: data
  })
}

// 修改摘要抽取模板
export function updateExtraction_template(data) {
  return request({
    url: '/literature/extraction_template',
    method: 'put',
    data: data
  })
}

// 删除摘要抽取模板
export function delExtraction_template(templateId) {
  return request({
    url: '/literature/extraction_template/' + templateId,
    method: 'delete'
  })
}

// 导出摘要抽取模板列表
export function exportExtraction_template(data) {
  return request({
    url: '/literature/extraction_template/export',
    method: 'post',
    data: data
  })
}

// 修改摘要抽取模板状态
export function changeExtractionTemplateStatus(templateId, status) {
  const data = {
    templateId,
    status
  }
  return request({
    url: '/literature/extraction_template/changeStatus',
    method: 'put',
    data: data
  })
}
