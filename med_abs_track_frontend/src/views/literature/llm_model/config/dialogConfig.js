export default (listeners = {}) => {
  return {
    rules: {
      displayName: [
        { required: true, message: '显示名称不能为空', trigger: 'blur' },
        {
          min: 2,
          max: 100,
          message: '显示名称长度必须介于 2 和 100 之间',
          trigger: 'blur',
        },
      ],
      modelName: [
        { required: true, message: '模型名称不能为空', trigger: 'blur' },
        {
          max: 100,
          message: '模型名称长度不能超过100个字符',
          trigger: 'blur',
        },
      ],
      modelVersion: [
        {
          max: 50,
          message: '模型版本长度不能超过50个字符',
          trigger: 'blur',
        },
      ],
      provider: [
        {
          max: 100,
          message: '模型提供商长度不能超过100个字符',
          trigger: 'blur',
        },
      ],
      baseUrl: [
        {
          max: 255,
          message: 'API基础URL长度不能超过255个字符',
          trigger: 'blur',
        },
      ],
      apiKey: [
        {
          max: 255,
          message: 'API密钥长度不能超过255个字符',
          trigger: 'blur',
        },
      ],
      organizationId: [
        {
          max: 100,
          message: '组织ID长度不能超过100个字符',
          trigger: 'blur',
        },
      ],
      defaultParameters: [
        {
          validator: (rule, value, callback) => {
            if (value && value.trim() !== '') {
              try {
                JSON.parse(value)
                callback()
              } catch (e) {
                callback(new Error('请输入有效的JSON格式'))
              }
            } else {
              callback()
            }
          },
          trigger: 'blur',
        },
      ],
      contextLength: [
        {
          type: 'number',
          message: '上下文长度必须为数字',
          trigger: 'blur'
        }
      ],
      requestTimeout: [
        {
          type: 'number',
          message: '请求超时时间必须为数字',
          trigger: 'blur'
        }
      ],
      status: [{ required: true, message: '状态不能为空', trigger: 'change' }],
    },
    formItems: [
      {
        field: 'displayName',
        type: 'input',
        label: '显示名称',
        config: {
          clearable: false,
          maxlength: 100,
          placeholder: '请输入显示名称',
        },
      },
      {
        field: 'modelName',
        type: 'input',
        label: '模型名称',
        config: {
          clearable: false,
          maxlength: 100,
          placeholder: '请输入模型名称，如gpt-4, gpt-3.5-turbo等',
        },
      },
      {
        field: 'modelVersion',
        type: 'input',
        label: '模型版本',
        config: {
          clearable: true,
          maxlength: 50,
          placeholder: '请输入模型版本，如0613, 0125-preview等',
        },
      },
      {
        field: 'provider',
        type: 'input',
        label: '模型提供商',
        config: {
          clearable: true,
          maxlength: 100,
          placeholder: '请输入模型提供商，默认为OpenAI',
        },
      },
      {
        field: 'baseUrl',
        type: 'input',
        label: 'API基础URL',
        config: {
          clearable: true,
          maxlength: 255,
          placeholder: '请输入API基础URL，默认为https://api.openai.com/v1',
        },
      },
      {
        field: 'apiKey',
        type: 'password',
        label: 'API密钥',
        config: {
          clearable: true,
          maxlength: 255,
          placeholder: '请输入API密钥',
          showPassword: true,
        },
      },
      {
        field: 'organizationId',
        type: 'input',
        label: '组织ID',
        config: {
          clearable: true,
          maxlength: 100,
          placeholder: '请输入OpenAI组织ID，可选',
        },
      },
      {
        field: 'contextLength',
        type: 'inputNumber',
        label: '上下文长度',
        config: {
          clearable: true,
          placeholder: '请输入模型上下文长度限制',
        },
      },
      {
        field: 'requestTimeout',
        type: 'inputNumber',
        label: '请求超时',
        config: {
          clearable: true,
          placeholder: '请输入请求超时时间（秒），默认30秒',
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
        field: 'defaultParameters',
        type: 'textarea',
        label: '默认参数',
        layout: {
          xl: 24,
          lg: 24,
          md: 24,
          sm: 24,
          xs: 24,
        },
        config: {
          rows: 5,
          placeholder: '请输入JSON格式的默认参数配置，如temperature, max_tokens等',
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
          placeholder: '请输入备注信息',
          maxlength: 500,
          showWordLimit: true,
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
