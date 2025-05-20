export default (otherConfig = {}) => {
  return {
    labelWidth: '120px',
    formItems: [
      {
        type: 'input',
        label: '方法名称',
        field: 'methodName',
        placeholder: '请输入方法名称'
      },
      {
        type: 'select',
        label: '方法类型',
        field: 'methodType',
        placeholder: '请选择方法类型',
        options: [
          { label: '规则抽取', value: 'rule' },
          { label: 'LLM抽取', value: 'llm' }
        ]
      },
      {
        type: 'select',
        label: '状态',
        field: 'status',
        placeholder: '请选择状态',
        options: [
          { label: '启用', value: '1' },
          { label: '禁用', value: '0' }
        ]
      }
    ],
    elFormConfig: {},
  }
} 