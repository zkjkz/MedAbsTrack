import { request } from '@/utils/hsj/service/index'

// 查询围手术期相关论文信息列表
export function listPaper(query) {
  return request({
    url: '/literature/paper/list',
    method: 'get',
    params: query
  })
}

// 查询围手术期相关论文信息详细
export function getPaper(paperId) {
  return request({
    url: '/literature/paper/' + paperId,
    method: 'get'
  })
}

// 新增围手术期相关论文信息
export function addPaper(data) {
  return request({
    url: '/literature/paper',
    method: 'post',
    data: data
  })
}

// 修改围手术期相关论文信息
export function updatePaper(data) {
  return request({
    url: '/literature/paper',
    method: 'put',
    data: data
  })
}

// 删除围手术期相关论文信息
export function delPaper(paperId) {
  return request({
    url: '/literature/paper/' + paperId,
    method: 'delete'
  })
}

// 导出围手术期相关论文信息
export function exportPaper(query) {
  return request({
    url: '/literature/paper/export',
    method: 'post',
    data: query
  })
}

// 获取论文已分配的作者列表
export function getPaperAuthorList(paperId) {
  return request({
    url: '/literature/paper/authAuthor/' + paperId,
    method: 'get'
  })
}

// 更新论文作者关联关系
export function updatePaperAuthor(data) {
  return request({
    url: '/literature/paper/authAuthor',
    method: 'put',
    data: data
  })
}

// 获取论文已分配的关键词列表
export function getPaperKeywordList(paperId) {
  return request({
    url: '/literature/paper/authKeyword/' + paperId,
    method: 'get'
  })
}

// 更新论文关键词关联关系
export function updatePaperKeyword(data) {
  return request({
    url: '/literature/paper/authKeyword',
    method: 'put',
    data: data
  })
}
