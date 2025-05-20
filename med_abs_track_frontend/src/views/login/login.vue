<script setup>
import { getCodeImg } from '@/api/login.js'
import useUserStore from '@/store/modules/user.js'
import getFormConfig from './config/formConfig.js'
import { decrypt, encrypt } from '@/utils/jsencrypt.js'
import Cookies from 'js-cookie'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const title = ref(import.meta.env.VITE_APP_TITLE)
const formRef = ref(null)
const formData = ref({
  code: '',
  username: '',
  password: '',
  uuid: '',
  rememberMe: false,
})
const codeUrl = ref('')
// 验证码开关
const captchaEnabled = ref(true)
const hideItems = ref([])

// 生成验证码
const generateCode = async () => {
  const res = await getCodeImg()
  if (res) {
    codeUrl.value = 'data:image/gif;base64,' + res.img
    formData.value.uuid = res.uuid
    captchaEnabled.value = res.captchaEnabled === true
  }
}

const getCookie = () => {
  const username = Cookies.get('username')
  const password = Cookies.get('password')
  const rememberMe = Cookies.get('rememberMe')
  formData.value = {
    username: username || 'admin',
    password: decrypt(password) || 'admin123',
    rememberMe: rememberMe ? false : Boolean(rememberMe),
    code: '',
    uuid: '',
  }
}

const config = {
  codeHide: !captchaEnabled.value,
  listener: {
    keyup: (event) => {
      if (event.key === 'Enter') {
        submit()
      }
    },
  },
}
const formConfig = getFormConfig(config)
const formConfigComputed = computed(() => {
  if (!captchaEnabled.value) {
    hideItems.value = ['code']
  } else {
    hideItems.value = []
  }
  formConfig.hideItems = hideItems
  return formConfig
})
const redirect = ref(undefined)

watch(
  route,
  (newRoute) => {
    redirect.value = newRoute.query && newRoute.query.redirect
  },
  { immediate: true }
)
const loginLoading = ref(false)
const submit = async () => {
  let flag = await formRef.value?.getFormValidate()
  if (flag) {
    loginLoading.value = true
    try {
      await userStore.login(formData.value)
      const query = route.query
      const otherQueryParams = Object.keys(query).reduce((acc, cur) => {
        if (cur !== 'redirect') {
          acc[cur] = query[cur]
        }
        return acc
      }, {})
      if (formData.value.rememberMe) {
        Cookies.set('username', formData.value.username, { expires: 30 })
        Cookies.set('password', encrypt(formData.value.password), {
          expires: 30,
        })
        Cookies.set('rememberMe', formData.value.rememberMe, { expires: 30 })
      } else {
        // 否则移除
        Cookies.remove('username')
        Cookies.remove('password')
        Cookies.remove('rememberMe')
      }
      router.push({ path: redirect.value || '/', query: otherQueryParams })
    } catch (error) {
      if (captchaEnabled.value) {
        generateCode()
      }
      loginLoading.value = false
    }
  }
}

const init = () => {
  generateCode()
  getCookie()
}
init()
onUnmounted(() => {
  loginLoading.value = false
})
</script>

<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-card">
        <div class="logo-container">
          <div class="logo-circle">
            <SvgIcon iconClass="user" size="24" class="logo-icon" />
          </div>
        </div>
        <h2 class="login-title">{{ title }}</h2>
        
        <BaseForm ref="formRef" :data="formData" v-bind="formConfigComputed" class="login-form">
          <template #usernamePrefix>
            <SvgIcon iconClass="user" size="16" class="input-icon"></SvgIcon>
          </template>
          <template #passwordPrefix>
            <SvgIcon iconClass="unlock" size="16" class="input-icon"></SvgIcon>
          </template>
          <template #codeCustom>
            <div class="verification-code-container">
              <el-input
                v-model="formData.code"
                class="verification-input"
                placeholder="验证码"
                size="large"
                @keyup.enter="submit"
              >
                <template #prefix>
                  <SvgIcon :size="16" iconClass="shield-halved" class="input-icon" />
                </template>
              </el-input>
              <div class="verification-image" @click="generateCode">
                <el-image :src="codeUrl" class="captcha-image">
                  <template #error>
                    <el-icon>
                      <DocumentDelete />
                    </el-icon>
                  </template>
                  <template #placeholder>
                    <el-icon class="is-loading">
                      <Loading />
                    </el-icon>
                  </template>
                </el-image>
              </div>
            </div>
          </template>
          <template #footer>
            <div class="footer">
              <el-button
                :loading="loginLoading"
                size="large"
                type="primary"
                class="login-button"
                @click="submit"
              >
                登录
              </el-button>
            </div>
          </template>
        </BaseForm>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: cover;
  padding: 20px;
}

.login-content {
  width: 100%;
  max-width: 420px;
}

.login-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 40px 30px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  }
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.logo-circle {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  box-shadow: 0 8px 16px rgba(118, 75, 162, 0.3);
}

.logo-icon {
  color: white;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  font-weight: 600;
  color: #333;
  font-size: 24px;
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-input) {
    border-radius: 8px;
    overflow: hidden;
    
    .el-input__wrapper {
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05) !important;
      padding: 0 15px;
      transition: all 0.3s;
      
      &:hover, &:focus, &.is-focus {
        box-shadow: 0 3px 15px rgba(102, 126, 234, 0.2) !important;
      }
    }
  }
}

.input-icon {
  color: #667eea;
}

.verification-code-container {
  display: flex;
  gap: 12px;
}

.verification-input {
  flex: 2;
}

.verification-image {
  flex: 1;
  height: 38px;
  overflow: hidden;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  
  &:hover {
    transform: scale(1.02);
  }

  .captcha-image {
    width: 100%;
    height: 100%;
  }

  :deep(.el-image__wrapper) {
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.footer {
  margin-top: 30px;
  width: 100%;

  .login-button {
    width: 100%;
    height: 44px;
    border-radius: 8px;
    font-weight: 500;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}
</style>