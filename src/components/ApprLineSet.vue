<template>
  <layout>
    <span slot="header">
      {{title}}
      <button class="btn-pop-close delete" aria-label="close" @click="closeModal"></button>
    </span>

    <div slot="content">
      <div class="table-area">
        <div class="table-b">
          <div class="table-header">
            <div class="table-name">
              <h3 class="ico_table_name">결재자 지정</h3>
            </div>
            <div class="btn-wrap btn-type1 clearfix fl_right" style="padding-right: 195px">
              <div class="dp-ib fl_left">
                <input type="radio" id="appr_radio01" v-model="apprTypeCd" value="20" />
                <label for="appr_radio01" class="NotoM">결재</label>
              </div>
              <div class="dp-ib fl_left">
                <input type="radio" id="appr_radio02" v-model="apprTypeCd" value="30" />
                <label for="appr_radio02" class="NotoM">합의</label>
              </div>
            </div>
          </div>
          <div
            id="treeBox"
            style="width:300px;height:350px;float:left; border-top:1px solid #c7c7c7; border-bottom:1px solid #c7c7c7; border-left:1px solid #c7c7c7; border-right:1px solid #c7c7c7;"
          ></div>

          <div class="grid-wrap" style="float:right;width: 50%;">
            <dhx-grid
              ref="gridEmp"
              v-model="empList"
              :config="config"
              @constructGridSuccessful="constructGridSuccessful"
            />
          </div>
        </div>
      </div>

      <div class="table-area">
        <div class="table-b">
          <div class="table-header">
            <div class="table-name">
              <h3 class="ico_table_name">결재선</h3>
            </div>
            <div class="btn-wrap btn-type2">
              <button class="btn-size btn-w-gray" @click="moveDown">
                <i class="fas fa-angle-down"></i>
              </button>
              <button class="btn-size btn-w-gray" @click="moveUp">
                <i class="fas fa-angle-up"></i>
              </button>
              <button class="btn-size btn-w-gray" @click="save">
                <i class="fas fa-pen-alt"></i> 저장
              </button>
              <button class="btn-size btn-w-gray" @click="addEmp">
                <i class="fas fa-check"></i> 추가
              </button>
              <button class="btn-size btn-w-gray" @click="cancel">
                <i class="far fa-trash-alt"></i> 삭제
              </button>
            </div>
          </div>
          <div class="grid-wrap">
            <dhx-grid
              ref="gridLine"
              v-model="form.lineList"
              :config="configLine"
              @constructGridSuccessful="constructGridSuccessfulLine"
            />
          </div>
        </div>
      </div>
    </div>
  </layout>
</template>

<script>
import Layout from "@/components/ModalSlot.vue";
import mixin from "@/mixin";
import mixinSlip from "@/mixin/slip";

import DhxGrid from "@/components/DhxGrid.vue";
import Emp from "@/components/Emp.vue";

export default {
  name: "ApprLineSet",
  mixins: [mixin, mixinSlip],
  components: { Layout, Emp, DhxGrid },

  props: ["lineList"],
  data() {
    return {
      config: {
        columns: [
          {
            id: "rn",
            type: "cntr",
            align: "center",
            sort: "na",
            value: "No.",
            width: 35
          },
          {
            id: "empNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "이름"
          },
          {
            id: "dutNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "직급"
          },
          {
            id: "empNo",
            type: "ro",
            align: "center",
            sort: "na",
            value: "사번"
          },
          {
            id: "cctrNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "부서명"
          },
          {
            id: "jobNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "직책명"
          }
        ],
        height: 350
      },
      configLine: {
        columns: [
          {
            id: "rn",
            type: "cntr",
            align: "center",
            sort: "na",
            value: "순서.",
            width: 35
          },
          {
            id: "aprverUser",
            type: "ro",
            align: "center",
            sort: "na",
            value: "이름"
          },
          {
            id: "jobNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "직책"
          },
          {
            id: "cctrNm",
            type: "ro",
            align: "center",
            sort: "na",
            value: "부서"
          },
          {
            id: "apprType",
            type: "ro",
            align: "center",
            sort: "na",
            value: "결재형식"
          },
          {
            id: "apprTypeCd",
            type: "ro",
            align: "center",
            sort: "na",
            value: "결재형식"
          },
          {
            id: "aprverId",
            type: "ro",
            align: "center",
            sort: "na",
            value: "사번"
          }
        ],
        height: 200
      },
      title: "결재선 지정",
      form: {
        lineList: []
      },
      apprTypeCd: "20",
      returnObject: {},
      empList: [],
      items: []
    };
  },
  methods: {
    constructGridSuccessful(grid) {
      let apprTypeNm;
      let outYn = "";
      grid.setColumnHidden(3, true);
      grid.setColumnHidden(4, true);
      grid.setColumnHidden(5, true);
      grid.attachEvent("onRowDblClicked", rId => {
        outYn = "N";
        if (this.apprTypeCd === "20") apprTypeNm = "결재";
        else if (this.apprTypeCd === "30") apprTypeNm = "합의";

        if (!this.checkDup(grid.cells(rId, 3).getValue())) return;

        this.form.lineList.push({
          aprverUser: grid.cells(rId, 1).getValue(),
          jobNm: grid.cells(rId, 5).getValue(),
          aprverId: grid.cells(rId, 3).getValue(),
          cctrNm: grid.cells(rId, 4).getValue(),
          apprTypeCd: this.apprTypeCd,
          apprType: apprTypeNm
        });
      });
    },
    constructGridSuccessfulLine(grid) {
      grid.setColumnHidden(5, true);
      grid.setColumnHidden(6, true);

      grid.attachEvent("onRowDblClicked", rId => {
        let index = rId - 1;
        let row = this.form.lineList[index];

        if (row.apprTypeCd === "10") {
          this.$swal({
            type: "warning",
            text: "선택하신 행은 삭제할 수 없습니다."
          });
        } else {
          this.form.lineList.splice(index, 1);
        }
      });
    },
    addEmp() {
      try {
        if (this.$refs.gridEmp.instance.getSelectedRowId() == null)
          throw "선택된 행이 없습니다.";
        let index = this.$refs.gridEmp.instance.getSelectedRowId() - 1;
        let row = this.empList[index];

        let apprTypeNm;

        if (this.apprTypeCd === "20") apprTypeNm = "결재";
        else if (this.apprTypeCd === "30") apprTypeNm = "합의";

        if (!this.checkDup(row.empNo)) return;

        this.form.lineList.push({
          aprverUser: row.empNm,
          jobNm: row.jobNm,
          aprverId: row.empNo,
          cctrNm: row.cctrNm,
          apprTypeCd: this.apprTypeCd,
          apprType: apprTypeNm
        });
      } catch (e) {
        this.$swal({
          type: "warning",
          text: e
        });
      }
    },
    cancel() {
      try {
        if (this.$refs.gridLine.instance.getSelectedRowId() == null)
          throw "선택된 행이 없습니다.";
        let index = this.$refs.gridLine.instance.getSelectedRowId() - 1;
        let row = this.form.lineList[index];

        if (row.apprTypeCd === "10") {
          this.$swal({
            type: "warning",
            text: "선택하신 행은 삭제할 수 없습니다."
          });
        } else {
          this.form.lineList.splice(index, 1);
        }
      } catch (e) {
        this.$swal({
          type: "warning",
          text: e
        });
      }
    },
    moveDown() {
      _process.apply(this, [0]);

      function _process(retry) {
        retry = retry || 0;

        try {
          let grid = this.$refs.gridLine.instance;
          let rId = grid.getSelectedRowId();
          if (rId === null) {
            // 선택된 행이 없음
            this.$swal({
              type: "warning",
              text: "선택된 행이 없습니다."
            });
          } else {
            let rowIndex = grid.getRowIndex(rId);
            if (rowIndex === 0) {
              this.$swal({
                type: "warning",
                text: "선택된 행은 이동 불가능합니다."
              });
              return;
            }

            let alterIndex =
              rowIndex + 1 >= this.form.lineList.length
                ? this.form.lineList.length - 1
                : rowIndex + 1;
            let data = this.form.lineList[rowIndex];

            this.form.lineList.splice(rowIndex, 1);
            this.form.lineList.splice(alterIndex, 0, data);

            setTimeout(() => {
              let alterId = grid.getRowId(alterIndex);
              grid.selectRowById(alterId);
            }, 100);
          }
        } catch (e) {
          if (retry < 3) {
            _process.apply(this, [retry + 1]);
          }
        }
      }
      // try {
      //     if (this.$refs.gridLine.instance.getSelectedRowId() == null)
      //         throw '선택된 행이 없습니다.'
      //     let index = this.$refs.gridLine.instance.getSelectedRowId() - 1
      //     let row = this.form.lineList[index]
      //
      //     let newPos = index + 1;
      //     if (index === 0)
      //         throw '선택하신 행은 이동 불가능합니다.'
      //
      //     const newContents = JSON.parse(JSON.stringify(this.form.lineList));
      //     if (newPos >= this.form.lineList.length) newPos = this.form.lineList.length;
      //
      //     newContents.splice(index, 1);
      //     newContents.splice(newPos, 0, row);
      //     this.form.lineList = newContents;
      //
      //     this.$refs.gridLine.instance.selectRow(newPos)
      // }
      // catch (e) {
      //     this.$swal({
      //         type: 'warning',
      //         text: e
      //     })
      // }
    },
    moveUp() {
      _process.apply(this, [0]);

      function _process(retry) {
        retry = retry || 0;

        try {
          let grid = this.$refs.gridLine.instance;
          let rId = grid.getSelectedRowId();
          if (rId === null) {
            // 선택된 행이 없음
            this.$swal({
              type: "warning",
              text: "선택된 행이 없습니다."
            });
          } else {
            let rowIndex = grid.getRowIndex(rId);
            let alterIndex = rowIndex - 1 < 0 ? 0 : rowIndex - 1;

            if (alterIndex === 0) {
              this.$swal({
                type: "error",
                text: "첫번째 행으로 이동 불가능합니다."
              });
              return;
            }

            let data = this.form.lineList[rowIndex];
            this.form.lineList.splice(rowIndex, 1);
            this.form.lineList.splice(alterIndex, 0, data);

            setTimeout(() => {
              let alterId = grid.getRowId(alterIndex);
              grid.selectRowById(alterId);
            }, 100);
          }
        } catch (e) {
          if (retry < 3) {
            _process.apply(this, [retry + 1]);
          }
        }
      }
      // try {
      //     if (this.$refs.gridLine.instance.getSelectedRowId() == null)
      //         throw '선택된 행이 없습니다.'
      //     let index = this.$refs.gridLine.instance.getSelectedRowId() - 1
      //     let row = this.form.lineList[index]
      //
      //     let newPos = index - 1;
      //     if (index === 0)
      //         throw '선택하신 행은 이동 불가능합니다.'
      //     if (newPos === 0)
      //         throw '첫번쨰 행으로 이동 불가능합니다.'
      //
      //     const newContents = JSON.parse(JSON.stringify(this.form.lineList));
      //     if (newPos >= this.form.lineList.length) newPos = this.form.lineList.length;
      //
      //     newContents.splice(index, 1);
      //     newContents.splice(newPos, 0, row);
      //     this.form.lineList = newContents;
      //
      //     this.$refs.gridLine.instance.selectRow(newPos)
      // }
      // catch (e) {
      //     this.$swal({
      //         type: 'warning',
      //         text: e
      //     })
      // }
    },
    save() {
      if (
        this.form.lineList[this.form.lineList.length - 1].apprTypeCd === "30"
      ) {
        this.$swal({
          type: "warning",
          text: "마지막 결재형식은 합의가 될 수 없습니다."
        });
        return;
      }
      this.returnObject.name = "apprLine";
      this.returnObject.lineList = this.form.lineList;
      this.$parent.$emit("receive", this.returnObject);
      this.$emit("close", this.returnObject);
      this.closeModal();
    },
    closeModal() {
      this.$parent.close();
    },
    checkDup(emp) {
      let outYn = "N";
      _.forEach(this.form.lineList, v => {
        if (v.aprverId === emp) {
          outYn = "Y";
          return;
        }
      });
      if (outYn === "Y") {
        this.$swal({ type: "info", text: "이미 결재선에 존재합니다." });
        return false;
      }
      return true;
    },
    goEmpList(deptCd) {
      this.$store.commit("loading");
      this.$http.get(`/api/emp/dept/${deptCd}`).then(response => {
        if (response.data) {
          this.empList = response.data;
        }
      });
    },
    drawTree() {
      this.$http.get(`/api/appr/detail/approvalLine`).then(response => {
        this.items = response.data;

        let arr = [];
        _.forEach(response.data, v => {
          v.text = v.cctrNm;
          v.id = v.cctrCd;
          if (!v.upperCd) {
            arr.push(v);
          } else {
            makeChildren(arr, v);
          }
        });

        function makeChildren(arr, value) {
          let result = undefined;
          if (Array.isArray(arr) && arr.length > 0) {
            _.forEach(arr, v => {
              if (v.cctrCd === value.upperCd) {
                v.items = v.items || [];
                v.items.push(value);
                result = true;
                return false;
              } else if (Array.isArray(v.items) && v.items.length > 0) {
                let r = makeChildren(v.items, value);
                if (r !== undefined) {
                  result = r;
                  return false;
                }
              }
            });
          }
          return result;
        }

        this.items = arr;
        const tree = new dhtmlXTreeView({
          parent: "treeBox",
          items: this.items,
          iconset: "font_awesome"
        });

        _.forEach(response.data, v => {
          if (v.id) {
            tree.setItemIcons(v.id, {
              file: "fas fa-user",
              folder_opened: "fas fa-users",
              folder_closed: "fas fa-user"
            });
          }
        });

        tree.attachEvent("onClick", id => {
          this.goEmpList(tree.items[id].id);
        });

        let openList = [];
        openParent(response.data, this.$store.state.loginInfo.loginDeptCd);

        function openParent(treeItem, value) {
          _.forEach(treeItem, v => {
            if (v.upperCd) {
              if (v.id === value) {
                openList.unshift({ cd: v.upperCd });
                openParent(treeItem, v.upperCd);
              }
            }
          });
        }

        _.forEach(openList, v => {
          tree.openItem(v.cd);
        });
        this.goEmpList(this.$store.state.loginInfo.loginDeptCd);
      });
    }
  },
  created() {
    Object.assign(this.form.lineList, this.lineList);
  },
  mounted() {
    this.drawTree();
  }
};
</script>

<style scoped>
.desc-content .item.desc-left .desc-item .td-s-thumb.search-area input {
  float: left;
}

.desc-content .item.desc-left .desc-item .desc.select select {
  width: 70%;
}

.search-area input {
  position: relative;
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

.table-area {
  width: 620px;
}

.btn-wrap,
.modal .pop-content .btn-type1 {
  margin-bottom: 0px;
}

.table-b {
  margin-bottom: 20px;
}
</style>