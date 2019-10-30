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
            <span class="label-tit">- 그룹코드/명</span>
          </div>
          <div class="desc">
            <input class="input Rt-M tal" type="text" id="group_cd" v-model="form.codeNm" />
          </div>
        </div>
      </div>
      <div class="item desc-center">
        <div class="desc-item">
          <div class="tit">
            <span class="label-tit">- 사용여부</span>
          </div>
          <div class="desc">
            <b-select class="select is-fullwidth" id="use_yn" v-model="form.useType">
              <option value="Y">예</option>
              <option value="N">아니오</option>
            </b-select>
          </div>
        </div>
      </div>
    </div>
    <!-- 테이블 -->
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">그룹코드</h3>
        </div>
        <div class="btn-wrap btn-type2 clearfix">
          <button class="btn-size btn-w-gray" @click="addRow()">
            <span class="btn-icon">
              <i class="fas fa-plus"></i>
            </span>행추가
          </button>
          <button class="btn-size btn-w-gray" @click="deleteRow">
            <span class="btn-icon">
              <i class="fas fa-trash-alt"></i>
            </span>행삭제
          </button>
        </div>
      </div>
      <dhx-grid ref="grid1" v-model="data" :config="config" />
    </div>
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">상세코드</h3>
        </div>
        <div class="btn-wrap btn-type2 clearfix">
          <button class="btn-size btn-w-gray" @click="addRowd">
            <span class="btn-icon">
              <i class="fas fa-plus"></i>
            </span>행추가
          </button>
          <button class="btn-size btn-w-gray" @click="deleteRowd">
            <span class="btn-icon">
              <i class="fas fa-trash-alt"></i>
            </span>행삭제
          </button>
        </div>
      </div>
      <dhx-grid ref="grid2" v-model="datad" :config="config_child" />
    </div>
  </div>
</template>
<script>
import _ from "lodash";
import DhxGrid from "@/components/DhxGrid.vue";
import GridCheckbox from "@/components/grid/GridCheckbox.vue";

/**
 * Url JOIN
 */
function _url(...args) {
  args = args.map(x =>
    String(x || "")
      .trim()
      .replace(/^\/*|\/*$/g, "")
  );
  return args.filter(x => x).join("/");
}

export default {
  name: "codeMng",
  components: {
    DhxGrid
  },
  data() {
    return {
      title: "공통코드 관리",
      deleteid: "",
      deleteList: [],
      form: {
        codeNm: "",
        useType: ""
      },
      data: [],
      datad: [],
      config: {
        columns: [
          {
            id: "itemSeq",
            align: "center",
            type: "cntr",
            value: "No",
            width: 35
          },
          {
            id: "groupCd",
            type: "ed",
            value: "그룹코드",
            width: 100
          },
          {
            id: "groupNm",
            align: "left",
            type: "ed",
            value: "그룹코드명",
            width: 120
          },
          {
            id: "useYn",
            value: "사용여부",
            width: 50,
            component: GridCheckbox
          },
          {
            id: "groupDesc",
            type: "ed",
            align: "left",
            value: "설명",
            width: 300
          },
          {
            id: "compCd",
            hide: true
          }
        ],
        events: {
          onRowSelect(rid){
            console.log(this.$parent.data[rid - 1])
            this.$http
              .post("/api/code/detail", {
                groupCd: this.$parent.data[rid-1].groupCd
              })
              .then(response => {
                console.log(response.data)
                this.$parent.datad = response.data
              });
          }
        }
      },
      config_child: {
        columns: [
          {
            id: "itemSeq",
            align: "center",
            type: "cntr",
            value: "No",
            width: 35
          },
          {
            id: "detailCd",
            type: "ed",
            value: "상세코드",
            width: 100
          },
          {
            id: "detailNm",
            align: "left",
            type: "ed",
            value: "상세코드명",
            width: 120
          },
          {
            id: "useYn",
            value: "사용여부",
            width: 50,
            component: GridCheckbox
          },
          {
            id: "orderSeq",
            type: "ed",
            align: "left",
            value: "정렬순서",
            width: 50
          },
          {
            id: "remark1",
            type: "ed",
            align: "left",
            value: "비고1",
            width: 50
          },
          {
            id: "remark2",
            type: "ed",
            align: "left",
            value: "비고2",
            width: 50
          },
          {
            id: "remark3",
            type: "ed",
            align: "left",
            value: "비고3",
            width: 50
          },
          {
            id: "remark4",
            type: "ed",
            align: "left",
            value: "비고4",
            width: 50
          },
          {
            id: "remark5",
            type: "ed",
            align: "left",
            value: "비고5",
            width: 50
          },
          {
            id: "detailDesc",
            type: "ed",
            align: "left",
            value: "설명",
            width: 50
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
    goOpen() {
      // code list 조회
      this.$http
        .post(_url("/api/code/list"), {
          groupCd: this.form.codeNm,
          useYn: this.form.useType
        })
        .then(response => {
          this.data = response.data;
        });
    },
    save() {
      //그룹코드 확인
      for(var i = 0;i<this.data.length;i++){
        for(var j = i+1; j<this.data.length;j++){
          if(this.data[i].groupCd === this.data[j].groupCd){
            this.$swal({type: 'warning', text: '해당 그룹코드가 이미 존재합니다.'});
            return false;
          }
        }
      }

      //상세코드 확인
      for(var i = 0;i<this.datad.length;i++){
        for(var j = i+1; j<this.datad.length;j++){
          if(this.datad[i].detailCd === this.datad[j].detailCd){
            this.$swal({type: 'warning', text: '해당 상세코드가 이미 존재합니다.'});
            return false;
          }
        }
      }

      //저장 시작
      
       // this.$http
        //.delete('/api/code/delete/' + this.deleteid)
        //.then(response => {
          this.$http
          .put('/api/code/save',{codeHeader : this.data, codeDetail : this.datad})
          .then(response => {
          this.$swal({ type: 'success', text: '저장되었습니다.' });
          this.goOpen()
        })
        .catch(({ message }) => {
          if (message === "Request failed with status code 500") {
            this.$swal({ type: "error", text: "상세코드를 입력해주세요." });
          }
        });  
       // })
      
    },
    deleteRow() {
        if(this.datad.length > 0){
         this.$swal({type: 'error' , text:'해당 그룹코드의 상세코드가 존재합니다. 상세코드 삭제 후 그룹코드 삭제가 가능합니다.'})
          return
        }
       const rId = this.$refs.grid1.instance.getSelectedRowId()
      if (rId === null) {
        this.$swal({
          type: 'error',
          text: '삭제할 행을 선택하여주세요.'
        })
      } else {
        const rowIndex = this.$refs.grid1.instance.getRowIndex(rId)
        const isNew = this.data[rowIndex].new
        const groupCd = this.data[rowIndex].groupCd

        this.data.splice(rowIndex, 1)

        if (!isNew) {
          this.$http.delete('/api/code/delete/'+groupCd
          ).then(response => {
            // Do nothing!
          })
        }
      }
      
    },
    addRow() {
      this.data.push({
        groupCd: "",
        groupNm: "",
        useYn: "Y",
        groupDesc: "",
        compCd: this.$store.state.loginInfo.compCd,
      });
    },
    deleteRowd() {
      try{
        if(this.$refs.grid2.instance.getSelectedRowId() == null)
          throw '선택된 행이 없습니다.'
        let index = this.$refs.grid2.instance.getSelectedRowId() - 1
        this.datad.splice(index, 1)
      }catch (e) {
        this.$swal({
          type: 'warning',
          text: e
        })
      }
    },
    addRowd() {
      try{
        if(this.$refs.grid1.instance.getSelectedRowId() == null)
         throw '그룹코드가 선택되지 않았습니다.'
        this.datad.push({
        detailCd: "",
        detailNm: "",
        useYn: "Y",
        orderSeq:"",
        remark1: "",
        remark2: "",
        remark3: "",
        remark4: "",
        remark5: "",
        detailDesc: "",
        groupCd: this.data[this.$refs.grid1.instance.getSelectedRowId()-1].groupCd,
        compCd: this.data[this.$refs.grid1.instance.getSelectedRowId()-1].compCd,
        });
      }catch (e) {
        this.$swal({
          type: 'warning',
          text: e
        })
      }
    }
  },
  mounted() {
    this.goOpen();
  }
};
</script>


<style scoped>
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