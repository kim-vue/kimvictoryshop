<template>
<div>
  <h1 class="title">전자전표 프로젝트</h1>
  <br />
  <div class="box">
    <ul>
      <li @keydown.enter="popVendor">
        <b-field label="거래처">
          <b-input type="text" v-model="vendor.vendCd" style="width:50px;" disabled></b-input>
          <b-input type="text" v-model="vendor.vendNm" style="width:200px;" @input="initVendor"></b-input>
          <b-button type="is-success" @click="popVendor(true)">Search</b-button>
        </b-field>
      </li>
      <li @keydown.enter="popAccount">
        <b-field label="계정코드">
          <b-input type="text" v-model="account.acctCd" style="width:100px;" disabled></b-input>
          <b-input type="text" v-model="account.acctNm" style="width:200px;" @input="initAccount"></b-input>
          <b-button type="is-success" @click="popAccount(true)">Search</b-button>
        </b-field>
      </li>
      <li @keydown.enter="popCctr">
        <b-field label="비용부서">
          <b-input type="text" v-model="cctr.cctrCd" style="width:100px;" disabled></b-input>
          <b-input type="text" v-model="cctr.cctrNm" style="width:200px;" @input="initCctr"></b-input>
          <b-button type="is-success" @click="popCctr(true)">Search</b-button>
        </b-field>
      </li>
      <li @keydown.enter="popEmp">
        <b-field label="임직원">
          <b-input type="text" v-model="emp.empNo" style="width:100px;" disabled></b-input>
          <b-input type="text" v-model="emp.empNm" style="width:200px;" @input="initEmp"></b-input>
          <b-button type="is-success" @click="popEmp(true)">Search</b-button>
        </b-field>
      </li>
      <li @keydown.enter="popIo">
        <b-field label="IO">
          <b-input type="text" v-model="io.ioCd" style="width:100px;" disabled></b-input>
          <b-input type="text" v-model="io.ioNm" style="width:200px;" @input="initIo"></b-input>
          <b-button type="is-success" @click="popIo(true)">Search</b-button>
        </b-field>
      </li>
        <li @keydown.enter="popIoc">
        <b-field label="IOC">
          <b-input type="text" v-model="io.cctrCd" style="width:100px;" disabled></b-input>
          <b-input type="text" v-model="io.cctrNm" style="width:200px;" disabled></b-input>
          <b-button type="is-success" @click="popIoc(true)">Search</b-button>
        </b-field>
      </li>
    </ul>
  </div>
  <div class="box">
    <ul>
      <li>
        <a @click="popMessage"><span class="button">Message 팝업</span></a>
      </li>
      <li>
        <b-field grouped>
          <b-field label="증빙유형">
            <b-select v-model="form.evdType">
              <option v-for="item in evdTypes" :key="item.key" :value="item.key" v-text="item.value" />
            </b-select>
          </b-field>
          <b-field label="정산구분">
            <b-radio v-for="item in stlFgs" :key="item.key" :native-value="item.key" v-model="form.stlFg">
              {{item.value}}
            </b-radio>
          </b-field>
        </b-field>
      </li>
    </ul>

    <b-modal :active.sync="showVendorModal" has-modal-card @receive="receiveObject">
      <vendor :param="vendor.vendNm" :slipTypeCd="slipTypeCd"></vendor>
    </b-modal>
    <b-modal :active.sync="showAccountModal" has-modal-card @receive="receiveObject">
      <account :param="account.acctNm" :slipTypeCd="slipTypeCd"></account>
    </b-modal>
    <b-modal :active.sync="showCctrModal" has-modal-card @receive="receiveObject">
      <cctr :param="cctr.cctrNm"></cctr>
    </b-modal>
    <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveObject">
      <emp :param="emp.empNm"></emp>
    </b-modal>
    <b-modal :active.sync="showIoModal" has-modal-card @receive="receiveIoObject">
       <io :param="io.ioNm"></io>
    </b-modal>
    <b-modal :active.sync="showIoModal1" has-modal-card @receive="receiveIocObject">
        <io :param="io.cctrNm"></io>
    </b-modal>
  </div>

  <div class="inner-box">
    <dhx-grid grid-name="Grid1" v-model="header" :config="config_header" @constructGridSuccessful="constructGridSuccessful"></dhx-grid>
  </div>

</div>
</template>

<script>
// import ModalForm from '@/views/ModalForm.vue';
import Vendor from '@/components/Vendor.vue';
import Account from '@/components/Account.vue';
import Cctr from '@/components/Cctr.vue';
import Emp from '@/components/Emp.vue';
import Io from '@/components/IO.vue';
import mixin from '@/mixin';

import DhxGrid from '@/components/DhxGrid.vue'
import GridNumber from '@/components/grid/GridNumberInput.vue'
import GridCheckbox from '@/components/grid/GridCheckbox.vue'

export default {
  name: 'TestMain',
  components: {
    Vendor,
    Account,
    Cctr,
    Emp,
    Io,
    DhxGrid
  },
  mixins: [mixin],
  data() {
    return {
      header: [{
        col1: 'T1',
        col2: 'T2'
      }],
      children: [],
      config_header: {
        columns: [{
          id: 'col1',
          value: 'TestHeader1'
        }, {
          id: 'col2',
          value: 'TestHeader2'
        }],
        enablePaging: true,
        // 그리드 데이터 익스체인지 메소드
        queryPage: (page) => {
          page = page || 0
          return new Promise((resolve, reject) => {
            var data = {
              contents: [],
              page: page,
              totalPages: 3,
              totalElements: 0
            }
            resolve({
              data: data
            })
          })
        }
      },
      evdTypes: [],
      stlFgs: [],
      slipTypeCd: 'E3',
      form: {
        evdType: '31',
        stlFg: 'N',
      },
      showVendorModal: false,
      showAccountModal: false,
      showCctrModal: false,
      showEmpModal: false,
      showIoModal: false,
      showIoModal1: false,
      vendor: {
        vendCd: '',
        vendNm: '',
      },
      account: {
        acctCd: '',
        acctNm: '',
      },
      cctr: {
        cctrCd: '',
        cctrNm: '',
      },
      emp: {
        empNo: '',
        empNm: '',
      },
      io: {
        ioCd: '',
        ioNm: '',
        cctrCd: '',
        cctrNm: '',
       }
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      /**
       * Grid data 초기화!!
       */
      this.config_header.queryPage(0)
    },
    testButton() {
      console.log(JSON.stringify(this.data))
    },
    popMessage() {
      this.$swal({
        animation: false,
        type: 'warning',
        text: '메세지 팝업 테스트',
      });
    },
    popVendor(clear) {
      if (clear === true) this.vendor = {};
      this.showVendorModal = true;
    },
    popAccount(clear) {
      if (clear === true) this.account = {};
      this.showAccountModal = true;
    },
    popCctr(clear) {
      if (clear === true) this.cctr = {};
      this.showCctrModal = true;
    },
    popEmp(clear) {
      if (clear === true) this.emp = {};
      this.showEmpModal = true;
    },
    popIo(clear) {
      if(clear===true) {
        this.io.ioCd = '';
        this.io.ioNm = '';
      };
      this.showIoModal = true;
    },
    popIoc(clear) {
      if(clear===true) {
        this.io.cctrCd = '';
        this.io.cctrNm = '';
      };
      this.showIoModal1 = true;
    },
    // 증빙유형
    getEvdType() {
      this.$http
        .get("/api/code/combo", {
          params: {
            groupCd: "EVD_TYPE_CD",
            remark1: this.slipTypeCd
          }
        })
        .then(response => {
          this.evdTypes = response.data;
        });
    },
    // 정산유형
    getStlFg() {
      this.$http
        .get("/api/code/combo", {
          params: {
            groupCd: "STL_FG_CD"
          }
        })
        .then(response => {
          this.stlFgs = response.data;
        });
    },
    receiveObject(obj) {
      this[obj.name] = obj;
    },
    receiveIoObject(obj) {
      this.io.ioCd = obj.ioCd;
      this.io.ioNm = obj.ioNm;
    },
    receiveIocObject(obj) {
      this.io.cctrCd = obj.cctrCd;
      this.io.cctrNm = obj.cctrNm;
    },
    initVendor() {
      if (this.vendor.vendNm === '') this.vendor = {};
    },
    initAccount() {
      if (this.account.acctNm === '') this.account = {};
    },
    initCctr() {
      if (this.cctr.cctrNm === '') this.cctr = {};
    },
    initEmp() {
      if (this.emp.empNm === '') this.emp = {};
    },
    initIo() {
          if(this.io.ioNm === '') this.io = {};
        },
  },
  mounted() {
    this.getEvdType();
    this.getStlFg();
  },
};
</script>

<style scoped>
li {
  text-align: left;
  line-height: 3em;
}
</style>
