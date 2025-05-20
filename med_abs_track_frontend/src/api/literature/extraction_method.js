import { request } from '@/utils/hsj/service/index'

// 查询抽取方法配置列表
export function listExtractionMethod(query) {
  return request({
    url: '/literature/extraction_method/list',
    method: 'get',
    params: query
  })
}

// 查询抽取方法配置详细
export function getExtractionMethod(methodId) {
  return request({
    url: '/literature/extraction_method/' + methodId,
    method: 'get'
  })
}

// 新增抽取方法配置
export function addExtractionMethod(data) {
  return request({
    url: '/literature/extraction_method',
    method: 'post',
    data: data
  })
}

// 修改抽取方法配置
export function updateExtractionMethod(data) {
  return request({
    url: '/literature/extraction_method',
    method: 'put',
    data: data
  })
}

// 删除抽取方法配置
export function delExtractionMethod(methodId) {
  return request({
    url: '/literature/extraction_method/' + methodId,
    method: 'delete'
  })
}

// 导出抽取方法配置
export function exportExtractionMethod(query) {
  return request({
    url: '/literature/extraction_method/export',
    method: 'post',
    data: query
  })
}

// 获取可用的抽取模板列表
export function getAvailableTemplates() {
  return request({
    url: '/literature/extraction_method/templates',
    method: 'get'
  })
}

// 获取可用的LLM模型列表
export function getAvailableModels() {
  return request({
    url: '/literature/extraction_method/models',
    method: 'get'
  })
}

// 获取可用的提示词模板列表
export function getAvailablePrompts() {
  return request({
    url: '/literature/extraction_method/prompts',
    method: 'get'
  })
} 

// 修改抽取方法配置状态
export function changeExtractionMethodStatus(methodId, status) {
  const data = {
    methodId,
    status
  }
  return request({
    url: '/literature/extraction_method/changeStatus',
    method: 'put',
    data: data
  })
}