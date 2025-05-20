export default (otherConfig = {}) => {
  return {
    formItems: [
      {
        label: '模板名称',
        field: 'promptName',
        type: 'input',
      },
      {
        label: '创建者',
        field: 'createBy',
        type: 'input',
      },
      {
        label: '创建时间',
        field: 'dateRange',
        type: 'datepicker',
        config: {
          type: 'daterange',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
        },
      },
    ],
    elFormConfig: {},
  }
}
