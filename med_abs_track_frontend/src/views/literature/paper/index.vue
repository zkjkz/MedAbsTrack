<script setup name="Paper">
import { nextTick } from 'vue'
import { ElNotification } from 'element-plus'
import getSearchConfig from './config/searchConfig'
import getContentConfig from './config/contentConfig.js'
import getDialogConfig from './config/dialogConfig.js'
import useDialog from '@/hooks/useDialog'
import getComputedConfig from '@/hooks/getPageConfig'
import { literatureBaseUrl } from '@/api/config/base.js'
import { paper } from '@/views/pageName.js'
import to from '@/utils/to'
import { listExtractionMethod } from '@/api/literature/extraction_method'
import { executeExtraction } from '@/api/literature/extraction_task'
import { getAbstractStructureByPaperId } from '@/api/literature/abstract_structure'

const proxy = inject('proxy')
const pageName = paper
const requestBaseUrl = literatureBaseUrl
const pageSearchRef = ref(null)
const pageContentRef = ref(null)

// 添加查看详情所需的状态变量
const dialogVisible = ref(false)
const viewFormData = ref({})

// 添加抽取对话框相关状态
const extractDialogVisible = ref(false)
const currentPaperId = ref(null)
const extractionMethods = ref([])
const selectedMethodId = ref(null)
const extractLoading = ref(false)

// 添加查看抽取结果对话框相关状态
const viewExtractDialogVisible = ref(false)
const extractResultData = ref(null)
const extractResultLoading = ref(false)
const hasExtractResult = ref(false)

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

// 打开抽取对话框
const handleExtraction = (row) => {
  currentPaperId.value = row.paperId
  selectedMethodId.value = null
  extractDialogVisible.value = true
}

// 关闭抽取对话框
const closeExtractDialog = () => {
  extractDialogVisible.value = false
  currentPaperId.value = null
  selectedMethodId.value = null
}

// 执行抽取操作
const performExtraction = async () => {
  if (!selectedMethodId.value) {
    ElNotification({
      type: 'warning',
      message: '请选择抽取方法'
    })
    return
  }
  
  try {
    extractLoading.value = true
    const [res, err] = await to(executeExtraction({
      methodId: selectedMethodId.value,
      paperId: currentPaperId.value
    }))
    
    if (res) {
      closeExtractDialog()
      // 刷新数据
      pageSearchRef.value?.search()
    }
  } finally {
    extractLoading.value = false
  }
}

// 添加查看抽取结果功能
const handleViewExtractResult = async (row) => {
  currentPaperId.value = row.paperId
  extractResultLoading.value = true
  extractResultData.value = null
  hasExtractResult.value = false
  viewExtractDialogVisible.value = true
  
  try {
    const [res, err] = await to(getAbstractStructureByPaperId(row.paperId))
    
    if (res && res.data) {
      extractResultData.value = res.data
      hasExtractResult.value = true
    } else {
      hasExtractResult.value = false
    }
    
    if (err) {
      ElNotification({
        type: 'error',
        message: '获取抽取结果失败：' + (err.message || '未知错误')
      })
    }
  } finally {
    extractResultLoading.value = false
  }
}

// 关闭查看抽取结果对话框
const closeViewExtractDialog = () => {
  viewExtractDialogVisible.value = false
  currentPaperId.value = null
  extractResultData.value = null
}

// 加载所有可用的抽取方法列表
const loadExtractionMethods = async () => {
  try {
    const [res] = await to(listExtractionMethod({ pageNum: 1, pageSize: 100, status: '0' }))
    if (res && res.rows) {
      extractionMethods.value = res.rows
    }
  } catch (error) {
    console.error('加载抽取方法列表失败:', error)
  }
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

const beforeSend = (queryInfo) => {
  if (queryInfo.dateRange && Array.isArray(queryInfo.dateRange)) {
    const dateRange = queryInfo.dateRange
    queryInfo['params[beginTime]'] = dateRange[0]
    queryInfo['params[endTime]'] = dateRange[1]
    delete queryInfo.dateRange
  }
  
  if (queryInfo.published_date_range && Array.isArray(queryInfo.published_date_range)) {
    const publishedDateRange = queryInfo.published_date_range
    queryInfo['params[beginPublishedDate]'] = publishedDateRange[0]
    queryInfo['params[endPublishedDate]'] = publishedDateRange[1]
    delete queryInfo.published_date_range
  }
}

const permission = ref({
  add: 'literature:paper:add',
  edit: 'literature:paper:edit',
  del: 'literature:paper:remove',
  view: 'literature:paper:query',
  extract: 'literature:extraction_task:extract',
  viewExtract: 'literature:abstract_structure:query',
  export: 'literature:paper:export',
  list: 'literature:paper:list',
})
const onChangeShowColumn = (filterArr) => {
  tableHideItems.value = filterArr
}

/** 导出按钮操作 */
const handleExport = () => {
  proxy.download(
    'literature/paper/export',
    {
      ...searchData.value,
    },
    `paper_${new Date().getTime()}.xlsx`
  )
}

const init = () => {
  // 加载可用的抽取方法列表
  loadExtractionMethods()
}

// 添加自适应高度设置
const isSmall = window.isSmallScreen
const maxHeight = ref(520)
onMounted(() => {
  maxHeight.value = window.innerHeight - -57 - 52 - 30 - 80
})

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
      @beforeSend="beforeSend"
      :permission="permission"
      @onChangeShowColumn="onChangeShowColumn"
      @addClick="addClick"
      @editBtnClick="editBtnClick"
      @editMoreClick="editMoreClick"
      idKey="paperId"
    >
      <template #statusSlot="{ backData }">
        {{ backData.status === '1' ? '已出版' : '预发表' }}
      </template>
      <template #toolbar>
        <el-dropdown v-v-hasPermi="['literature:paper:export']">
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
      <!-- 添加操作列中的详情按钮和抽取按钮 -->
      <template #todoSlot="{ backData }">
        <el-button
          v-hasPermi="['literature:paper:query']"
          type="primary"
          size="small"
          @click="handleView(backData)"
        >
          <SvgIcon size="14" iconClass="eye" />
          <span class="ml6">详情</span>
        </el-button>
        <!-- 查看抽取结果按钮 -->
        <el-button
          v-if="backData.abstractId!==null"
          v-hasPermi="['literature:abstract_structure:query']"
          type="info"
          size="small"
          @click="handleViewExtractResult(backData)"
        >
          <SvgIcon size="14" iconClass="eye-open" />
          <span class="ml6">查看抽取</span>
        </el-button>
        <el-button
          v-else
          v-hasPermi="['literature:extraction_task:extract']"
          type="success"
          size="small"
          @click="handleExtraction(backData)"
        >
          <SvgIcon size="14" iconClass="key" />
          <span class="ml6">开始抽取</span>
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
    >
    </PageDialog>
    
    <!-- 添加查看详情的对话框 -->
    <el-dialog
      title="论文详细信息"
      v-model="dialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <BaseForm :data="viewFormData" v-bind="dialogConfig">
        </BaseForm>
      </el-scrollbar>
      <template #footer>
        <el-button @click="handleClose">关 闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加抽取对话框 -->
    <el-dialog
      title="选择抽取方法"
      v-model="extractDialogVisible"
      :width="500"
      destroy-on-close
    >
      <div class="extraction-form">
        <el-form label-width="100px">
          <el-form-item label="抽取方法">
            <el-select v-model="selectedMethodId" placeholder="请选择抽取方法" style="width: 100%">
              <el-option 
                v-for="method in extractionMethods" 
                :key="method.methodId" 
                :label="method.methodName" 
                :value="method.methodId"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="closeExtractDialog">取 消</el-button>
        <el-button type="primary" :loading="extractLoading" @click="performExtraction">执 行</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加查看抽取结果对话框 -->
    <el-dialog
      title="抽取结果"
      v-model="viewExtractDialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <div v-loading="extractResultLoading">
          <div v-if="hasExtractResult && extractResultData">
            <el-descriptions title="摘要结构信息" :column="1" border>
              <el-descriptions-item label="背景">
                {{ extractResultData.background || '暂无数据' }}
              </el-descriptions-item>
              <el-descriptions-item label="方法">
                {{ extractResultData.methods || '暂无数据' }}
              </el-descriptions-item>
              <el-descriptions-item label="结果">
                {{ extractResultData.results || '暂无数据' }}
              </el-descriptions-item>
              <el-descriptions-item label="结论">
                {{ extractResultData.conclusion || '暂无数据' }}
              </el-descriptions-item>
            </el-descriptions>
            <div v-if="extractResultData.content" class="mt20">
              <el-divider>其他结构内容</el-divider>
              <pre class="extract-content-pre">{{ JSON.stringify(extractResultData.content, null, 2) }}</pre>
            </div>
          </div>
          <div v-else-if="!extractResultLoading" class="empty-result">
            <el-empty description="暂无抽取结果" />
            <div class="text-center mt20">
              <el-button type="primary" @click="handleExtraction({paperId: currentPaperId})">
                开始抽取
              </el-button>
            </div>
          </div>
        </div>
      </el-scrollbar>
      <template #footer>
        <el-button @click="closeViewExtractDialog">关 闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.extraction-form {
  padding: 0 20px;
}
.empty-result {
  padding: 30px 0;
}
.extract-content-pre {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
}
.text-center {
  text-align: center;
}
.mt20 {
  margin-top: 20px;
}
</style>
