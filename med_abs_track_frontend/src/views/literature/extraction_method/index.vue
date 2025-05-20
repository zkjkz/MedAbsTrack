<script setup name="ExtractionMethod">
import { nextTick } from 'vue'
import { ElNotification } from 'element-plus'
import getSearchConfig from './config/searchConfig'
import getContentConfig from './config/contentConfig'
import getDialogConfig from './config/dialogConfig'
import useDialog from '@/hooks/useDialog'
import getComputedConfig from '@/hooks/getPageConfig'
import { literatureBaseUrl } from '@/api/config/base.js'
import { extractionMethod } from '@/views/pageName.js'
import to from '@/utils/to'
import {
  listExtraction_template,
  getExtraction_template,
} from '@/api/literature/extraction_template'
import { listLlm_model, getLlm_model } from '@/api/literature/llm_model'
import {
  listPrompt_template,
  getPrompt_template,
} from '@/api/literature/prompt_template'
import { changeExtractionMethodStatus } from '@/api/literature/extraction_method'

const proxy = inject('proxy')
const pageName = extractionMethod
const requestBaseUrl = literatureBaseUrl
const pageSearchRef = ref(null)
const pageContentRef = ref(null)

// 添加查看详情所需的状态变量
const dialogVisible = ref(false)
const viewFormData = ref({})

// 添加模板详情对话框状态
const templateDialogVisible = ref(false)
const templateDetailData = ref({})

// 添加模型详情对话框状态
const modelDialogVisible = ref(false)
const modelDetailData = ref({})

// 添加提示词详情对话框状态
const promptDialogVisible = ref(false)
const promptDetailData = ref({})

const dialogHideItems = ref([])
const tableHideItems = ref([])
const dictMap = {}
const searchConfig = getSearchConfig()
const searchConfigComputed = computed(() => {
  return getComputedConfig(searchConfig, dictMap)
})
const tableSelected = ref([])
const tableListener = {
  selectionChange: (selected) => {
    tableSelected.value = selected
  },
}
const contentConfig = getContentConfig()
const contentConfigComputed = computed(() => {
  contentConfig.hideItems = tableHideItems
  return contentConfig
})

const dialogConfig = getDialogConfig()
const dialogConfigComputed = computed(() => {
  dialogConfig.hideItems = dialogHideItems
  return getComputedConfig(dialogConfig, dictMap)
})

// 添加查看详情的处理函数
const handleView = (row) => {
  dialogVisible.value = true
  viewFormData.value = row
}

const handleClose = () => {
  dialogVisible.value = false
  viewFormData.value = {}
}

// 关闭模板详情对话框
const closeTemplateDialog = () => {
  templateDialogVisible.value = false
  templateDetailData.value = {}
}

// 关闭模型详情对话框
const closeModelDialog = () => {
  modelDialogVisible.value = false
  modelDetailData.value = {}
}

// 关闭提示词详情对话框
const closePromptDialog = () => {
  promptDialogVisible.value = false
  promptDetailData.value = {}
}

const addCallBack = () => {
  dialogHideItems.value.length = 0
}

const editCallBack = (item) => {
  dialogHideItems.value = []
}

const isEditMore = ref(false)
const editMoreClick = () => {
  if (tableSelected.value.length > 0) {
    const data = tableSelected.value[0]
    pageContentRef.value?.editClick(data, true)
    nextTick(() => {
      const newArray = tableSelected.value.slice(1)
      dialogRef.value?.changeSelected(newArray)
    })
  }
}

const editNext = (data) => {
  pageContentRef.value?.editClick(data, true)
}

const [dialogRef, infoInit, addClick, editBtnClick] = useDialog(
  addCallBack,
  editCallBack,
  '添加'
)

const dialogWidth = ref('800px')
const searchData = computed(() => {
  return pageContentRef.value?.finalSearchData
})

const search = () => {
  pageSearchRef.value?.search()
}

const permission = ref({
  add: 'literature:extraction_method:add',
  edit: 'literature:extraction_method:edit',
  del: 'literature:extraction_method:remove',
  view: 'literature:extraction_method:query',
  export: 'literature:extraction_method:export',
  list: 'literature:extraction_method:list'
})

const onChangeShowColumn = (filterArr) => {
  tableHideItems.value = filterArr
}

/** 导出按钮操作 */
const handleExport = () => {
  proxy.download(
    'literature/extraction_method/export',
    {
      ...searchData.value,
    },
    `extraction_method_${new Date().getTime()}.xlsx`
  )
}

// 添加自适应高度设置
const isSmall = window.isSmallScreen
const maxHeight = ref(520)
onMounted(() => {
  maxHeight.value = window.innerHeight - -57 - 52 - 30 - 80
})

// 初始化下拉选项数据
const initOptions = async () => {
  try {
    // 获取可用的模板列表
    const [templateRes] = await to(
      listExtraction_template({ pageNum: 1, pageSize: 100, status: '0' })
    )
    if (templateRes && templateRes.rows) {
      dialogConfig.formItems.find(
        (item) => item.field === 'templateId'
      ).options = templateRes.rows.map((item) => ({
        label: item.templateName,
        value: item.templateId,
      }))
    }

    // 获取可用的模型列表
    const [modelRes] = await to(
      listLlm_model({ pageNum: 1, pageSize: 100, status: '0' })
    )
    if (modelRes && modelRes.rows) {
      dialogConfig.formItems.find((item) => item.field === 'modelId').options =
        modelRes.rows.map((item) => ({
          label: item.modelName,
          value: item.modelId,
        }))
    }

    // 获取可用的提示词列表
    const [promptRes] = await to(
      listPrompt_template({ pageNum: 1, pageSize: 100, status: '0' })
    )
    if (promptRes && promptRes.rows) {
      dialogConfig.formItems.find((item) => item.field === 'promptId').options =
        promptRes.rows.map((item) => ({
          label: item.promptName,
          value: item.promptId,
        }))
    }
  } catch (error) {
    console.error('初始化选项数据失败:', error)
  }
}

// 添加模板详情查看功能
const templateMap = ref({})
const viewTemplateDetail = async (templateId) => {
  try {
    const [res] = await to(getExtraction_template(templateId))
    console.log(res)
    if (res) {
      templateDialogVisible.value = true
      templateDetailData.value = res.data
    }
  } catch (error) {
    console.error('获取模板详情失败:', error)
  }
}

// 添加模型详情查看功能
const modelMap = ref({})
const viewModelDetail = async (modelId) => {
  try {
    const [res] = await to(getLlm_model(modelId))
    console.log(res)
    if (res) {
      modelDialogVisible.value = true
      modelDetailData.value = res.data
    }
  } catch (error) {
    console.error('获取模型详情失败:', error)
  }
}

// 添加提示词详情查看功能
const promptMap = ref({})
const viewPromptDetail = async (promptId) => {
  try {
    const [res] = await to(getPrompt_template(promptId))
    console.log(res)
    if (res) {
      promptDialogVisible.value = true
      promptDetailData.value = res.data
    }
  } catch (error) {
    console.error('获取提示词详情失败:', error)
  }
}

// 加载所有相关数据的名称映射
const loadNameMappings = async () => {
  try {
    // 加载模板名称映射
    const [templateRes] = await to(
      listExtraction_template({ pageNum: 1, pageSize: 999 })
    )
    if (templateRes && templateRes.rows) {
      templateMap.value = templateRes.rows.reduce((acc, item) => {
        acc[item.templateId] = item.templateName
        return acc
      }, {})
    }

    // 加载模型名称映射
    const [modelRes] = await to(listLlm_model({ pageNum: 1, pageSize: 999 }))
    if (modelRes && modelRes.rows) {
      modelMap.value = modelRes.rows.reduce((acc, item) => {
        acc[item.modelId] = item.modelName
        return acc
      }, {})
    }

    // 加载提示词名称映射
    const [promptRes] = await to(
      listPrompt_template({ pageNum: 1, pageSize: 999 })
    )
    if (promptRes && promptRes.rows) {
      promptMap.value = promptRes.rows.reduce((acc, item) => {
        acc[item.promptId] = item.promptName
        return acc
      }, {})
    }
  } catch (error) {
    console.error('加载名称映射失败:', error)
  }
}

/** 修改模型状态 */
const handleStatusChange = async (row) => {
  let text = row.status === '0' ? '启用' : '停用'
  const [res, err] = await to(
    changeExtractionMethodStatus(row.methodId, row.status)
  )
  if (res) {
    ElNotification({
      type: 'success',
      message: text + '成功',
    })
  }
  if (err) {
    row.status = row.status === '0' ? '1' : '0'
  }
}

const init = () => {
  initOptions()
  loadNameMappings()
}

init()
</script>

<template>
  <div class="default-main page">
    <PageSearch
      ref="pageSearchRef"
      :pageName="pageName"
      :searchConfig="searchConfigComputed"
    ></PageSearch>
    <PageContent
      ref="pageContentRef"
      :pageName="pageName"
      :contentConfig="contentConfigComputed"
      :autoDesc="false"
      :dictMap="dictMap"
      :tableListener="tableListener"
      :tableSelected="tableSelected"
      :requestBaseUrl="requestBaseUrl"
      :permission="permission"
      @onChangeShowColumn="onChangeShowColumn"
      @addClick="addClick"
      @editBtnClick="editBtnClick"
      @editMoreClick="editMoreClick"
      idKey="methodId"
    >
      <!-- 模板插槽 -->
      <template #templateSlot="{ backData }">
        <el-button
          v-if="templateMap[backData.templateId]"
          type="text"
          @click="viewTemplateDetail(backData.templateId)"
        >
          {{ templateMap[backData.templateId] }}
        </el-button>
        <span v-else>{{ backData.templateId }}</span>
      </template>

      <!-- 模型插槽 -->
      <template #modelSlot="{ backData }">
        <el-button
          v-if="modelMap[backData.modelId]"
          type="text"
          @click="viewModelDetail(backData.modelId)"
        >
          {{ modelMap[backData.modelId] }}
        </el-button>
        <span v-else>{{ backData.modelId }}</span>
      </template>

      <!-- 提示词插槽 -->
      <template #promptSlot="{ backData }">
        <el-button
          v-if="promptMap[backData.promptId]"
          type="text"
          @click="viewPromptDetail(backData.promptId)"
        >
          {{ promptMap[backData.promptId] }}
        </el-button>
        <span v-else>{{ backData.promptId }}</span>
      </template>

      <template #statusSlot="{ backData }">
        <el-switch
          v-model="backData.status"
          active-value="0"
          inactive-value="1"
          @click="handleStatusChange(backData)"
        ></el-switch>
      </template>
      <template #toolbar>
        <el-dropdown v-v-hasPermi="['literature:extraction_method:export']">
          <el-button type="primary" plain>
            <el-icon><download /></el-icon>更多操作
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleExport"
                ><download />导出</el-dropdown-item
              >
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template #todoSlot="{ backData }">
        <el-button
          v-hasPermi="['literature:llm_model:query']"
          type="primary"
          size="small"
          @click="handleView(backData)"
        >
          <SvgIcon size="14" iconClass="eye" />
          <span class="ml6">详情</span>
        </el-button>
      </template>
    </PageContent>
    <PageDialog
      ref="dialogRef"
      :pageName="pageName"
      :dialogConfig="dialogConfigComputed"
      :infoInit="infoInit"
      :width="getWidth(dialogWidth)"
      :requestBaseUrl="requestBaseUrl"
      :search="search"
      @editNext="editNext"
      :hasEditMore="true"
      :isEditMore="isEditMore"
      idKey="methodId"
      sendIdKey="methodId"
    >
    </PageDialog>
    <!-- 添加查看详情的对话框 -->
    <el-dialog
      title="抽取方法详细信息"
      v-model="dialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <BaseForm :data="viewFormData" v-bind="dialogConfig"> </BaseForm>
      </el-scrollbar>
      <template #footer>
        <el-button @click="handleClose">关 闭</el-button>
      </template>
    </el-dialog>

    <!-- 模板详情对话框 -->
    <el-dialog
      title="模板详细信息"
      v-model="templateDialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <div class="detail-container">
          <div class="detail-item">
            <div class="detail-label">模板ID：</div>
            <div class="detail-value">{{ templateDetailData.templateId }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">模板名称：</div>
            <div class="detail-value">
              {{ templateDetailData.templateName }}
            </div>
          </div>
          <div class="detail-item">
            <div class="detail-label">模板描述：</div>
            <div class="detail-value">{{ templateDetailData.description }}</div>
          </div>
          <div class="detail-item" v-if="templateDetailData.templateContent">
            <div class="detail-label">模板内容：</div>
            <div class="detail-value content-box">
              {{ templateDetailData.templateContent }}
            </div>
          </div>
          <div class="detail-item" v-if="templateDetailData.remark">
            <div class="detail-label">备注：</div>
            <div class="detail-value">{{ templateDetailData.remark }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">状态：</div>
            <div class="detail-value">{{ templateDetailData.status === '0' ? '启用' : '停用' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">创建时间：</div>
            <div class="detail-value">{{ templateDetailData.createTime }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">更新时间：</div>
            <div class="detail-value">{{ templateDetailData.updateTime }}</div>
          </div>
        </div>
      </el-scrollbar>
      <template #footer>
        <el-button @click="closeTemplateDialog">关 闭</el-button>
      </template>
    </el-dialog>

    <!-- 模型详情对话框 -->
    <el-dialog
      title="模型详细信息"
      v-model="modelDialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <div class="detail-container">
          <div class="detail-item">
            <div class="detail-label">模型ID：</div>
            <div class="detail-value">{{ modelDetailData.modelId }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.displayName">
            <div class="detail-label">显示名称：</div>
            <div class="detail-value">{{ modelDetailData.displayName }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">模型名称：</div>
            <div class="detail-value">{{ modelDetailData.modelName }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.modelVersion">
            <div class="detail-label">模型版本：</div>
            <div class="detail-value">{{ modelDetailData.modelVersion }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.provider">
            <div class="detail-label">模型提供商：</div>
            <div class="detail-value">{{ modelDetailData.provider }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.description">
            <div class="detail-label">模型描述：</div>
            <div class="detail-value">{{ modelDetailData.description }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.baseUrl">
            <div class="detail-label">API基础URL：</div>
            <div class="detail-value">{{ modelDetailData.baseUrl }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.apiKey">
            <div class="detail-label">API密钥：</div>
            <div class="detail-value">{{ modelDetailData.apiKey }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.contextLength">
            <div class="detail-label">上下文长度：</div>
            <div class="detail-value">{{ modelDetailData.contextLength }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.requestTimeout">
            <div class="detail-label">超时时间(秒)：</div>
            <div class="detail-value">{{ modelDetailData.requestTimeout }}</div>
          </div>
          <div class="detail-item" v-if="modelDetailData.remark">
            <div class="detail-label">备注：</div>
            <div class="detail-value">{{ modelDetailData.remark }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">状态：</div>
            <div class="detail-value">{{ modelDetailData.status === '0' ? '启用' : '停用' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">创建时间：</div>
            <div class="detail-value">{{ modelDetailData.createTime }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">更新时间：</div>
            <div class="detail-value">{{ modelDetailData.updateTime }}</div>
          </div>
        </div>
      </el-scrollbar>
      <template #footer>
        <el-button @click="closeModelDialog">关 闭</el-button>
      </template>
    </el-dialog>

    <!-- 提示词详情对话框 -->
    <el-dialog
      title="提示词详细信息"
      v-model="promptDialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <div class="detail-container">
          <div class="detail-item">
            <div class="detail-label">提示词ID：</div>
            <div class="detail-value">{{ promptDetailData.promptId }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">提示词名称：</div>
            <div class="detail-value">{{ promptDetailData.promptName }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">提示词描述：</div>
            <div class="detail-value">{{ promptDetailData.description }}</div>
          </div>
          <div class="detail-item" v-if="promptDetailData.promptContent">
            <div class="detail-label">提示词内容：</div>
            <div class="detail-value content-box">
              {{ promptDetailData.promptContent }}
            </div>
          </div>
          <div class="detail-item" v-if="promptDetailData.remark">
            <div class="detail-label">备注：</div>
            <div class="detail-value">{{ promptDetailData.remark }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">状态：</div>
            <div class="detail-value">{{ promptDetailData.status === '0' ? '启用' : '停用' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">创建时间：</div>
            <div class="detail-value">{{ promptDetailData.createTime }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">更新时间：</div>
            <div class="detail-value">{{ promptDetailData.updateTime }}</div>
          </div>
        </div>
      </el-scrollbar>
      <template #footer>
        <el-button @click="closePromptDialog">关 闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.detail-container {
  padding: 10px;
}
.detail-item {
  display: flex;
  margin-bottom: 16px;
}
.detail-label {
  width: 100px;
  font-weight: bold;
  color: #606266;
}
.detail-value {
  flex: 1;
}
.content-box {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}
</style>
