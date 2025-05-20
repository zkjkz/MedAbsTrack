export default (listeners = {}) => {
  return {
    formItems: [
      {
        type: 'input',
        label: '方法名称',
        field: 'methodName',
        placeholder: '请输入方法名称',
        rules: [
          { required: true, message: '请输入方法名称', trigger: 'blur' }
        ]
      },
      {
        type: 'select',
        label: '方法类型',
        field: 'methodType',
        placeholder: '请选择方法类型',
        options: [
          { label: '规则抽取', value: 'REGEX' },
          { label: 'LLM抽取', value: 'LLM' }
        ],
        rules: [
          { required: true, message: '请选择方法类型', trigger: 'change' }
        ]
      },
      {
        type: 'textarea',
        label: '描述',
        field: 'description',
        placeholder: '请输入描述信息'
      },
      {
        type: 'input',
        label: '配置参数',
        field: 'configParams',
        placeholder: '请输入配置参数'
      },
      {
        type: 'select',
        label: '模板',
        field: 'templateId',
        placeholder: '请选择模板',
        options: []
      },
      {
        type: 'select',
        label: '模型',
        field: 'modelId',
        placeholder: '请选择模型',
        options: []
      },
      {
        type: 'select',
        label: '提示词',
        field: 'promptId',
        placeholder: '请选择提示词',
        options: []
      },
      {
        type: 'select',
        label: '状态',
        field: 'status',
        placeholder: '请选择状态',
        options: [
          { label: '启用', value: '1' },
          { label: '禁用', value: '0' }
        ],
        rules: [
          { required: true, message: '请选择状态', trigger: 'change' }
        ]
      }
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