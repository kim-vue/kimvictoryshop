<template>
  <div class="inner-box">
    <div class="content-name">
      <h2 class="dp-ib">{{title}}</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button class="btn-size btn-blue fl_left" @click="goOpen">
          <span class="btn-icon">
            <i class="fas fa-pen-alt"></i>
          </span>
          조회
        </button>
        <button class="btn-size btn-gray fl_left" @click="save">
          <span class="btn-icon">
            <i class="fas fa-check"></i>
          </span>
          저장
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
            <b-select
              id="bselect"
              class="select is-fullwidth"
              v-model="form.compCd"
              disabled="true"
            >
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
      <div class="item desc-center">
        <div class="desc-item">
          <div class="desc-item">
            <div class="tit">
              <span class="label-tit">- 기준연월</span>
            </div>
            <div class="desc">
              <div class="datepicker w-type-ymd">
                <dhx-calendar class="input" v-model="form.acctmonth" :config="config" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="table-area">
      <div class="table-b">
        <div class="table-header">
          <div class="table-name">
            <h3 class="ico_table_name">유류단가 내역</h3>
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
        <dhx-grid
          class="acct-mng-grid"
          ref="grid"
          v-model="data"
          :config="config1"
          @constructGridSuccessful="constructGridSuccessful"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import DhxGrid from "@/components/DhxGrid.vue";
import DhxCalendar from "@/components/DhxCalendar.vue";
import GridNumberInput from "@/components/grid/GridNumberInput.vue";
import GridSelect from "@/components/grid/GridSelect.vue";

import mixin from "@/mixin";
import mixinSlip from "@/mixin/slip";

const bus = new Vue();

const options = {};
const lock = {};

function queryMngItemCd() {
  return new Promise((resolve, reject) => {
    if (options["OIL_KIND_CD"] !== undefined || lock["OIL_KIND_CD"]) {
      reject(false);
    } else {
      lock["OIL_KIND_CD"] = true;
      this.$store.commit("loading");
      this.$http
        .get("/api/code/detail", {
          params: {
            groupCd: "OIL_KIND_CD"
          }
        })
        .then(response => {
          options["OIL_KIND_CD"] = response.data;
          delete lock["OIL_KIND_CD"];
          bus.$emit("OIL_KIND_CD", response.data);
          return resolve(response);
        })
        .catch(response => {
          return reject(response);
        })
        .finally(() => {
          this.$store.commit("finish");
        });
    }
  });
}

export default {
  name: "oilPcePop",
  mixins: [mixin, mixinSlip],
  components: {
    DhxGrid,
    DhxCalendar
  },
  data() {
    return {
      title: "유류단가 관리",
      compCds: [],
      data: [],
      deletedata: "",
      config: {
        hideTime: false,
        format: "YYYY-MM",
        outputFormat: "YYYYMM"
      },
      form: {
        compCd: "",
        acctmonth: this.$moment().format("YYYYMM")
      },
      config1: {
        columns: [
          {
            id: "itemSeq",
            type: "cntr",
            align: "center",
            value: "No",
            width: 35
          },
          {
            id: "baseYm",
            align: "center",
            value: "기준연월",
            width: 75,
            type: "dhxCalendarA"
          },
          {
            id: "oilKindCd",
            align: "left",
            value: "유종",
            width: 95,
            component: GridSelect,
            mixin: {
              data() {
                return {
                  options: []
                };
              },
              created() {
                this.options = options["OIL_KIND_CD"];
                bus.$on("OIL_KIND_CD", () => {
                  this.options = options["OIL_KIND_CD"];
                });
              }
            }
          },
          {
            id: "oilUpce",
            align: "left",
            value: "유류단가",
            width: 95,
            component: GridNumberInput
          },
          {
            id: "oilEff",
            align: "left",
            value: "연비(Km)",
            width: 60,
            component: GridNumberInput
          },
          {
            id: "compCd",
            hide: true
          }
        ]
      }
    };
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setDateFormat("%Y-%m", "%Y%m");
    },
    getCompCdCombo() {
      this.$http
        .get(`/api/code/combo`, { params: { groupCd: "COMP_CD" } })
        .then(response => {
          // eslint-disable-next-line
          this.compCds = response.data;
        });

      this.form.compCd = this.$store.state.loginInfo.compCd;
      if (this.$store.state.loginInfo.authorities[0].authority === "ADMIN") {
        //ADMIN일경우 disabled 해제
        document.getElementById("bselect").removeAttribute("disabled");
      }
    },
    goOpen() {
      this.$http
        .post("/api/oilPrice/list", {
          compCd: this.form.compCd,
          baseYm: this.form.acctmonth
        })
        .then(response => {
          this.data = response.data;
        });
    },
    save() {
      //유종 중복 확인
      for (var i = 0; i < this.data.length; i++) {
        for (var j = i + 1; j < this.data.length; j++) {
          if (this.data[i].oilKindCd === this.data[j].oilKindCd && this.data[i].baseYm === this.data[j].baseYm) {
            this.$swal({
              type: "error",
              text: "해당 유종이 이미 존재합니다."
            });
            return false;
          }
        }
      }
        this.$http.post("/api/oilPrice/save", this.data).then(response => {
            this.$swal({ type: "success", text: response.data });
            this.goOpen();
            return;
        });
    },
    addRow() {
      this.data.push({
        baseYm: this.$moment().format("YYYYMM"),
        oilKindCd: options["OIL_KIND_CD"][0].detailCd,
        oilUpce: "",
        oilEff: "",
        compCd: this.$store.state.loginInfo.compCd
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
        const baseYm = this.data[rowIndex].baseYm
        const oilKindCd = this.data[rowIndex].oilKindCd

        this.data.splice(rowIndex, 1)

        if (!isNew) {
          this.$http.post('/api/oilPrice/delete', {
            baseYm,
            oilKindCd
          }).then(response => {
            // Do nothing!
          })
        }
      }
    },
    saveExcel() {
      this.downloadExcel(this.$refs.grid);
    }
  },
  created() {
    queryMngItemCd.apply(this, []);
  },
  mounted() {
    this.getCompCdCombo();
    this.goOpen();
  }
};
</script>