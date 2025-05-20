export default (listeners = {}) => {
  return {
    rules: {
      promptName: [
        { required: true, message: '模板名称不能为空', trigger: 'blur' },
        {
          min: 2,
          max: 100,
          message: '模板名称长度必须介于 2 和 100 之间',
          trigger: 'blur',
        },
      ],
      promptType: [
        { required: true, message: '模板类型不能为空', trigger: 'blur' },
      ],
      promptContent: [
        { required: true, message: '模板内容不能为空', trigger: 'blur' },
      ],
    },
    formItems: [
      {
        field: 'promptName',
        type: 'input',
        label: '模板名称',
        config: {
          clearable: false,
          maxlength: 100,
        },
      },
      {
        field: 'status',
        type: 'radio',
        options: [],
        label: '状态',
        isGroup: true,
        config: {
          clearable: false,
        },
        optionConfig: {
          border: true,
        },
      },
      {
        field: 'description',
        type: 'textarea',
        label: '描述',
        layout: {
          xl: 24,
          lg: 24,
          md: 24,
          sm: 24,
          xs: 24,
        },
        config: {
          rows: 3,
        },
      },
      {
        field: 'promptContent',
        type: 'textarea',
        label: '模板内容',
        layout: {
          xl: 24,
          lg: 24,
          md: 24,
          sm: 24,
          xs: 24,
        },
        config: {
          rows: 10,
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
      labelWidth: '80px',
    },
    hideItems: ref([]),
  }
}
