export default (otherConfig = {}) => {
  return {
    formItems: [
      {
        label: '论文标题',
        field: 'title',
        type: 'input',
      },
      {
        label: 'PubMed ID',
        field: 'pmid',
        type: 'input',
      },
      {
        label: 'DOI',
        field: 'doi',
        type: 'input',
      },
      {
        label: '期刊ID',
        field: 'journal_id',
        type: 'input',
      },
      {
        label: '状态',
        field: 'status',
        type: 'select',
        config: {
          options: [
            { label: '预发表', value: '0' },
            { label: '已出版', value: '1' },
          ],
          clearable: true,
        },
      },
      {
        label: '发表日期',
        field: 'published_date_range',
        type: 'datepicker',
        config: {
          type: 'daterange',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
          rangeSeparator: '至',
          startPlaceholder: '开始日期',
          endPlaceholder: '结束日期',
        },
      },
      {
        label: '创建时间',
        field: 'dateRange',
        type: 'datepicker',
        config: {
          type: 'daterange',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
          rangeSeparator: '至',
          startPlaceholder: '开始日期',
          endPlaceholder: '结束日期',
        },
      },
    ],
    elFormConfig: {},
  }
}
