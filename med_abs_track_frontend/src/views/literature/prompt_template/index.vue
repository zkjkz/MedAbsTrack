<script setup name="PromptTemplate">
import { nextTick, onMounted } from 'vue'
import { ElNotification } from 'element-plus'
import getSearchConfig from './config/searchConfig'
import getContentConfig from './config/contentConfig.js'
import getDialogConfig from './config/dialogConfig.js'
import useDialog from '@/hooks/useDialog'
import getComputedConfig from '@/hooks/getPageConfig'
import { literatureBaseUrl } from '@/api/config/base.js'
import { promptTemplate } from '@/views/pageName.js'
import to from '@/utils/to'
import { changePrompt_templateStatus } from '@/api/literature/prompt_template'

const proxy = inject('proxy')
const { sys_normal_disable } = proxy.useDict('sys_normal_disable')
const pageName = promptTemplate
const requestBaseUrl = literatureBaseUrl
const pageSearchRef = ref(null)
const pageContentRef = ref(null)

// 添加查看详情所需的状态变量
const dialogVisible = ref(false)
const viewFormData = ref({})

const dialogHideItems = ref([])
const tableHideItems = ref([])
const dictMap = {
  status: sys_normal_disable,
}
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

const addCallBack = () => {
  dialogHideItems.value.length = 0
  dialogRef.value?.setFormData('status', '0')
}
const editCallBack = (_item, type, _res) => {
  isEditMore.value = type
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
}

const permission = ref({
  add: 'literature:prompt_template:add',
  edit: 'literature:prompt_template:edit',
  del: 'literature:prompt_template:remove',
  export: 'literature:prompt_template:export',
  query: 'literature:prompt_template:query',
  list: 'literature:prompt_template:list'
})
const onChangeShowColumn = (filterArr) => {
  tableHideItems.value = filterArr
}

/** 导出按钮操作 */
const handleExport = () => {
  proxy.download(
    'literature/prompt_template/export',
    {
      ...searchData.value,
    },
    `prompt_template_${new Date().getTime()}.xlsx`
  )
}

// 添加自适应高度设置
const isSmall = window.isSmallScreen
const maxHeight = ref(520)
onMounted(() => {
  maxHeight.value = window.innerHeight - -57 - 52 - 30 - 80
})

/** 修改模板状态 */
const handleStatusChange = async (row) => {
  let text = row.status === '0' ? '启用' : '停用'
  const [res, err] = await to(
    changePrompt_templateStatus(row.promptId, row.status)
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
  // 初始化操作，可以加载下拉选项等
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
      @beforeSend="beforeSend"
      :permission="permission"
      @onChangeShowColumn="onChangeShowColumn"
      @addClick="addClick"
      @editBtnClick="editBtnClick"
      @editMoreClick="editMoreClick"
      idKey="promptId"
    >
      <template #statusSlot="{ backData }">
        <el-switch
          v-model="backData.status"
          active-value="0"
          inactive-value="1"
          @click="handleStatusChange(backData)"
        ></el-switch>
      </template>
      <template #toolbar>
        <el-dropdown v-v-hasPermi="['literature:prompt_template:export']">
          <el-button type="primary" plain>
            <el-icon>
              <download /> </el-icon
            >更多操作
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleExport">
                <download />导出
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <!-- 添加操作列中的详情按钮 -->
      <template #todoSlot="{ backData }">
        <el-button
          v-hasPermi="['literature:prompt_template:query']"
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
      idKey="promptId"
      sendIdKey="promptId"
    >
    </PageDialog>
    
    <!-- 添加查看详情的对话框 -->
    <el-dialog
      title="提示模板详细信息"
      v-model="dialogVisible"
      draggable
      :top="isSmall ? '0vh' : '11vh'"
      :fullscreen="isSmall"
      :width="getWidth(1000)"
    >
      <el-scrollbar :max-height="maxHeight">
        <BaseForm :data="viewFormData" v-bind="dialogConfig">
          <template #statusSlot="{ backData }">
            <dict-tag :options="sys_normal_disable" :value="backData.formData.status" />
          </template>
        </BaseForm>
      </el-scrollbar>
      <template #footer>
        <el-button @click="handleClose">关 闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>
