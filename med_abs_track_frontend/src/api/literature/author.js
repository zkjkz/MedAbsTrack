import { request } from '@/utils/hsj/service/index'

// 查询作者列表
export function listAuthor(query) {
  return request({
    url: '/literature/author/list',
    method: 'get',
    params: query
  })
}

// 查询作者详细
export function getAuthor(authorId) {
  return request({
    url: '/literature/author/' + authorId,
    method: 'get'
  })
}

// 新增作者
export function addAuthor(data) {
  return request({
    url: '/literature/author',
    method: 'post',
    data: data
  })
}

// 修改作者
export function updateAuthor(data) {
  return request({
    url: '/literature/author',
    method: 'put',
    data: data
  })
}

// 删除作者
export function delAuthor(authorId) {
  return request({
    url: '/literature/author/' + authorId,
    method: 'delete'
  })
}

// 批量新增作者
export function addBatchAuthor(data) {
  return request({
    url: '/literature/author/batch',
    method: 'post',
    data: data
  })
} 