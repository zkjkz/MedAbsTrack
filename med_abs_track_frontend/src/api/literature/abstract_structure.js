import { request } from '@/utils/hsj/service/index'

// 查询摘要结构列表
export function listAbstractStructure(query) {
  return request({
    url: '/literature/abstract_structure/list',
    method: 'get',
    params: query
  })
}

// 查询摘要结构详细
export function getAbstractStructure(abstractId) {
  return request({
    url: '/literature/abstract_structure/' + abstractId,
    method: 'get'
  })
}

// 新增摘要结构
export function addAbstractStructure(data) {
  return request({
    url: '/literature/abstract_structure',
    method: 'post',
    data: data
  })
}

// 修改摘要结构
export function updateAbstractStructure(data) {
  return request({
    url: '/literature/abstract_structure',
    method: 'put',
    data: data
  })
}

// 删除摘要结构
export function delAbstractStructure(abstractIds) {
  return request({
    url: '/literature/abstract_structure/' + abstractIds,
    method: 'delete'
  })
}

// 导出摘要结构列表
export function exportAbstractStructure(data) {
  return request({
    url: '/literature/abstract_structure/export',
    method: 'post',
    data: data
  })
}

// 修改摘要结构状态
export function changeAbstractStructureStatus(data) {
  return request({
    url: '/literature/abstract_structure/changeStatus',
    method: 'put',
    data: data
  })
}

// 根据文章ID获取摘要抽取数据
export function getAbstractStructureByPaperId(paperId) {
  return request({
    url: '/literature/abstract_structure/by-paper/' + paperId,
    method: 'get'
  })
}
