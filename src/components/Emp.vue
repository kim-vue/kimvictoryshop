<template>
  <layout>
    <span slot="header">{{title}}<button class="btn-pop-close delete" aria-label="close" @click="closeModal"></button></span>
    <div slot="content">
      <div class="btn-type1">
          <button class="btn-size btn-gray" @click="goSearch(true)"><span class="btn-icon"><i class="fas fa-search"></i></span> 조회</button>
      </div>

      <div class="pop-content-search">
          <div class="field has-addons ">
              <div class="mr20 ">
                  <span class="pop-c-name">- 임직원 사번/성명/부서명</span>
              </div>
              <div class="control is-expanded">
                  <input class="input" type="text" v-model="search" @keydown.enter="goSearch">
              </div>
          </div>
      </div>

      <div class="grid-wrap">
          <div id="empGridbox" class="grid-tbl-box"></div>
      </div>
    </div>
  </layout>
</template>

<script>
import Layout from '@/components/ModalSlot.vue'
import mixin from '@/mixin';

export default {
  name: 'Emp',
  props: ['param'],
  mixins: [ mixin ],
  data() {
    return {
      title: '임직원 조회',
      search: '',
      grid: {
        head: [
          {id: 'no', type: 'cntr', align: 'center', sort: 'int', value: 'No.'},
          {id: 'empNo', type: 'ro', align: 'center', sort: 'str', value: '사번'},
          {id: 'empNm', type: 'ro', align: 'center', sort: 'str', value: '성명'},
          {id: 'titleNm', type: 'ro', align: 'center', sort: 'str', value: '호칭'},
          {id: 'deptNm', type: 'ro', align: 'left', sort: 'str', value: '부서명'},
          {id: 'dutNm', type: 'ro', align: 'left', sort: 'str', value: '직급명', hidden:true},
          {id: 'compCd', type: 'ro', align: 'center', sort: 'na', value: '회사코드', hidden:true},
          {id: 'compNm', type: 'ro', align: 'center', sort: 'na', value: '회사명', hidden:true},
        ],
        data: [],
      },
      returnObject: {}
    }
  },
  methods: {
    drawGrid() {
      // eslint-disable-next-line
      const iljinGrid = new dhtmlXGridObject('empGridbox');
      this.$refs.grid = iljinGrid;
      iljinGrid.init();
      // iljingrid.enableAutoWidth(true);
      // iljingrid.setInitWidths("40,80,40,120,80");
      // iljinGrid.setColumnHidden(1, true);
      iljinGrid.enableAlterCss('even', 'uneven');
      iljinGrid.parse(this.grid, 'js');
      this.$refs.grid.attachEvent('onRowDblClicked', (rId) => {
        this.doReturnObject(rId);
      });
      $('#empGridbox').height('300')
      iljinGrid.setSizes()
    },
    goSearch(slow) {
        console.log('emp 검색');
      this.$store.commit('loading');
      this.grid.data = [];
      this.$http.get(`/api/emp/${this.search}`)
        .then((result) => {
          for (const item of result.data) {
            // item.roles = item.roles[0];
            this.grid.data.push(item);
          }
          this.$refs.grid.parse(this.grid, 'js');
          $(this.$refs.grid.entBox).height(300)
          this.$refs.grid.setSizes()
          // this.adjustGridColumns(this.$refs.grid);
          this.$store.commit('finish');

          if(!slow && this.grid.data.length === 1) {
            this.doReturnObject(1);
          }
        });
    },
    doReturnObject(rId) {
      this.returnObject.name = 'emp';
      this.returnObject.empNo = this.$refs.grid.cells(rId, 1).getValue();
      this.returnObject.empNm = this.$refs.grid.cells(rId, 2).getValue();
      this.returnObject.titleNm = this.$refs.grid.cells(rId, 3).getValue();
      this.returnObject.deptNm = this.$refs.grid.cells(rId, 4).getValue();
      this.returnObject.dutNm = this.$refs.grid.cells(rId, 5).getValue();
      this.returnObject.compCd = this.$refs.grid.cells(rId, 6).getValue();
      this.returnObject.compNm = this.$refs.grid.cells(rId, 7).getValue();
      this.$parent.$emit('receive', this.returnObject);
      this.$emit('close', this.returnObject)
      this.closeModal();
    },
    closeModal() {
      this.$parent.close();
    }
  },
  mounted() {
    if(this.param !== undefined) this.search = this.param;
    this.drawGrid();
    if(this.search) this.goSearch();
  },
  components: {
    Layout
  }
};
</script>