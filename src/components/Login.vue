<template>
    <section class="hero is-fullheight login">
        <div class="hero-body">
            <div class="container">
                <div class="columns is-centered">
                    <article class="card is-rounded">
                        <div class="card-content">
                            <h1 class="title">
                                <img src="img/bg_login_title.png" alt="">
                            </h1>
                            <p class="control has-icon">
                                <input v-model="loginInfo.loginId"
                                autocomplete="name"
                                class="input" type="text" name="username"
                                placeholder="사번" autofocus="">
                                <i class="fa fa-envelope"></i>
                            </p>
                            <p class="control has-icon">
                                <input v-model="loginInfo.loginPw"
                                autocomplete="new-password"
                                class="input" type="password" name="password"
                                placeholder="비밀번호" @keydown.enter="login">
                                <i class="fa fa-lock"></i>
                            </p>
                            <p class="control">
                                <button class="button is-fullwidth btn-login" @click="login">Login</button>
                            </p>
                        </div>
                    </article>
                </div>
            </div>
        </div>
        <!-- footer -->
        <div class="footer-login">
            <span class="copyright">COPYRIGHT © ILJIN ALL RIGHTS RESERVED.</span>
        </div>
        <!-- //footer-login -->
    </section>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginInfo: {
        loginId: '',
        loginPw: '',
        compCd: '',
          loginDeptNm: '',
          loginDeptCd: '',
          loginDutCd: '',
          loginDutNm: '',
          loginJobCd: '',
          loginJobNm: '',
        token: '',
        menu: [],
        authorities: [],
      },
    }
  },
  methods: {
    loginFail() {
      this.$swal({
        animation: false,
        type: 'error',
        text: `로그인 실패했습니다. ID 또는 비밀번호를 확인해 주세요.`,
      });
    },
    async login() {      
      try {
        this.$store.commit('loading');
        const response = await this.$http.post('/login', this.loginInfo);
        const loginInfo = {};
        loginInfo.userName = response.data.userName;
        loginInfo.loginId = response.data.loginId;
        loginInfo.compCd = response.data.loginCompCd;
        loginInfo.loginDeptNm = response.data.loginDeptNm;
        loginInfo.loginDeptCd = response.data.loginDeptCd;
        loginInfo.loginDutCd = response.data.loginDutCd;
        loginInfo.loginDutNm = response.data.loginDutNm;
        loginInfo.loginJobCd = response.data.loginJobCd;
        loginInfo.loginJobNm = response.data.loginJobNm;
        loginInfo.token = response.data.token;
        loginInfo.menu = response.data.menu;
        loginInfo.authorities = response.data.authorities;
        loginInfo.loginPw = 'Not Use';
        this.$store.commit('login', loginInfo);
        this.$cookie.set('loginInfo', JSON.stringify(loginInfo));
        this.$http.defaults.headers['x-auth-token'] = loginInfo.token;
        this.$store.commit('finish');
      } catch(err) {
        this.$store.commit('finish');
        this.loginFail();
      }
    },
  },
  created() {

    //모바일 iframe 메시지 수신을 통한 로그인 
    window.addEventListener('message', async event => {
      // console.log(event.data.id);
      if(event.origin === process.env.VUE_APP_MO_URL) {
        // console.log(`pc:event.origin : ${event.origin}`)
        if(event.data.message === 'isPcLogin') {

          const ret = this.$store.state.loginInfo !== null && this.$store.state.token !== '';
          window.parent.postMessage({ 
            message: 'pcLogin', 
            value: ret
          }, '*');
          console.log('pc:isPcLogin 수신 후 pcLogin' + ret + '보냄');

        } else if(event.data.message === 'login') {

          console.log('pc:login 하라는 메시지 받음');

          if(!this.$store.state.loginInfo) { //로그인 안되어있다면
            this.loginInfo.loginId = event.data.loginId;
            this.loginInfo.loginPw = event.data.loginPw;
            await this.login();        
            const ret = this.$store.state.loginInfo !== null && this.$store.state.token !== '';

            window.parent.postMessage({ 
              message: 'pcLogin', 
              value: ret
            }, '*');
            console.log('pc:현재 로그인 안되어있어서 로그인 시키고 pcLogin:' + ret + ' 메시지 보냄');

          } else {
            window.parent.postMessage({ 
              message: 'pcLogin', 
              value: true
            }, '*');
            console.log('pc:현재 로그인 되어있어서 pcLogin true 메시지 보냄');
          }
        }
      }
    })
  }
};
</script>
