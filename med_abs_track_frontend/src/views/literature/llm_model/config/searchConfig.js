export default (otherConfig = {}) => {
  return {
    formItems: [
      {
        label: '显示名称',
        field: 'displayName',
        type: 'input',
        config: {
          placeholder: '请输入显示名称',
          clearable: true
        }
      },
      {
        label: '模型名称',
        field: 'modelName',
        type: 'input',
        config: {
          placeholder: '请输入模型名称',
          clearable: true
        }
      },
      {
        label: '模型提供商',
        field: 'provider',
        type: 'input',
        config: {
          placeholder: '请输入模型提供商',
          clearable: true
        }
      },
      {
        label: '状态',
        field: 'status',
        type: 'select',
        config: {
          placeholder: '请选择状态',
          clearable: true,
          options: [
            { label: '正常', value: '0' },
            { label: '停用', value: '1' }
          ]
        }
      },
      {
        label: '创建时间',
        field: 'dateRange',
        type: 'datepicker',
        config: {
          type: 'daterange',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
          startPlaceholder: '开始日期',
          endPlaceholder: '结束日期',
          clearable: true
        },
      },
    ],
    elFormConfig: {},
  }
}
