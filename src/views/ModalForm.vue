<template>
  <div>
    <!-- <form action> -->
    <div class="modal-card" style="width: auto">
      <header class="modal-card-head">
        <p class="modal-card-title">결재선 관리</p>
      </header>

      <section class="modal-card-body">
        <div id="top">
          <b-field label="사원정보"></b-field>
          <Employee ref="Employee"/>
        </div>

        <div class="spacer"></div>

        <div>
          <button class="button is-small is-danger" @click="removeApproval">
            <b-icon pack="fa" icon="angle-double-up"></b-icon>
          </button>
          &nbsp;
          <button class="button is-small is-info" @click="addApproval">
            <b-icon pack="fa" icon="angle-double-down"></b-icon>
          </button>
        </div>

        <div class="spacer"></div>

        <div id="down">
          <b-field label="결재선"></b-field>
          <div id="gridbox" class="grid"/>
        </div>
      </section>

      <footer class="modal-card-foot">
        <!-- <button class="button" type="button" @click="$parent.close()">Close</button> -->
        <div class="column">
          <button class="button is-info is-pulled-right" @click="saveApproval()">저장</button>
        </div>
      </footer>
    </div>
    <!-- </form> -->
  </div>
</template>
<script>
import Employee from "@/components/Employee.vue";

export default {
  name: "ModalForm",
  components: {
    Employee
  },
  methods: {
    validate(newEmpNo) {
      // 결재선 동일 사번 불허
      const rowsCnt = this.$refs.approvals.getRowsNum();

      for (let idx = 0; idx < rowsCnt; idx += 1) {
        const rowId = this.$refs.approvals.getRowId(idx);
        const rowData = this.$refs.approvals.getRowData(rowId);
        if (newEmpNo === rowData.loginId) {
          throw Error(
            `동일한 사번이 결재선에 이미 존재합니다. 사번: ${newEmpNo}`
          );
        }
      }
    },
    // 결재선 변경 시 순서 값 변경
    updateApprovalSeq() {
      const rowsCnt = this.$refs.approvals.getRowsNum();

      for (let idx = 0; idx < rowsCnt; idx += 1) {
        const rowId = this.$refs.approvals.getRowId(idx);
        const rowData = this.$refs.approvals.getRowData(rowId);
        rowData.seq = idx + 1;
        this.$refs.approvals.setRowData(rowId, rowData);
      }
    },
    // 결재선 라인 제거
    removeApproval() {
      const rowId = this.$refs.approvals.getSelectedRowId();
      if (rowId === null) {
        this.$snackbar.open({
          message: "결재선에서 선택된 항목이 없습니다.",
          type: "is-warning",
          position: "is-top",
          actionText: "닫기",
          indefinite: true
        });
      } else {
        this.$refs.approvals.deleteRow(rowId);
      }
    },
    // 결재선 라인 추가
    addApproval() {
      const rowId = this.$refs.employees.getSelectedRowId();
      this.$refs.employees.clearSelection();
      if (rowId === null) {
        this.$snackbar.open({
          message: "사원정보에서 선택된 항목이 없습니다.",
          type: "is-warning",
          position: "is-top",
          actionText: "닫기",
          indefinite: true
        });
      } else {
        const employee = this.$refs.employees.getRowData(rowId);

        const newItem = {
          seq: 0,
          approverId: "",
          attribute1: "",
          approvalType: null,
        };
        // TODO HEADER 및 DETAIL 추가
        newItem.seq = this.$refs.approvals.getRowsNum() + 1;
        newItem.approverId = employee.loginId;
        newItem.attribute1 = employee.userName;
        try {
          this.validate(newItem.loginId);
          this.$refs.approvals.addRow(newItem.loginId, [
            newItem.seq,
            newItem.approverId,
            newItem.attribute1,
            newItem.approvalType
          ]);

          this.grid.data.push(newItem);
        } catch (e) {
          this.$snackbar.open({
            message: `${e.toString()}`,
            type: "is-danger",
            position: "is-top",
            actionText: "닫기",
            indefinite: true
          });
        }
      }
    },
    // 결재선 라인 저장
    saveApproval() {

      this.$parent.$parent.grid.splice(0, this.$parent.$parent.grid.length);

      for (const line of this.grid.data) {
        this.$parent.$parent.grid.push(line);
      }

      // this.$emit("approvalLine");
      this.$parent.close();
    }
  },

  data() {
    // 이해를 돕기 위한 샘플 데이터
    return {
      grid: {
        head: [
          {
            id: "seq",
            type: "ro",
            align: "center",
            sort: "str",
            value: "결재순서"
          },
          {
            id: "loginId",
            type: "ro",
            align: "center",
            sort: "str",
            value: "사번"
          },
          {
            id: "userName",
            type: "ro",
            align: "center",
            sort: "str",
            value: "사용자명"
          },
          {
            id: "approvalType",
            type: "coro",
            align: "center",
            sort: "int",
            value: "결재유형"
          }
        ],
        data: []
      }
    };
  },
  mounted() {
    // eslint-disable-next-line
    const iljinGrid = new dhtmlXGridObject("gridbox");
    iljinGrid.enableAutoWidth(true);
    iljinGrid.init();
    iljinGrid.enableDragAndDrop(true);
    iljinGrid.attachEvent("onDrop", () => {
      this.updateApprovalSeq();
    });

    // 결재유형
    const combo = iljinGrid.getCombo(3);
    combo.put("APPROVAL", "결재");
    combo.put("SUPPORT", "합의");
    combo.put("POST", "후열");

    iljinGrid.parse(this.grid, "js");
    this.$refs.approvals = iljinGrid;
  }
};
</script>

<style lang="scss" scoped>
#up {
  height: 40%;
}

#down {
  height: 40px;
}

.box {
  width: 100%;
  height: 100%;
}

.grid {
  max-width: 100%;
  min-height: 200px;
  -webkit-box-sizing: content-box;
  -moz-box-sizing: content-box;
  box-sizing: content-box;
}
</style>
