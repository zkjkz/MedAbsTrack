export default (listeners = {}) => {
  return {
    rules: {
      title: [
        { required: true, message: '论文标题不能为空', trigger: 'blur' },
        {
          min: 2,
          max: 300,
          message: '论文标题长度必须介于 2 和 300 之间',
          trigger: 'blur',
        },
      ],
      journal_id: [
        { required: false, message: '期刊ID不能为空', trigger: 'blur' },
      ],
    },
    formItems: [
      {
        field: 'title',
        type: 'input',
        label: '论文标题',
        config: {
          clearable: false,
          maxlength: 300,
        },
      },
      {
        field: 'pmid',
        type: 'input',
        label: 'PubMed ID',
        config: {
          clearable: false,
          maxlength: 20,
        },
      },
      {
        field: 'doi',
        type: 'input',
        label: 'DOI',
        config: {
          clearable: false,
          maxlength: 100,
        },
      },
      {
        field: 'journal_id',
        type: 'input',
        label: '期刊ID',
        config: {
          clearable: false,
        },
      },
      {
        field: 'status',
        type: 'select',
        label: '状态',
        config: {
          options: [
            { label: '预发表', value: '0' },
            { label: '已出版', value: '1' },
          ],
          clearable: false,
        },
      },
      {
        field: 'received_date',
        type: 'datepicker',
        label: '收稿日期',
        config: {
          type: 'date',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
          clearable: true,
        },
      },
      {
        field: 'accepted_date',
        type: 'datepicker',
        label: '接受日期',
        config: {
          type: 'date',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
          clearable: true,
        },
      },
      {
        field: 'published_date',
        type: 'datepicker',
        label: '发表日期',
        config: {
          type: 'date',
          valueFormat: 'YYYY-MM-DD',
          format: 'YYYY/MM/DD',
          clearable: true,
        },
      },
      {
        field: 'abstract',
        type: 'textarea',
        label: '论文摘要',
        layout: {
          xl: 24,
          lg: 24,
          md: 24,
          sm: 24,
          xs: 24,
        },
        config: {
          rows: 6,
        },
      },
      {
        field: 'abstract_id',
        type: 'input',
        label: '摘要结构ID',
        config: {
          clearable: false,
        },
      },
      {
        field: 'remark',
        type: 'textarea',
        label: '备注',
        layout: {
          xl: 24,
          lg: 24,
          md: 24,
          sm: 24,
          xs: 24,
        },
        config: {
          rows: 3,
          maxlength: 500,
        },
      },
    ],
    colLayout: {
      xl: 12,
      lg: 12,
      md: 12,
      sm: 12,
      xs: 24,
    },
    itemStyle: {
      padding: '0px 8px 0px 8px',
    },
    elFormConfig: {
      labelWidth: '100px',
    },
    hideItems: ref([]),
  }
}
