export const tableItem = [
  {
    prop: 'modelId',
    label: '模型ID',
    minWidth: 80,
  },
  {
    prop: 'displayName',
    label: '显示名称',
    minWidth: 120,
  },
  {
    prop: 'modelName',
    label: '模型名称',
    minWidth: 120,
    showOverflowTooltip: true,
  },
  {
    prop: 'modelVersion',
    label: '模型版本',
    minWidth: 100,
  },
  {
    prop: 'provider',
    label: '模型提供商',
    minWidth: 120,
  },
  {
    prop: 'baseUrl',
    label: 'API基础URL',
    minWidth: 150,
    showOverflowTooltip: true,
  },
  {
    prop: 'contextLength',
    label: '上下文长度',
    minWidth: 100,
  },
  {
    prop: 'requestTimeout',
    label: '超时时间(秒)',
    minWidth: 100,
  },
  {
    prop: 'status',
    label: '状态',
    minWidth: 100,
    slotName: 'statusSlot',
  },
  {
    prop: 'remark',
    label: '备注',
    minWidth: 120,
    showOverflowTooltip: true,
  },
  {
    prop: 'updateTime',
    label: '更新时间',
    minWidth: 180,
  },
  {
    prop: 'todo',
    label: '操作',
    width: 280,
    fixed: !window.isSmallScreen ? 'right' : false,
    slotName: 'todo',
    showOverflowTooltip: false,
  },
]
export default () => {
  return {
    tableItem,
    elTableConfig: {
      tooltipOptions: {
        popperClass: 'lmw_popper',
        effect: 'light',
      },
      rowKey: 'modelId',
    },
    showIndex: false,
    showChoose: true,
    pagination: true,
  }
}
