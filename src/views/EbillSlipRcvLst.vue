<template>
  <div class="inner-box">
    <div class="content-name">
      <h2 class="dp-ib">{{title}}</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button class="btn-size btn-blue fl_left" @click="goSearch">
          <span class="btn-icon">
            <i class="fas fa-pen-alt"></i>
          </span> 조회
        </button>
      </div>
    </div>

    <!-- 검색조건 영역 -->
    <div class="desc-content search-border">
      <div class="item desc-left">
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 공급일자</span>
          </div>
          <div class="desc">
            <div class="datepicker w-type-ymd02">
              <dhx-calendar class="input ddate sDate" v-model="form.issueDateFrom" />
            </div>
            <span class="wave">~</span>
            <div class="datepicker w-type-ymd02">
              <dhx-calendar class="input ddate sDate" v-model="form.issueDateTo" />
            </div>
          </div>
        </div>
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 소속부서</span>
          </div>
          <div class="desc">
            <div class="td-s-thumb search-area" style="width: 300px">
              <input
                class="input input-bg"
                type="text"
                style="width:100px;"
                v-model="form.ipDeptcode1"
                disabled
              />
              <div class="ip-box ip-box-w02" style="width:120px;">
                <input
                  class="input"
                  type="text"
                  v-model="form.ipDeptname1"
                  @input="initCctr"
                  @keydown.enter="popCctr"
                />
                <button class="icon is-right" @click="popCctr(true)">
                  <i class="fas fa-search"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="item desc-center">
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 공급자</span>
          </div>
          <div class="desc">
            <input class="input Rt-M tal" type="text" v-model="form.suName" />
          </div>
        </div>
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 승인번호</span>
          </div>
          <div class="desc">
            <input class="input Rt-M tal" type="text" v-model="form.issueId" />
          </div>
        </div>
      </div>
      <div class="item desc-right">
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 처리상태</span>
          </div>
          <div class="desc">
            <b-select class="select is-fullwidth" v-model="form.dealStatCd">
              <option value>==전체==</option>
              <option
                v-for="item in dealStats"
                :key="item.key"
                :value="item.key"
                v-text="item.value"
              />
            </b-select>
          </div>
        </div>
      </div>
    </div>
    <!-- //검색조건 영역 -->

    <!-- 테이블 -->
    <div class="table-area">
      <div class="table-b">
        <div class="table-header">
          <div class="table-name">
            <h3 class="ico_table_name">수신내역</h3>
          </div>
          <div class="btn-wrap btn-type1 clearfix">
            <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
          </div>
        </div>
        <div class="grid-wrap">
          <dhx-grid
            ref="grid"
            v-model="rcvList"
            :config="config"
            @constructGridSuccessful="constructGridSuccessful"
          />
        </div>
      </div>
    </div>
    <!-- //테이블 -->

    <!--팝업-->
    <b-modal :active.sync="showCctrModal" has-modal-card @receive="receiveCctr">
      <cctr :param="form.wrtDeptNm"></cctr>
    </b-modal>
    <!--//팝업 -->
  </div>
</template>

<script>
import mixin from "@/mixin";
import mixinSlip from "@/mixin/slip";
import _ from "lodash";

import DhxCalendar from "@/components/DhxCalendar.vue";
import DhxGrid from "@/components/DhxGrid.vue";
import Cctr from "@/components/Cctr.vue";
import Emp from "@/components/Emp.vue";

export default {
  name: "SlipList",
  mixins: [mixin, mixinSlip],
  components: { Cctr, Emp, DhxCalendar, DhxGrid },
  data() {
    return {
      config: {
        columns: [
          {
            id: "no",
            type: "cntr",
            align: "center",
            sort: "na",
            value: "No.",
            width: 35
          },
          {
            id: "issueId",
            type: "ro",
            align: "center",
            sort: "na",
            value: "전자세금계산서<br>승인번호",
            width: 200
          },
          {
            id: "dealStatNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "처리상태",
            width: 70
          },
          {
            id: "issueDate",
            type: "ro",
            align: "center",
            sort: "na",
            value: "공급일자",
            width: 100
          },
          {
            id: "eaSlipNo",
            type: "ro",
            align: "center",
            sort: "na",
            value: "전표번호",
            width: 120
          },
          {
            id: "statusNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "전표상태",
            width: 100
          },
          {
            id: "suName",
            type: "ron",
            align: "left",
            sort: "na",
            value: "공급자",
            width: 150
          },
          {
            id: "suId",
            type: "ron",
            align: "center",
            sort: "na",
            value: "#cspan",
            width: 120
          },
          {
            id: "suIndtype",
            type: "ron",
            align: "left",
            sort: "na",
            value: "#cspan",
            width: 140
          },
          {
            id: "chargetotal",
            type: "ron",
            align: "right",
            sort: "na",
            value: "금액",
            width: 120
          },
          {
            id: "taxtotal",
            type: "ron",
            align: "right",
            sort: "na",
            value: "#cspan",
            width: 120
          },
          {
            id: "grandtotal",
            type: "ron",
            align: "right",
            sort: "na",
            value: "#cspan",
            width: 120
          },
          {
            id: "dtiTypeNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "세금계산서<br>종류",
            width: 130
          },
          {
            id: "amendName",
            type: "ro",
            align: "left",
            sort: "na",
            value: "수정사유",
            width: 140
          },
          {
            id: "bpName",
            type: "ro",
            align: "center",
            sort: "na",
            value: "수탁사업자",
            width: 100
          },
          {
            id: "bpId",
            type: "ro",
            align: "center",
            sort: "na",
            value: "#cspan",
            width: 100
          },
          {
            id: "ipName",
            type: "ro",
            align: "center",
            sort: "na",
            value: "공급받는자",
            width: 100
          },
          {
            id: "ipMin",
            type: "ro",
            align: "center",
            sort: "na",
            value: "#cspan",
            width: 100
          },
          {
            id: "ipEmail1",
            type: "ro",
            align: "left",
            sort: "na",
            value: "#cspan",
            width: 180
          },
          {
            id: "ipPersname1",
            type: "ro",
            align: "center",
            sort: "na",
            value: "#cspan",
            width: 100
          },
          {
            id: "ipDeptname1",
            type: "ro",
            align: "center",
            sort: "na",
            value: "#cspan",
            width: 100
          },
          { id: "compCd", type: "ro", align: "center", sort: "na", value: "" },
          { id: "bpCd", type: "ro", align: "center", sort: "na", value: "" },
          {
            id: "issueDate",
            type: "ro",
            align: "center",
            sort: "na",
            value: ""
          },
          { id: "invSeq", type: "ro", align: "center", sort: "na", value: "" }
        ],
        height: 390,
        enablePaging: true,
        pagingSize: 8,
        afterRefreshData(grid, data) {
          this.$nextTick(() => {
            _.forEach(data, (item, index) => {
              let rId = index + 1;
              grid
                .cells(rId, 3)
                .setValue(
                  this.$moment(grid.cells(rId, 3).getValue()).format(
                    "YYYY-MM-DD"
                  )
                );
            });
          });
        }
      },
      title: "전자세금계산서 매입내역",
      dealStats: [],
      rcvList: [],
      form: {
        issueDateFrom: this.$moment()
          .startOf("month")
          .format("YYYY-MM-DD"),
        issueDateTo: this.$moment().format("YYYY-MM-DD"),
        ipDeptcode1: "",
        ipDeptname1: "",
        suName: "",
        issueId: "",
        dealStatCd: ""
      },
      showCctrModal: false,
      showEmpModal: false
    };
  },
  methods: {
    constructGridSuccessful(grid) {
      this.config.queryPage(0);
      grid.setNumberFormat("0,000", 9, ".", ",");
      grid.setNumberFormat("0,000", 10, ".", ",");
      grid.setNumberFormat("0,000", 11, ".", ",");
      grid.setColumnHidden(21, true);
      grid.setColumnHidden(22, true);
      grid.setColumnHidden(23, true);
      grid.setColumnHidden(24, true);
      grid.attachHeader([
        "#rspan",
        "#rspan",
        "#rspan",
        "#rspan",
        "#rspan",
        "#rspan",
        "회사",
        "사업자등록번호",
        "업종",
        "공급가액",
        "부가세액",
        "합계금액",
        "#rspan",
        "#rspan",
        "회사",
        "사업자등록번호",
        "회사",
        "종사업장",
        "E-Mail",
        "담당자",
        "부서"
      ]);
      grid.attachEvent("onRowDblClicked", rId => {
        let compCd = grid.cells(rId, 21).getValue();
        let bpCd = grid.cells(rId, 22).getValue();
        let issueDate = grid.cells(rId, 23).getValue();
        let invSeq = grid.cells(rId, 24).getValue();
        let eaSlipNo = grid.cells(rId, 4).getValue();
        this.goPage({ eaSlipNo, xml: { compCd, bpCd, issueDate, invSeq } });
      });
    },
    getDealStatCombo() {
      this.$http
        .get(`/api/code/combo`, { params: { groupCd: "DEAL_STAT_CD" } })
        .then(response => {
          this.dealStats = response.data;
        });
    },
    saveExcel() {
      this.downloadExcel(this.$refs.grid);
    },
    goPage(params) {
      //this.$router.push({path: `/billSlipMng/${params.eaSlipNo}`});
      // this.$router.push({name: 'ebillSlipReg', params: params});
      /*        if(params.eaSlipNo != '') {
                            this.$router.push({ path: `/ebillSlipReg/${params.eaSlipNo}` });
                            // this.$router.push({ path: `/billSlipQry/${params.eaSlipNo}` });
                        } else {
                            this.$router.push({ name: 'ebillSlipReg', params: params });
                        }*/
      console.log("페이지이동", params);
      let targetName =
        !params.eaSlipNo || params.slipStatCd === "10"
          ? "ebillSlipReg"
          : "billSlipMng";
      this.$router.push({ name: targetName, params: params });
    },
    goSearch() {
      console.log("조회...");
      const param = JSON.parse(JSON.stringify(this.form));
      const stripFields = ["issueDateFrom", "issueDateTo"];
      _.forEach(stripFields, name => (param[name] = this.toPure(param[name])));
      // 임시로 조건 삭제
      param.ipDeptname1 = "";

      if (!this.validation(param)) return;

      this.$store.commit("loading");
      this.$http.post(`/api/ebill/rcv-list`, param).then(response => {
        if (response.data) {
          // set data
          this.rcvList = response.data;
          //this.$refs.grid.attachHeader(["#rspan", "#rspan", "#rspan", "#rspan", "#rspan", "#rspan", "회사", "사업자등록번호", "업종", "공급가액", "부가세액", "합계금액", "#rspan", "#rspan", "회사", "사업자등록번호", "회사", "종사업장", "E-Mail", "담당자", "부서"]);
          // this.grid.data.forEach((item, index, array) => {
          //     let rowId =(new Date()).valueOf();
          //     this.$refs.grid.addRow(rowId,"");
          //     this.$refs.grid.setRowData(rowId, item);
          // });
          //this.setGridStyle();
          // this.adjustGridColumns(this.$refs.grid);
          this.$store.commit("finish");
        }
      });
    },
    validation(param) {
      if (!param.issueDateFrom || !param.issueDateTo) {
        this.$swal({ type: "warning", text: "공급일자를 입력해 주세요." });
        return false;
      }
      return true;
    },
    popCctr(clear) {
      if (clear === true) {
        this.form.ipDeptcode1 = "";
        this.form.ipDeptname1 = "";
      }
      this.showCctrModal = true;
    },
    receiveCctr(obj) {
      this.form.ipDeptcode1 = obj.cctrCd;
      this.form.ipDeptname1 = obj.cctrNm;
    },
    initCctr(force) {
      if (force === true) this.form.ipDeptname1 = "";
      if (this.form.ipDeptname1 === "") this.form.ipDeptcode1 = "";
    }
  },
  mounted() {
    this.form.ipDeptcode1 = this.$store.state.loginInfo.loginDeptCd;
    this.form.ipDeptname1 = this.$store.state.loginInfo.loginDeptNm;
    this.getDealStatCombo();
    this.goSearch();
  }
};
</script>

<style scoped>
.gridbox {
  height: 470px !important;
}

.desc-content:after {
  clear: both;
  content: "";
  display: block;
}

.btn-wrap {
  margin-bottom: 20px;
}

.desc-content {
  border: 2px solid #9db6c9;
  background: #f9fafc;
  margin: 0 0 20px 0;
  border-radius: 4px;
  padding: 15px 2%;
  clear: both;
}

.desc-content .item {
  float: left;
}

.desc-content .item .desc-item {
  position: relative;
  padding-left: 82px;
  margin-bottom: 8px;
}

.desc-content .item .desc-item:last-child {
  margin-bottom: 0;
  height: 25px;
}

.desc-content .item .desc-item .tit {
  position: absolute;
  left: 0;
}

.desc-content .item .desc-item .label-tit {
  font-family: "NotoM";
  color: #222;
  font-size: 15px;
}

.desc-content .item.desc-left .desc-item {
  padding-left: 90px;
}

.desc-content .item.desc-left .desc-item .desc:after {
  clear: both;
  content: "";
  display: block;
}

.desc-content .item.desc-left .desc-item .desc .datepicker {
  float: left;
}

.desc-content .item.desc-left .desc-item .desc span.wave {
  float: left;
  padding: 0 6px;
}

.desc-content .item.desc-left .desc-item .td-s-thumb.search-area:after {
  clear: both;
  content: "";
  display: block;
}

.desc-content .item.desc-left .desc-item .td-s-thumb.search-area input,
.desc-content .item.desc-left .desc-item .td-s-thumb.search-area .ip-box {
  float: left;
}

.desc-content .item.desc-left .desc-item .desc.select select {
  width: 70%;
}

.desc-content .item.desc-left {
  width: 35%;
  padding-right: 40px;
}

.desc-content .item.desc-center {
  width: 35%;
  padding-right: 40px;
}

.desc-content .item.desc-right {
  width: 30%;
}

.search-area input {
  position: relative;
}

.search-area .icon {
  position: absolute;
  right: 8px;
  top: 1px;
  z-index: 100;
  cursor: pointer;
  font-size: 16px;
  color: #555;
}

.search-border .td-s-thumb {
  position: relative;
  display: inline-block;
}

.search-border .td-s-thumb.search-area > input,
.search-border
  .td-s-thumb.search-area
  > .ip-box
  .search-border
  .td-s-thumb.search-area
  > button {
  float: left;
}

.search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
  width: 60%;
  margin-left: 6px;
}

.remove_text {
  margin-left: 0;
}

.contents div.gridbox_material.gridbox .xhdr {
  border-bottom: 1px solid #dfdfdf;
}

@media (max-width: 1580px) {
  .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
    width: 50%;
  }
}
</style>
