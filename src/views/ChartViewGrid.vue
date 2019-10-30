 <template>
  <div class="inner-box">
    <div class="content-name">
      <h2 class="dp-ib">{{title}}</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button class="btn-size btn-blue fl_left" @click="goOpen">
          <span class="btn-icon">
            <i class="fas fa-pen-alt"></i>
          </span> 조회
        </button>
        <button class="btn-size btn-gray fl_left" @click="save">
          <span class="btn-icon">
            <i class="fas fa-check"></i>
          </span> 저장
        </button>
      </div>
    </div>
    <!-- 검색조건 영역 -->
    <div class="desc-content search-border">
      <div class="item desc-left">
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 회사</span>
          </div>
          <div class="desc">
            <b-select id="bselect" class="select is-fullwidth" v-model="form.compCd" disabled = "true">
              <option
                v-for="item in compCds"
                :key="item.key"
                :value="item.key"
                v-text="item.value"
              />
            </b-select>
          </div>
        </div>
      </div>
      <div class="item desc-left">
          <div class="desc-item">
            <div class="tit">
              <span class="label-tit">- 세금 코드/명</span>
            </div>
            <div class="desc">
              <!-- <input class="input Rt-M tal" type="text" id="account_cd" v-model="form.codeNm" /> -->
            </div>
          </div>
      </div>
    </div>
    <!-- Grid영역 -->
    <div class="table-area">
      <div class="table-b">
        <div class="table-header">
          <div class="table-name">
            <h3 class="ico_table_name">세금코드 관리</h3>
          </div>
          <div class="btn-wrap btn-type2 clearfix">
            <button class="btn-size btn-w-gray" @click="addRow">
              <span class="btn-icon">
                <i class="fas fa-plus"></i>
              </span>행추가
            </button>
            <button class="btn-size btn-w-gray" @click="deleteRow">
              <span class="btn-icon">
                <i class="fas fa-trash-alt"></i>
              </span>행삭제
            </button>
            <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
          </div>
        </div>
      </div>
    </div>
    <dhx-grid class="tax-mng-grid" ref="grid" v-model="data" :config="config" />
  </div>
</template>

<script>
import Vue from "vue";
import dhxGrid from "@/components/DhxGrid.vue";
import GridSelect from "@/components/grid/GridSelect.vue";
import mixin from "@/mixin/slip-common";
import GridNumberInput from '@/components/grid/GridNumberInput.vue'
import mixinSlip from '@/mixin/slip';
// import GridCheckbox from '@/components/grid/GridCheckbox.vue'
import _ from 'lodash'

var eventBus = new Vue();

const options = {};

var queryEvdTypeCd_run = false;

function queryTpsTypeCd() {
  if (options["evdTypeCd"] === undefined && !queryEvdTypeCd_run) {
    queryEvdTypeCd_run = true;
    this.$http
      .get("/api/code/detail", {
        params: {
          groupCd: "EVD_TYPE_CD"
        }
      })
      .then(response => {
        var datas = {};
        datas[0] = { detailCd: "initial", detailNm: "--선택--", detailRealNm: ""}
        for (var i = 0; i < response.data.length; i++) {
          datas[i + 1] = {
            detailCd: response.data[i].detailCd,
            originNm: response.data[i].detailNm,
            detailNm: "[" + response.data[i].detailCd + "] " + response.data[i].detailNm,
            detailRealNm: response.data[i].detailNm
          };
        }
        options["evdTypeCd"] = datas;
      })
      .catch(response => {
        options["evdTypeCd"] = undefined;
        return response;
      })
      .finally(() => {
        eventBus.$emit("evdTypeCd.updated");
        queryEvdTypeCd_run = false;
      });
  }
}

export default {
  name: "taxMng",
  mixins: [mixin, mixinSlip],
  components: { dhxGrid },
  data() {
    return {
      title: "세금코드 관리",
      compCds: [],
      deleteid: [],
      form: {
        compCd: "",
        codeNm: ""
      },
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
            id: "taxCd",
            type: "ed",
            align: "center",
            sort: "na",
            value: "세금코드",
            width: 80
          },
          {
            id: "taxNm",
            type: "ed",
            align: "left",
            sort: "na",
            value: "세금명칭",
            width: 180
          },
          {
            id: "taxRt",
            align: "center",
            sort: "na",
            value: "세율",
            width: 30,
            type:"ed"
          },
          {
            id: "useYn",
            align: "center",
            sort: "na",
            value: "사용여부",
            width: 60,
            component: GridCheckbox
          },
          {
            id: "orderSeq",
            align: "center",
            sort: "na",
            value: "정렬순서",
            width: 60,
            component: GridNumberInput
          },
          {
            id: "machineId",
            align: "left",
            sort: "na",
            value: "증빙유형코드",
            width: 150,
            component: GridSelect, 
            mixin: {
              data() {
                return {
                  options: [] 
                };
              },
              created() {
                this.options = options["machineId"];

                eventBus.$on('machineId.updated', () => {
                this.options = options['machineId']
              })
              },
            }
          },
          // {
          //   id: "evdTypeNm",
          //   type: "ro",
          //   align: "left",
          //   sort: "na",
          //   value: "증빙유형명",
          //   width: 150
          // },
          {
            id: "ref1",
            type: "ed",
            align: "left",
            sort: "na",
            value: "비고1",
            width: 100
          },
          {
            id: "ref2",
            type: "ed",
            align: "left",
            sort: "na",
            value: "비고2",
            width: 100
          },
          {
            id: "ref3",
            type: "ed",
            align: "left",
            sort: "na",
            value: "비고3",
            width: 100
          },
          {
            id: "compCd",
            type: "ro",
            align: "left",
            sort: "na",
            value: "compcode",
            hide: true
          }
        ],
        events:{
          onEditCell(stage, rId, cInd, nValue, oValue) {
            if (stage === 2 && cInd === 3) {
              if(isNaN(parseInt(nValue))){
                return false
              }
              if (nValue > 100) {
                return false
              }
              
            }//비율 100까지만 입력
            return true
          },
          onCellChanged(rId, cInd, nValue){
            let row = this.data[this.instance.getRowIndex(rId)]
            let colDef = this.options.columns[cInd]
            if(cInd === 6){
              this.evdTypeNm = options['evdTypeCd'].originNm
            }
          }
        },
          afterRefreshData(grid, data){
              if (grid !== undefined && Array.isArray(data)) {
            this.$nextTick(() => {
              _.forEach(data, (row, index) => {
                let rId = grid.getRowId(index)
                this.unlockCell(rId, 1)
                if (row.new) {
                  //this.setColumnClassName(rId, [1, 2], 'bg-lightpink')
                } else {
                  this.lockCell(rId, 1)
                }
              })
            })
          }
          }
      },
      selected: [],
      data: [{}]
    };
  },
  created() {
    queryTpsTypeCd.apply(this, []);
  },
  methods: {
    save() {
      for(var i = 0;i<this.data.length;i++){
        for(var j = i+1; j<this.data.length;j++){
          if(this.data[i].taxCd === this.data[j].taxCd){
            this.$swal({type: 'warning', text: '해당 세금코드가 이미 존재합니다. 중복코드 : ' + this.data[i].taxCd});
            return false;
          }
        }
      }
        this.$http.post('/api/taxes/save',  this.data)
      .then(response =>{
        this.$swal({ type: 'success', text: '저장되었습니다' });
        this.goOpen()
      })

    },
    addRow() {
      this.data.push({
        taxCd: "",
        taxNm: "",
        taxRt: 0,
        useYn: "Y",
        orderSeq: "0",
        evdTypeCd: "initial",
        ref1: "",
        ref2: "",
        ref3: "",
        compCd: this.$store.state.loginInfo.compCd,
        new: true
      });
    },
    deleteRow() {
      const rId = this.$refs.grid.instance.getSelectedRowId()
      if (rId === null) {
        this.$swal({
          type: 'error',
          text: '삭제할 행을 선택하여주세요.'
        })
      } else {
        const rowIndex = this.$refs.grid.instance.getRowIndex(rId)
        const isNew = this.data[rowIndex].new
        const taxCd = this.data[rowIndex].taxCd

        this.data.splice(rowIndex, 1)

        if (!isNew) {
          this.$http.post('/api/taxes/delete', {
            taxCd
          }).then(response => {
            // Do nothing!
          })
        }
      }
    },
    saveExcel() {
      this.downloadExcel(this.$refs.grid);
    },
    getCompCdCombo() {
      this.$http
        .get(`http://197.200.11.176:8081/api/customer/es/machineList/CUST0001`, { params: { groupCd: "equipNm" } })
        .then(response => {
          // eslint-disable-next-line
		  this.compCds = response.data;
		  console.log('comCds:',compCds);

        });

        this.form.compCd = this.$store.state.loginInfo.compCd;
      if (this.$store.state.loginInfo.authorities[0].authority === "ADMIN") {
        //ADMIN일경우 disabled 해제
        document.getElementById("bselect").removeAttribute("disabled");
      }
    },
    

    goOpen() {
      this.$http
        .post(`/api/taxes/list`, 
        { 
          compCd: this.compCds.key,
          taxCd: this.form.codeNm
        })
        .then(response => {
          this.data = response.data;
        });
    },

  },
  mounted() {
    this.getCompCdCombo();
    this.goOpen();
  }
};
</script>

<style lang="scss" scoped>
.tax-mng-grid {
  :global(.gridbox) {
    height: 50vh !important;
  }
}

.gridbox {
  height: 200px !important;
}
.gridbox .objbox {
  height: 350px !important;
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