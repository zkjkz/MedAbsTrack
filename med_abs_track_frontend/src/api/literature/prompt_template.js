import { request } from '@/utils/hsj/service/index'

// 查询Prompt模板列表
export function listPrompt_template(query) {
  return request({
    url: '/literature/prompt_template/list',
    method: 'get',
    params: query
  })
}

// 查询Prompt模板详细
export function getPrompt_template(promptId) {
  return request({
    url: '/literature/prompt_template/' + promptId,
    method: 'get'
  })
}

// 新增Prompt模板
export function addPrompt_template(data) {
  return request({
    url: '/literature/prompt_template',
    method: 'post',
    data: data
  })
}

// 修改Prompt模板
export function updatePrompt_template(data) {
  return request({
    url: '/literature/prompt_template',
    method: 'put',
    data: data
  })
}

// 删除Prompt模板
export function delPrompt_template(promptId) {
  return request({
    url: '/literature/prompt_template/' + promptId,
    method: 'delete'
  })
}

// 导出Prompt模板列表
export function exportPrompt_template(data) {
  return request({
    url: '/literature/prompt_template/export',
    method: 'post',
    data: data
  })
}

// 修改Prompt模板状态
export function changePrompt_templateStatus(promptId, status) {
  const data = {
    promptId,
    status
  }
  return request({
    url: '/literature/prompt_template/changeStatus',
    method: 'put',
    data: data
  })
}
