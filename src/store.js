import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';

Vue.use(Vuex);

export default new Vuex.Store({
    plugins: [createPersistedState()],
    state: {
        loginInfo: {
            userName: '',
            loginId: '',
            loginPw: '',
            loginCompCd: '',
            token: '',
            authorities: [],
            menus: [],
        },
        isLoading: false,
    },
    mutations: {
        login(state, loginInfo) {
            state.loginInfo = loginInfo;
        },
        logout(state) {
            state.loginInfo = null;
        },
        loading(state) {
            state.isLoading = true;
        },
        finish(state) {
            state.isLoading = false;
        }

    },
});
