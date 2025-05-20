export const tableItem = [
  {
    prop: 'templateId',
    label: '模板ID',
    minWidth: 80,
  },
  {
    prop: 'templateName',
    label: '模板名称',
    minWidth: 120,
  },
  {
    prop: 'description',
    label: '模板描述',
    minWidth: 200,
    showOverflowTooltip: true,
  },
  {
    prop: 'templateContent',
    label: '模板内容',
    minWidth: 200,
    showOverflowTooltip: true,
  },
  {
    prop: 'remark',
    label: '备注',
    minWidth: 150,
    showOverflowTooltip: true,
  },
  {
    prop: 'status',
    label: '状态',
    minWidth: 100,
    slotName: 'statusSlot',
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
      rowKey: 'templateId',
    },
    showIndex: false,
    showChoose: true,
    pagination: true,
    selectionConfig: {
      selectable: (item) => {
        return item.templateId !== 1
      },
    },
  }
}
