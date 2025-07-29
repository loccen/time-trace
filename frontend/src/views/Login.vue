<template>
  <div class="login">
    <div class="login-container">
      <div class="login-form">
        <div class="title-container">
          <h3 class="title">时迹工时追踪系统</h3>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form-content"
          autocomplete="on"
          label-position="left"
        >
          <el-form-item prop="username">
            <span class="svg-container">
              <el-icon><User /></el-icon>
            </span>
            <el-input
              ref="username"
              v-model="loginForm.username"
              placeholder="用户名"
              name="username"
              type="text"
              tabindex="1"
              autocomplete="on"
            />
          </el-form-item>

          <el-tooltip v-model="capsTooltip" content="大写锁定已开启" placement="right" manual>
            <el-form-item prop="password">
              <span class="svg-container">
                <el-icon><Lock /></el-icon>
              </span>
              <el-input
                :key="passwordType"
                ref="password"
                v-model="loginForm.password"
                :type="passwordType"
                placeholder="密码"
                name="password"
                tabindex="2"
                autocomplete="on"
                @keyup="checkCapslock"
                @blur="capsTooltip = false"
                @keyup.enter="handleLogin"
              />
              <span class="show-pwd" @click="showPwd">
                <el-icon>
                  <View v-if="passwordType === 'password'" />
                  <Hide v-else />
                </el-icon>
              </span>
            </el-form-item>
          </el-tooltip>

          <el-button
            :loading="loading"
            type="primary"
            style="width:100%;margin-bottom:30px;"
            @click.prevent="handleLogin"
          >
            登录
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const username = ref(null)
const password = ref(null)

const loginForm = ref({
  username: 'admin',
  password: '123456'
})

const loginRules = ref({
  username: [{ required: true, trigger: 'blur', message: '请输入用户名' }],
  password: [{ required: true, trigger: 'blur', message: '请输入密码' }]
})

const passwordType = ref('password')
const capsTooltip = ref(false)
const loading = ref(false)

const showPwd = () => {
  if (passwordType.value === 'password') {
    passwordType.value = ''
  } else {
    passwordType.value = 'password'
  }
  nextTick(() => {
    password.value.focus()
  })
}

const checkCapslock = (e) => {
  const { key } = e
  capsTooltip.value = key && key.length === 1 && (key >= 'A' && key <= 'Z')
}

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await userStore.login(loginForm.value)
        if (result.success) {
          ElMessage.success('登录成功')
          router.push({ path: '/' })
        } else {
          ElMessage.error(result.message)
        }
      } catch (error) {
        ElMessage.error('登录失败')
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.error('请填写完整信息')
      return false
    }
  })
}
</script>

<style lang="scss" scoped>
.login {
  min-height: 100vh;
  width: 100%;
  background-color: #2d3a4b;
  overflow: hidden;

  .login-container {
    position: relative;
    width: 100%;
    min-height: 100vh;
    background-color: #2d3a4b;
    overflow: hidden;

    .login-form {
      position: relative;
      width: 520px;
      max-width: 100%;
      padding: 160px 35px 0;
      margin: 0 auto;
      overflow: hidden;

      .title-container {
        position: relative;

        .title {
          font-size: 26px;
          color: #eee;
          margin: 0px auto 40px auto;
          text-align: center;
          font-weight: bold;
        }
      }

      .login-form-content {
        .el-form-item {
          border: 1px solid rgba(255, 255, 255, 0.1);
          background: rgba(0, 0, 0, 0.1);
          border-radius: 5px;
          color: #454545;
        }

        .el-input {
          display: inline-block;
          height: 47px;
          width: 85%;

          :deep(.el-input__wrapper) {
            padding: 0;
            background: transparent;
            box-shadow: none;

            .el-input__inner {
              background: transparent;
              border: 0px;
              border-radius: 0px;
              padding: 12px 5px 12px 15px;
              color: #fff;
              height: 47px;
              caret-color: #fff;

              &:-webkit-autofill {
                box-shadow: 0 0 0px 1000px #283443 inset !important;
                -webkit-text-fill-color: #fff !important;
              }
            }
          }
        }

        .svg-container {
          padding: 6px 5px 6px 15px;
          color: #889aa4;
          vertical-align: middle;
          display: inline-block;
        }

        .show-pwd {
          position: absolute;
          right: 10px;
          top: 7px;
          font-size: 16px;
          color: #889aa4;
          cursor: pointer;
          user-select: none;
        }
      }
    }
  }
}
</style>
