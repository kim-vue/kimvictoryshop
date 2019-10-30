<template>
  <div>
    <!--팝업-->
    <b-modal :active.sync="showAccountModal" has-modal-card @receive="receiveAccount">
        <account :slipTypeCd="slipTypeCd"></account>
    </b-modal>
    <b-modal :active.sync="showCctrModal" has-modal-card @receive="receiveCctr">
        <cctr></cctr>
    </b-modal>
    <!--//팝업 -->
  </div>
</template>
<script>
/* eslint-disable */
import _ from 'lodash'
// PopUp
import Account from '@/components/Account.vue';
import Cctr from '@/components/Cctr.vue';

export default {
  name: 'PopupGrid',
  components: { Account, Cctr },
  props: ['slipTypeCd'],
  data() {
    return {
      showAccountModal: false,
      showCctrModal: false,
      account: {},
      cctr: {},
      popupRowId: 0,
    };
  },
  methods: {
    popAccount(rId, cInd) {
      console.log(rId, cInd)
      // if(clear===true) this.account = {};
      this.showAccountModal = true;
    },
    popCctr(rId, cInd) {
      // if(clear===true) this.cctr = {};
      this.showCctrModal = true;
    },
    receiveAccount(obj) {
      this.$emit('returnValue', obj);
    },
    receiveCctr(obj) {
      this.$emit('returnValue', obj);
    },
    receiveObject(name, obj) {
      this[name] = obj;
    },
    initAccount() {
      if(this.account.acctNm === '') this.account = {};
    },
    initCctr() {
      if(this.cctr.cctrNm === '') this.cctr = {};
    },
    test() {
      console.log("왜 불러~~~")
    }
  },
  mounted() {
  },
  created() {
  }
};
</script>

<style>
</style>

