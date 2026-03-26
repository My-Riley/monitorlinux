<template>
  <div class="login">
    <div class="container">
      <div class="container-left">
        <div class="logo"></div>
        <div class="left-content">
          <img
            alt="情绪识别系统"
            src="../assets/svg/login-box-bg.svg"
            class="-enter-x left-transition"
          />
          <div class="login-text -enter-x left-transition">
            <span>情绪识别系统</span>
          </div>
        </div>
      </div>
      <div class="container-right">
        <div class="form-content -enter-x right-transition">
          <h1 class="title">登录</h1>
          <el-form
            ref="loginForm"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                type="text"
                auto-complete="off"
                placeholder="账号"
                style="width: 63%"
              ></el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                auto-complete="off"
                placeholder="密码"
                @keyup.enter.native="handleLogin"
                show-password
                style="width: 63%"
              ></el-input>
            </el-form-item>
            <el-form-item prop="code" v-if="captchaEnabled" class="mb10" style="display: flex; align-items: center; width: 63%;">
              <el-input
                v-model="loginForm.code"
                auto-complete="off"
                placeholder="验证码"
                @keyup.enter.native="handleLogin"
                style="width: 63%; margin-right: 10px;"
              >
              </el-input>
              <div class="login-code">
                <img :src="codeUrl" @click="getCode" class="login-code-img" />
              </div>
            </el-form-item>
            <el-checkbox
              v-model="loginForm.rememberMe"
              style="margin: 0px 0px 25px 0px"
            >记住密码</el-checkbox>
            <el-form-item style="width: 100%">
              <el-button
                :loading="loading"
                size="medium"
                @click.native.prevent="handleLogin"
              >
                <span v-if="!loading">登 录</span>
                <span v-else>登 录 中...</span>
              </el-button>
              <div style="float: right" v-if="register">
                <router-link class="link-type" :to="'/register'">立即注册</router-link>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCodeImg } from "@/api/login";
import Cookies from "js-cookie";
import { encrypt, decrypt } from "@/utils/jsencrypt";

export default {
  name: "Login",
  data() {
    return {
      codeUrl: "",
      loginForm: {
        username: "",
        password: "",
        rememberMe: false,
        code: "",
        uuid: "",
      },
      loginRules: {
        username: [
          { required: true, trigger: "blur", message: "请输入您的账号" },
        ],
        password: [
          { required: true, trigger: "blur", message: "请输入您的密码" },
        ],
        code: [{ required: true, trigger: "change", message: "请输入验证码" }],
      },
      loading: false,
      // 验证码开关
      captchaEnabled: true,
      // 注册开关
      register: false,
      // 重定向地址
      redirect: undefined,
    };
  },
  watch: {
    $route: {
      handler: function (route) {
        this.redirect = route.query && route.query.redirect;
      },
      immediate: true,
    },
  },
  created() {
    this.getCode();
    this.getCookie();
  },
  methods: {
    getCode() {
      getCodeImg().then((res) => {
        this.captchaEnabled = res.captchaEnabled === undefined ? true : res.captchaEnabled;
        if (this.captchaEnabled) {
          this.codeUrl = res.img;
          this.loginForm.uuid = res.uuid;
        }
      }).catch(error => {
        console.error('获取验证码失败:', error);
      });
    },
    getCookie() {
      // 获取cookie
      const username = Cookies.get("username");
      const password = Cookies.get("password");
      const rememberMe = Cookies.get("rememberMe");
      this.loginForm = {
        username: username === undefined ? this.loginForm.username : username,
        password:
          password === undefined ? this.loginForm.password : decrypt(password),
        rememberMe: rememberMe === undefined ? false : Boolean(rememberMe),
      };
    },
    handleLogin() {
      this.$refs.loginForm.validate((valid) => {
        if (valid) {
          this.loading = true;
          if (this.loginForm.rememberMe) {
            //
            Cookies.set("username", this.loginForm.username, { expires: 30 });
            Cookies.set("password", encrypt(this.loginForm.password), {
              expires: 30,
            });
            Cookies.set("rememberMe", this.loginForm.rememberMe, {
              expires: 30,
            });
          } else {
            Cookies.remove("username");
            Cookies.remove("password");
            Cookies.remove("rememberMe");
          }
          this.$store
            .dispatch("Login", this.loginForm)
            .then(() => {
              this.$router.push({ path: this.redirect || "/" }).catch(() => {});
              // this.$router.push({ path: '/screen' }).catch(() => { });
            })
            .catch(() => {
              this.loading = false;
              if (this.captchaEnabled) {
                this.getCode();
              }
            });
        }
      });
    },
  },
};
</script>

<style rel="stylesheet/scss" lang="scss">
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-size: cover;
  width: 100%;
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    margin-left: -46%;
    background-image: url(../assets/svg/login-bg.svg);
    background-repeat: no-repeat;
    background-position: 100%;
    background-size: auto 100%;
    z-index: 1;
  }
  .container {
    display: flex;
    width: 100%;
    height: 100%;
    margin-left: auto;
    margin-right: auto;
    padding: 8px 40px;
    .container-left {
      position: relative;
      width: 50%;
      height: 100%;
      .logo {
        display: flex;
        align-items: center;
        width: 60%;
        height: 80px;
        padding-left: 8px;
        position: absolute;
        top: 12px;
        z-index: 2;
        transition: all 0.2s ease;
        cursor: pointer;
        img {
          width: 48px;
          height: 48px;
        }
        .logo-title {
          color: #fff;
          font-size: 24px;
          font-weight: 700;
          margin-left: 8px;
        }
      }
      .left-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100%;
        padding-left: 16px;
        margin-right: 16px;
        img {
          position: relative;
          width: 50%;
          vertical-align: middle;
          border-style: none;
          margin-top: -64px;
          z-index: 2; /* 适当的 z-index 值 */
        }
        .login-text {
          color: #fff;
          font-size: 40px;
          font-weight: 500;
          font-family: sans-serif;
          width: 50%;
          text-align: center;
          margin-top: 20px;
          z-index: 2;
        }
        .login-details {
          color: #fff;
          font-size: 16px;
          font-family: sans-serif;
          margin-top: 20px;
          z-index: 2;
        }
      }
    }
    .container-right {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      width: 50%;
      height: 100%;
      .form-content {
        width: 70%;
        margin-top: -45px;
        padding: 16px;
        .title {
          font-weight: 700;
          margin-bottom: 12px;
        }
        .login-form {
          padding: 16px 20px;
        }
        .login-code {
          display: flex;
          justify-content: flex-start;
          height: 40px;
          img {
            cursor: pointer;
            vertical-align: middle;
          }
          .login-code-img {
            height: 40px;
            width: auto;
          }
        }
      }
    }
  }
}

//媒体查询
@media screen and (min-width: 1750px) {
  .container {
    max-width: 1536px;
  }
}

@media screen and (min-width: 1536px) and (max-width: 1750px) {
  .container {
    max-width: 1200px;
  }
}

@media screen and (min-width: 780px) and (max-width: 1536px) {
  .container {
    max-width: 1024px;
  }
}

::v-deep.el-button {
  width: 100%;
  background-color: #0960bd;
  color: #fff;
  font-size: 16px;
  height: 40px;
  padding: 7px 15px;
  border-radius: 8px;
}

::v-deep .el-input {
  width: 100%;
  min-width: 0;
}
::v-deep .el-input--medium .el-input__inner {
  width: 100%;
  min-width: 0;
  height: 40px;
  padding: 7px 11px;
  font-size: 16px;
  line-height: 1.5;
  border-radius: 8px;
}

::v-deep .el-form-item {
  width: 100%;
  min-width: 0;
  margin-bottom: 24px;
  margin-left: 0;
  margin-right: 0;
}
</style>
