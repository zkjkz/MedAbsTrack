export const tableItem = [
  {
    prop: 'promptId',
    label: '模板ID',
    minWidth: 80,
  },
  {
    prop: 'promptName',
    label: '模板名称',
    minWidth: 120,
  },
  {
    prop: 'description',
    label: '描述',
    minWidth: 150,
    showOverflowTooltip: true,
  },
  {
    prop: 'promptContent',
    label: '模板内容',
    showOverflowTooltip: true,
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
    minWidth: 150,
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
      rowKey: 'promptId',
    },
    showIndex: false,
    showChoose: true,
    pagination: true,
    selectionConfig: {
      selectable: (item) => {
        return item.promptId !== 1
      },
    },
  }
}
