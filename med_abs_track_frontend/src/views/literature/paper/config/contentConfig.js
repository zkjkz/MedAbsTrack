export const tableItem = [
  {
    prop: 'paperId',
    label: '论文ID',
    minWidth: 80,
  },
  {
    prop: 'pmid',
    label: 'PubMed ID',
    minWidth: 100,
  },
  {
    prop: 'title',
    label: '论文标题',
    minWidth: 180,
    showOverflowTooltip: true,
  },
  {
    prop: 'doi',
    label: 'DOI',
    minWidth: 120,
    showOverflowTooltip: true,
  },
  {
    prop: 'abstract',
    label: '论文摘要',
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
    prop: 'publishedDate',
    label: '发表日期',
    minWidth: 110,
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
      rowKey: 'paper_id',
    },
    showIndex: false,
    showChoose: true,
    pagination: true,
  }
}
