<template>
    <div class="table-b">
        <div class="table-header">
            <div class="table-name">
                <h3 class="ico_table_name">{{title}}</h3>
            </div>
            <div class="btn-wrap btn-type2">
                <button class="btn-size btn-w-gray" @click="clearGrid"><span class="btn-icon"><i class="fas fa-redo"></i></span>초기화</button>
                <button class="btn-size btn-w-gray" @click="addRow"><span class="btn-icon"><i class="fas fa-plus"></i></span>행추가</button>
                <button class="btn-size btn-w-gray" @click="deleteRow"><span class="btn-icon"><i class="fas fa-trash-alt"></i></span>행삭제</button>
            </div>
        </div>
        <div class="grid-wrap" ref="test">
            <div ref="grid" id="gridbox" class="grid-tbl-box grid-slip"></div>
        </div>

        <popup-grid ref="pop" :slipTypeCd="form.slipTypeCd" @returnValue="setCellValue"></popup-grid>

    </div>
</template>
<script>
/* eslint-disable */
import Vue from 'vue';
import mixin from '@/mixin';
import mixinSlip from '@/mixin/slip';
import _ from 'lodash'

import PopupGrid from '@/components/PopupGrid.vue';

export default {
  name: 'SlipGrid',
  components: { PopupGrid },
  props: ['slipDetails','form'],
  mixins: [ mixin, mixinSlip ],
  data() {
    return {
      title: '세부항목',
      grid: {
        head: [
          {id: 'itemSeq', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
          {id: 'dcNm', type: 'ro', align: 'center', sort: 'na', value: '유형', width: 40},
          {id: 'taxCd', type: 'ro', align: 'center', sort: 'na', value: '세금코드', width: 60},
          {id: 'ioNo', type: 'ro', align: 'center', sort: 'na', value: 'IO', width: 40},
          {id: 'cctrCd', type: 'ro', align: 'center', sort: 'na', value: '귀속부서', width: 100},
          {id: 'cctrNm', type: 'ed', align: 'left', sort: 'na', value: '귀속부서명', width: 120},
          {id: 'cctrSrch', type: 'ro', align: 'center', sort: 'na', value: '#cspan', width: 40},
          {id: 'acctCd', type: 'ro', align: 'center', sort: 'na', value: '계정코드', width: 80},
          {id: 'acctNm', type: 'ed', align: 'left', sort: 'na', value: '계정명', width: 140},
          {id: 'acctSrch', type: 'ro', align: 'center', sort: 'na', value: '#cspan', width: 40},
          {id: 'bdgAmt', type: 'ron', align: 'right', sort: 'na', value: '잔여예산', width: 80},
          {id: 'debitAmt', type: 'edn', align: 'right', sort: 'na', value: '차변금액', width: 90},
          {id: 'creditAmt', type: 'edn', align: 'right', sort: 'na', value: '대변금액', width: 90},
          {id: 'lnSgtxt', type: 'ed', align: 'left', sort: 'na', value: '적요'},
          {id: 'dcCd', type: 'ro', align: 'center', sort: 'na', value: '', width: 0},
          {id: 'lnTypeCd', type: 'ro', align: 'center', sort: 'na', value: '', width: 0},
        ],
        data: [],
      },
      line: {
        creditAcctCd: '',
        creditAcctNm: '',
        debitAcctCd: '',
        debitAcctNm: '',
      },
      popup: {
        rId: -1,
        cInd: -1,
      },
      searchDept: "<button class='icon fl_right' onclick='popCctr();'><i class='fas fa-search'></i></button>",
      searchAcct: "<button class='icon fl_right' onclick='popAccount();'><i class='fas fa-search'></i></button>",
      rowCount: 0,
      showVatLine: true,
      isSyncAmt: true,
      // 잔여예산
      rmnBudget: 0,
    };
  },
  methods: {
    getVatAccount() {
      this.$http.get(`/api/account/vat`)
          .then(response => {
            if(response.data) {
              this.line.debitAcctCd = response.data.acctCd;
              this.line.debitAcctNm = response.data.acctNm;

              if(!this.$parent.viewMode) {
                  this.setInitGrid();
              }
            }
          });
    },
    drawGrid() {
      // eslint-disable-next-line
      const iljinGrid = new dhtmlXGridObject('gridbox');
      this.$refs.grid = iljinGrid;

      iljinGrid.attachHeader(["합계","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#stat_total","#stat_total","","",""]);
      iljinGrid.setNumberFormat("0,000",10,'.',',');
      iljinGrid.setNumberFormat("0,000",11,'.',',');
      iljinGrid.setNumberFormat("0,000",12,'.',',');
      iljinGrid.setColumnHidden(14,true);
      iljinGrid.setColumnHidden(15,true);
      iljinGrid.enableEditEvents(true,false,true);  // click, dblclick, F2key

      iljinGrid.init();
      iljinGrid.parse(this.grid,"js");
      iljinGrid.enableAutoWidth(true);
      iljinGrid.enableAutoHeight(false);

      iljinGrid.attachEvent("onCellChanged", (rId,cInd,nValue) => {
        if(cInd === 11 || cInd === 12) {
          const debitAmt = _.toNumber(_.reduce(iljinGrid.collectValues(11), (a, b) => { return _.toNumber(a) + _.toNumber(b); }));
          const creditAmt = _.toNumber(_.reduce(iljinGrid.collectValues(12), (a, b) => { return _.toNumber(a) + _.toNumber(b); }));

          if(debitAmt === creditAmt) {
            this.isSyncAmt = true;
          } else {
            this.isSyncAmt = false;
          }
        }

        if(cInd === 4 || cInd === 7) {
          const dcCd = this.$refs.grid.cells(rId,14).getValue();
          const lnTypeCd = this.$refs.grid.cells(rId,15).getValue();
          const cctrCd = this.$refs.grid.cells(rId,4).getValue();
          const acctCd = this.$refs.grid.cells(rId,7).getValue();

          if(dcCd === 'D' && lnTypeCd === 'ITEM') {
            this.getRemainBudget(rId, cctrCd,acctCd);
          }
        }

      });
      iljinGrid.attachEvent("onEnter", (rId,cInd) => {
        if(cInd === 11) this.calcDebitAmt(rId);
      });
      iljinGrid.attachEvent("onRowSelect", (rId, cInd) => {
        console.log("셀위치 [", rId, cInd, "]", this.$refs.grid.cells(rId,14).getValue(), this.$refs.grid.cells(rId,15).getValue(), this.$refs.grid.getRowData(rId))
        this.popup.rId = rId;
        this.popup.cInd = cInd;
      });

    },
    calcDebitAmt(rId) {
      const debitAmt = _.toNumber(_.reduce(this.$refs.grid.collectValues(11), (a, b) => { return _.toNumber(a) + _.toNumber(b); }));
      const creditAmt = _.toNumber(_.reduce(this.$refs.grid.collectValues(12), (a, b) => { return _.toNumber(a) + _.toNumber(b); }));

      // 차변금액 자동계산
      let overAmt = debitAmt - creditAmt;
      const rowsNum = this.$refs.grid.getRowsNum();
      for(var i=rowsNum-1; i >=0; i--) {
        var rowId = this.$refs.grid.getRowId(i);
        var dcCd = this.$refs.grid.cells2(i,14).getValue();
        var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

        if(rId !== rowId && dcCd === 'D' && lnTypeCd === 'ITEM') {
          let targetAmt = this.$refs.grid.cells2(i,11).getValue();
          if(overAmt > 0) { // 행이 추가된 경우
            if(targetAmt > overAmt) {
              this.$refs.grid.cells2(i,11).setValue(targetAmt - overAmt);
              break;
            } else {
              let remain = overAmt - targetAmt;
              this.$refs.grid.cells2(i,11).setValue(targetAmt - remain);
              overAmt -= remain;
            }
          } else {  // 행이 삭제된 경우
            this.$refs.grid.cells2(i,11).setValue(targetAmt - overAmt);
            break;
          }
        }
      }
      this.refreshGrid();
    },
    refreshGrid() {
      this.$refs.grid.callEvent('ongridreconstructed',[]);
    },
    getNewRowId() {
      return ++this.rowCount;
    },
    setInitGrid(force) {
      this.setDefaultLine(1);

      if(force) {
        this.setTaxCd();
        this.setBaseDept();
        this.setCreditAccount();
        this.setHdSgtxt();
        this.setSupAmt();
        this.setVatAmt();
        this.setEtcAmt();
        this.setTotAmt();
      }
    },
    setDefaultLine(expItemCnt) {
      this.addRow({ dcCd: 'C', lnTypeCd: 'ITEM', acctCd: this.form.apAcctCd, acctNm: this.form.apAcctNm, search: false });
      if(!this.$parent.hideVat) {
        this.addRow({ dcCd: 'D', lnTypeCd: 'TAX', acctCd: this.line.debitAcctCd, acctNm: this.line.debitAcctNm, search: false });
      }
      for(var i=0; i<expItemCnt; i++) {
        this.addRow({ dcCd: 'D', lnTypeCd: 'ITEM', search: true });
      }
    },
    setGridStyle() {
      this.doLineAction(this.$refs.grid, {
        credit: (grid,rId) => grid.lockRow(rId, true),
        vat: (grid,rId) => grid.lockRow(rId, true),
        cost: (grid,rId) => {
          this.setCellClassName(grid, rId, [5,6,8,9,11,13], 'bg-lightpink');
          grid.cells(rId,12).setDisabled(true);
        },
        all: (grid,rId) => {
          this.setCellClassName(grid, rId, [5, 8, 13], 'tal');
          this.setCellClassName(grid, rId, [10, 11, 12], 'tar');
        }
      });
    },
    clearGrid() {
      this.$refs.grid.clearAll();
      this.setInitGrid(true);
    },
    addRow(data) {
      const rId = this.getNewRowId();
      this.$refs.grid.addRow(rId, [
        null,
        data.dcCd === 'C'?'대변':'차변',
        this.form.taxCd,
        null,
        this.form.baseDeptCd,
        this.form.baseDeptNm,
        data.search == false? null : this.searchDept,
        data.acctCd,
        data.acctNm,
        data.search == false? null : this.searchAcct,
        null,
        null,
        null,
        this.form.hdSgtxt,
        data.dcCd ? data.dcCd : 'D',
        data.lnTypeCd ? data.lnTypeCd : 'ITEM'
      ]);
      this.setGridStyle();

      return rId;
    },
    deleteRow() {
      const rowsNum = this.$refs.grid.getRowsNum();
      const tax = this.$parent.taxes.find(x => x.taxCd == this.form.taxCd);
      let maxRowNum = 3;

      if(tax && tax.taxRt === 0) maxRowNum = 2;

      if(rowsNum > maxRowNum) {
        var lastRowId = this.$refs.grid.getRowId(rowsNum-1);
        if(lastRowId) {
          this.$refs.grid.deleteRow(lastRowId);
          this.calcDebitAmt(lastRowId);
        }
      } else {
        this.$swal({ type: 'info', text: '더 이상 삭제할 수 없습니다.' });
        return;
      }
    },
    setTaxCd() {
      const rowsNum = this.$refs.grid.getRowsNum();
      for(var i=0; i <rowsNum; i++) {
        this.$refs.grid.cells2(i,2).setValue(this.form.taxCd);
      }

      // 부가세율에 따른 로우 삭제처리
      const tax = this.$parent.taxes.find(x => x.taxCd == this.form.taxCd);

      if(tax) {
        if(tax.taxRt === 0) {
          this.form.vatAmt = 0;
          this.$emit('setHideVat', true);

          for(var i=rowsNum-1; i >=0; i--) {
            var rowId = this.$refs.grid.getRowId(i);
            var dcCd = this.$refs.grid.cells2(i,14).getValue();
            var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

            if(dcCd === 'D' && lnTypeCd === 'TAX') {
              this.$refs.grid.deleteRow(rowId);
              this.showVatLine = false;
            }
          }
          this.changeRowId(this.$refs.grid);
        } else {
          // 부가세 로우 추가
          if(!this.showVatLine) {
            var rowId = this.addRow({ dcCd: 'D', lnTypeCd: 'TAX', acctCd: this.line.debitAcctCd, acctNm: this.line.debitAcctNm, search: false });
            this.changeRowId(this.$refs.grid);
            this.$refs.grid.moveRowTo(this.$refs.grid.getRowsNum(),1,"move");
          }
          this.$emit('setHideVat', false);
          this.showVatLine = true;
        }
      }
    },
    setBaseDept() {
      const rowsNum = this.$refs.grid.getRowsNum();
      for(var i=0; i <rowsNum; i++) {
        this.$refs.grid.cells2(i,4).setValue(this.form.baseDeptCd);
        this.$refs.grid.cells2(i,5).setValue(this.form.baseDeptNm);
      }
    },
    setVatAccount() {
      const rowsNum = this.$refs.grid.getRowsNum();
      for(var i=0; i <rowsNum; i++) {
        var dcCd = this.$refs.grid.cells2(i,14).getValue();
        var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

        if(dcCd === 'D' && lnTypeCd === 'TAX') {
          this.$refs.grid.cells2(i,7).setValue(this.line.debitAcctCd);
          this.$refs.grid.cells2(i,8).setValue(this.line.debitAcctNm);
        }
      }
    },
    // 대변계정이 선택될 경우
    setCreditAccount() {
      const rowsNum = this.$refs.grid.getRowsNum();
      if(rowsNum > 0) {
        for(var i=0; i <rowsNum; i++) {
          var dcCd = this.$refs.grid.cells2(i,14).getValue();
          var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

          if(dcCd === 'C' && lnTypeCd === 'ITEM') {
            this.$refs.grid.cells2(i,7).setValue(this.form.apAcctCd);
            this.$refs.grid.cells2(i,8).setValue(this.form.apAcctNm);
          }
        }
      } else {
          console.log('setCreditAccount    !@!@')
          // else 경우 setInitGrid 호출하는 이유?
          // this.setInitGrid();
      }
    },
    setHdSgtxt() {
      if(this.$refs.grid) {
        const rowsNum = this.$refs.grid.getRowsNum();
        for(var i=0; i <rowsNum; i++) {
          this.$refs.grid.cells2(i,13).setValue(this.form.hdSgtxt);
        }
      }
    },
    setSupAmt() {
      if(this.$refs.grid) {
        const amt = _.parseInt(this.toPure(this.form.supAmt)||0) + _.parseInt(this.toPure(this.form.etcAmt)||0);

        const rowsNum = this.$refs.grid.getRowsNum();
        for(var i=0; i <rowsNum; i++) {
          var dcCd = this.$refs.grid.cells2(i,14).getValue();
          var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

          if(dcCd === 'D' && lnTypeCd === 'ITEM') {
            this.$refs.grid.cells2(i,11).setValue(amt);
          }
        }
      }
    },
    setVatAmt() {
      if(this.$refs.grid && this.$refs.grid.getRowsNum() > 0) {
        const rowsNum = this.$refs.grid.getRowsNum();
        for(var i=0; i <rowsNum; i++) {
          var dcCd = this.$refs.grid.cells2(i,14).getValue();
          var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

          if(dcCd === 'D' && lnTypeCd === 'TAX') {
            this.$refs.grid.cells2(i,11).setValue(this.toPure(this.form.vatAmt));
          }
        }
      }
    },
    setEtcAmt() {
      this.setSupAmt();
    },
    setTotAmt() {
      if(this.$refs.grid && this.$refs.grid.getRowsNum() > 0) {
        const rowsNum = this.$refs.grid.getRowsNum();
        for(var i=0; i <rowsNum; i++) {
          var dcCd = this.$refs.grid.cells2(i,14).getValue();
          var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();

          if(dcCd === 'C' && lnTypeCd === 'ITEM') {
            this.$refs.grid.cells2(i,12).setValue(this.toPure(this.form.totAmt));
          }
        }
        this.refreshGrid();
      }
    },
    setCellValue(data) {
      if(this.$refs.grid) {
        if(data.name === 'account') {
          this.$refs.grid.cells(this.popup.rId,7).setValue(data.acctCd);
          this.$refs.grid.cells(this.popup.rId,8).setValue(data.acctNm);
        } else if(data.name === 'cctr') {
          this.$refs.grid.cells(this.popup.rId,4).setValue(data.cctrCd);
          this.$refs.grid.cells(this.popup.rId,5).setValue(data.cctrNm);
        }
      }
    },
    getRemainBudget(rId, cctrCd, acctCd) {
      if(rId && cctrCd && acctCd && this.form.postDt !== '') {
        this.$http.get(`/api/budget/remain`, { params: {postDt: this.toPure(this.form.postDt), cctrCd: cctrCd, acctCd: acctCd} })
            .then(response => {
                this.form.rmnBudget = _.toInteger(response.data);
                this.setRemainBudget(rId)
            });
      }
    },
    setRemainBudget(rId) {
      this.$refs.grid.cells(rId,10).setValue(this.form.rmnBudget);
    },
    setRemainBudgetAll() {
      const rowsNum = this.$refs.grid.getRowsNum();
      for(var i=0; i <rowsNum; i++) {
        var rowId = this.$refs.grid.getRowId(i);
        var dcCd = this.$refs.grid.cells2(i,14).getValue();
        var lnTypeCd = this.$refs.grid.cells2(i,15).getValue();
        var cctrCd = this.$refs.grid.cells2(i,4).getValue();
        var acctCd = this.$refs.grid.cells2(i,7).getValue();

        if(dcCd === 'D' && lnTypeCd === 'ITEM') {
          this.getRemainBudget(rowId, cctrCd, acctCd)
        }
      }
    },
    validation() {
      // 계정, 금액입력 확인
      const rowsNum = this.$refs.grid.getRowsNum();
      for(var i=0; i <rowsNum; i++) {
        var rowId = this.$refs.grid.getRowId(i);
        var debitAcctCd = this.$refs.grid.cells2(i,7).getValue();
        var debitAmt = this.$refs.grid.cells2(i,11).getValue();
        var dcCd = this.$refs.grid.cells2(i,14).getValue();

        if(!debitAcctCd) {
          this.$swal({ type: 'warning', text: '계정을 선택해 주세요.' });
          this.$refs.grid.selectRow(rowId);
          return false;
          break;
        } else if(dcCd === 'D' && _.toInteger(debitAmt) == 0) {
          this.$swal({ type: 'warning', text: '차변금액을 입력해 주세요.' });
          this.$refs.grid.selectRow(rowId);
          return false;
          break;
        }
      }

      if(!this.isSyncAmt) { this.$swal({ type: 'warning', text: '차변금액과 대변금액이 일치하지 않습니다.\n차변금액을 조정해 주세요.' }); return false; }

      return true;
    },
    setSlipDetails() {
      if(this.slipDetails.length > 0) {
        setTimeout(() => {
          this.$refs.grid.clearAll();
          this.setDefaultLine(this.$parent.slipHeader.expItemCnt);

          this.slipDetails.forEach((item, index, array) => {
            if(item.dcCd === 'C') {
              item.creditAmt = item.acctAmt;
            } else if(item.dcCd === 'D') {
              item.debitAmt = item.acctAmt;
            }
            this.$refs.grid.setRowData(this.$refs.grid.getRowId(index), item);
          });
          this.grid.data = this.slipDetails;
          this.refreshGrid();
        }, 100);
      }
    },
  },
  watch: {
    slipDetails() {
      this.setSlipDetails();
    },
    'form.taxCd'() {
      this.setTaxCd();
    },
    'form.baseDeptCd'() {
      this.setBaseDept();
    },
    'line.debitAcctCd'() {
      this.setVatAccount();
    },
    'form.apAcctCd'() {
      this.setCreditAccount();
    },
    'form.postDt'() {
      this.setRemainBudgetAll();
    },
    'form.hdSgtxt'() {
      this.setHdSgtxt()
    },
    'form.supAmt'() {
      this.setSupAmt()
    },
    'form.vatAmt'() {
      this.setVatAmt()
    },
    'form.etcAmt'() {
      this.setEtcAmt()
    },
    'form.totAmt'() {
      this.setTotAmt()
    },
  },
  mounted() {
    window.popCctr = () => this.$refs.pop.popCctr(this.popup.rId, this.popup.cInd);
    window.popAccount = () => this.$refs.pop.popAccount(this.popup.rId, this.popup.cInd);

    this.drawGrid();
  },
  created() {
    this.getVatAccount();
  }
};
</script>

<style scoped>
.gridbox{height: 258px!important;}
.gridbox .objbox{height:185px!important;}
</style>

