
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
                  <span class="pop-c-name">- IO 코드/명</span>
              </div>
              <div class="control is-expanded">
                  <input class="input" type="text" v-model="search" @keydown.enter="goSearch">
              </div>
          </div>
      </div>

      <div class="grid-wrap">
          <div id="IoGridbox" class="grid-tbl-box"></div>
      </div>
    </div>
  </layout>
</template>

<script>
import Layout from '@/components/ModalSlot.vue'
import mixin from '@/mixin';

export default {
  name: 'Io',
  props: ['param'],
  mixins: [ mixin ],
  data() {
    return {
      title: 'IO 조회',
      search: '',
      grid: {
        head: [
          {id: 'no', type: 'cntr', align: 'center', sort: 'int', value: 'No.'},
          {id: 'ioCd', type: 'ro', align: 'center', sort: 'str', value: 'IO코드'},
          {id: 'ioNm', type: 'ro', align: 'center', sort: 'str', value: 'IO명칭'},
          {id: 'cctrCd', type: 'ro', align: 'center', sort: 'str', value: '비용부서코드'},
          {id: 'cctrNm', type: 'ro', align: 'center', sort: 'str', value: '비용부서'},

        ],
        data: [],
      },
      returnObject: {}
    }
  },
  methods: {
    drawGrid() {
      // eslint-disable-next-line
      const iljinGrid = new dhtmlXGridObject('IoGridbox');
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
      $('#IoGridbox').height('300')
      iljinGrid.setSizes()
    },
    goSearch(slow) {
      this.$store.commit('loading');
      this.grid.data = [];
      this.$http.get(`/api/io/${this.search}`)
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
      this.returnObject.name = 'io';
      this.returnObject.ioCd = this.$refs.grid.cells(rId, 1).getValue();
      this.returnObject.ioNm = this.$refs.grid.cells(rId, 2).getValue();
      this.returnObject.cctrCd = this.$refs.grid.cells(rId, 3).getValue();
      this.returnObject.cctrNm = this.$refs.grid.cells(rId, 4).getValue();

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

<style scoped>
div#gridbox {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>
