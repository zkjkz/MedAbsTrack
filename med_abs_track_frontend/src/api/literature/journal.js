import { request } from '@/utils/hsj/service/index'

// 查询期刊列表
export function listJournal(query) {
  return request({
    url: '/literature/journal/list',
    method: 'get',
    params: query
  })
}

// 查询期刊详细
export function getJournal(journalId) {
  return request({
    url: '/literature/journal/' + journalId,
    method: 'get'
  })
}

// 新增期刊
export function addJournal(data) {
  return request({
    url: '/literature/journal',
    method: 'post',
    data: data
  })
}

// 修改期刊
export function updateJournal(data) {
  return request({
    url: '/literature/journal',
    method: 'put',
    data: data
  })
}

// 删除期刊
export function delJournal(journalId) {
  return request({
    url: '/literature/journal/' + journalId,
    method: 'delete'
  })
} 