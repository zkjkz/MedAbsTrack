import { request } from '@/utils/hsj/service/index'

// 查询关键词列表
export function listKeyword(query) {
  return request({
    url: '/literature/keyword/list',
    method: 'get',
    params: query
  })
}

// 查询关键词详细
export function getKeyword(keywordId) {
  return request({
    url: '/literature/keyword/' + keywordId,
    method: 'get'
  })
}

// 新增关键词
export function addKeyword(data) {
  return request({
    url: '/literature/keyword',
    method: 'post',
    data: data
  })
}

// 修改关键词
export function updateKeyword(data) {
  return request({
    url: '/literature/keyword',
    method: 'put',
    data: data
  })
}

// 删除关键词
export function delKeyword(keywordId) {
  return request({
    url: '/literature/keyword/' + keywordId,
    method: 'delete'
  })
}

// 批量新增关键词
export function addBatchKeyword(data) {
  return request({
    url: '/literature/keyword/batch',
    method: 'post',
    data: data
  })
} 