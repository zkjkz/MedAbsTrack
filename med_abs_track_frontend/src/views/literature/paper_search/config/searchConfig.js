export default (otherConfig = {}) => {
  return {
    formItems: [
      {
        label: '关键词',
        field: 'query',
        type: 'input',
        placeholder: '请输入搜索关键词',
        required: true,
      },
      {
        label: '排序方式',
        field: 'sortBy',
        type: 'select',
        options: [
          { label: '相关性排序', value: 'relevance' },
          { label: '发布日期', value: 'pub_date' },
        ],
        defaultValue: 'relevance',
      },
      {
        label: '发布日期',
        field: 'dateRange',
        type: 'datepicker',
        config: {
          type: 'daterange',
          rangeSeparator: '至',
          startPlaceholder: '开始日期',
          endPlaceholder: '结束日期',
          valueFormat: 'YYYY/MM/DD',
        },
      },
    ],
  }
} 