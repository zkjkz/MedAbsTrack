import { request } from '@/utils/hsj/service/index'

// 查询大语言模型基座列表
export function listLlm_model(query) {
  return request({
    url: '/literature/llm_model/list',
    method: 'get',
    params: query
  })
}

// 查询大语言模型基座详细
export function getLlm_model(modelId) {
  return request({
    url: '/literature/llm_model/' + modelId,
    method: 'get'
  })
}

// 新增大语言模型基座
export function addLlm_model(data) {
  return request({
    url: '/literature/llm_model',
    method: 'post',
    data: data
  })
}

// 修改大语言模型基座
export function updateLlm_model(data) {
  return request({
    url: '/literature/llm_model',
    method: 'put',
    data: data
  })
}

// 删除大语言模型基座
export function delLlm_model(modelId) {
  return request({
    url: '/literature/llm_model/' + modelId,
    method: 'delete'
  })
}

// 导出大语言模型基座列表
export function exportLlm_model(data) {
  return request({
    url: '/literature/llm_model/export',
    method: 'post',
    data: data
  })
}

// 修改大语言模型基座状态
export function changeLlm_modelStatus(modelId, status) {
  const data = {
    modelId,
    status
  }
  return request({
    url: '/literature/llm_model/changeStatus',
    method: 'put',
    data: data
  })
}
