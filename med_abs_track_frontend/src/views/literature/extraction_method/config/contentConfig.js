export const tableItem = [
  { prop: 'methodId', label: '方法ID', minWidth: '100' },
  { prop: 'methodName', label: '方法名称', minWidth: '120' },
  { prop: 'methodType', label: '方法类型', minWidth: '100' },
  { prop: 'description', label: '描述', minWidth: '200' },
  { 
    prop: 'templateId', 
    label: '模板', 
    minWidth: '150',
    slotName: 'templateSlot' 
  },
  { 
    prop: 'modelId', 
    label: '模型', 
    minWidth: '150',
    slotName: 'modelSlot' 
  },
  { 
    prop: 'promptId', 
    label: '提示词', 
    minWidth: '150',
    slotName: 'promptSlot' 
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
  },  {
    prop: 'todo',
    label: '操作',
    width: 280,
    fixed: !window.isSmallScreen ? 'right' : false,
    slotName: 'todo',
    showOverflowTooltip: false,
  },]
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
