<template>

<div class="wrap type-main">
    <!-- header -->
        <div class="header">
            <div class="logo">
                <a href="#none"></a>
                <button>메뉴</button>
            </div>
            <div class="user-info">
                <span class="user-msg">[{{ this.$store.state.loginInfo.loginDeptNm }}] <span class="point-blue">{{ this.$store.state.loginInfo.userName }}</span> <span>({{ this.$store.state.loginInfo.loginId }})</span></span>
                <a href="/" class="ico ico-home" title=""></a>
                <a href="/quickSetting" class="ico ico-top02" title=""></a>
                <a href="#" class="ico ico-logout" title="" @click="logout"></a>
            </div>
        </div>
        <!-- //header -->
    <!-- menu -->
    <div class="menu-wrap">
        <ul class="menu">
            <li v-for="(menuhead,i) in menuheads" :key="i">
                <a>{{menuhead.menuNm}}</a>
                <ul>
                    <li v-for="(mainmenu,i) in mainmenus" :key="i">
                        <a v-if="menuhead.menuNo === mainmenu.upperMenuNo">
                            <a :href="mainmenu.programFileNm">{{mainmenu.menuNm}}</a>
                        </a>
                    </li>
                </ul>
            </li>

        </ul>
    </div>
    <!-- //menu -->

    <!-- contents -->
    <div class="contents2">
        <div class="inner">
            <div class="clearfix">
                <!-- left 영역 -->
                <div class="left">
                    <!-- 2.퀵메뉴 -->
                    <!--큌메뉴 설정 6개 이하일 경우-->
                    <ul v-if="myquicks === null" class="quick-menu" >
                        <li v-for="index in six"  class="">
                            <a href=""></a>
                        </li>
                        <li class="ico06-07 card"><router-link to="/quickSetting">시스템관리</router-link></li>
                    </ul>
                    <ul v-else-if="myquicks.length !== 6" class="quick-menu" >
                        <li v-for="(quick,i) in myquicks" :class="quickIcon[i]">
                            <!--각 메뉴에 링크가 다 있으면 router-link로 바꾸자-->
                            <a :href="quick.programFileNm">{{quick.menuNm}}</a>
                        </li>
                        <li v-for="index in six"  class="">
                            <a href=""></a>
                        </li>
                        <li class="ico06-07 card"><router-link to="/quickSetting">시스템관리</router-link></li>
                    </ul>
                    <!--큌메뉴 설정 6개일 경우-->
                    <ul v-else class="quick-menu" >
                        <li v-for="(quick,i) in myquicks" :class="quickIcon[i]">
                            <!--각 메뉴에 링크가 다 있으면 router-link로 바꾸자-->
                            <a :href="quick.programFileNm">{{quick.menuNm}}</a>
                        </li>
                    </ul>
                    <!-- //2. 퀵메뉴 -->
                    <!-- 5. 사용현황 -->
                    <div class="white-box card status" >
                        <div class="top-area">
                            <h1 class="box-title">사용현황</h1>
                            <router-link class="btn-more" to="/slipLst"></router-link>
                        </div>
                        <div class="data-box" >
                            <!-- 그래프 영역 -->
                            <div class="graph-box">
                                <div id="chartbox" style="width:375px;height:170px;"></div>
                            </div>
                            <!-- //그래프 영역 -->
                            <div>

                                <ul v-if="psConds !==''" class="status-list">
                                    <li v-for="(psCond,i) in psConds" :key="i">
                                        <span class="dot"></span>{{psCond.acctNm}}
                                    </li>
                                </ul>

                                <ul v-if = "psConds.length===0" class="status-list">
                                    <li>
                                        <span class="dot"></span>없음
                                    </li>
                                </ul>
                            </div>

                        </div>
                    </div>

                    <!-- //5.사용현황 -->


                </div>
                <!-- //left 영역 -->

                <!-- right 영역 -->
                <div class="right">
                    <!-- 3.메인법인카드내역-->
                    <div class="white-box card creditcard">
                        <div class="top-area">
                            <h1 class="box-title">법인카드내역</h1>
                            <router-link class="btn-more" to="/cardSlipUseLst?useDtlsStatCd=10"></router-link>
                        </div>
                        <div class="data-box">
                            <!--카드 이미지 영역-->
                            <div class="card-box">
                                <img src="img/img_card.png">
                            </div>
                            <!--카드 이미지 영역-->
                            <!--법인카드 미처리 리스트-->
                            <ul class="line-list using-list">
                                <li v-for="(unCard,i) in mymains.unCardList" :key="i">
                                    <a @click="goPage(unCard)">
                                        <span class="store">{{unCard.merchNm}}</span><span class="money">{{unCard.apprAmt | currency}}</span><span class="date">{{unCard.apprDate}}</span>
                                    </a>
                                </li>
                            </ul>
                            <!--법인카드 미처리 리스트-->
                        </div>
                    </div>
                    <!-- 3.메인법인카드내역-->

                    <!-- 4.경비처리내역 -->
                    <div class="white-box card expense">
                        <div class="top-area">
                            <h1 class="box-title">경비처리내역</h1>
                            <router-link class="btn-more" to="/slipLst"></router-link>
                        </div>
                        <div class="data-box">
                            <ul class="line-list">
                                <li v-for="(rcSlip,i) in mymains.rcSlipList" :key="i">
                                    <a :href="rcSlipData[i]">
                                        <span class="txt">{{rcSlip.slipTypeNm}}</span>
                                        <span class="money">{{rcSlip.totAmt | currency}}</span>
                                            <span class="status statue-wait" >
                                                {{rcSlip.slipStatNm}}
                                            </span>
                                        <span class="status01">{{rcSlip.hdSgtxt}}</span>
                                        <span class="date">{{rcSlip.chgDtm}}</span>
                                    </a>
                                </li>
                            </ul>
                        </div>

                    </div>
                    <!-- //4.경비처리내역 -->
                </div>
                <!-- //right 영역 -->
            </div>
            <!-- //clearfix -->
        <!-- 6.메인처리 예정건수-->
        <ul class="blue-box">
            <li class="blue blue01">
                <router-link to="/cardSlipUseLst?useDtlsStatCd=10">
                    <span class="txt-kor">법인카드 미처리</span><span class="txt-eng">Corporate card unprocessed</span><span class="count"><span> {{ this.uncounts.untrCard && this.uncounts.untrCard.length > 0 ? this.uncounts.untrCard[0].cnt : '' }}</span>건</span>
                </router-link>
            </li>
            <li class="blue blue02">
                <router-link to="/ebillSlipRcvLst">
                    <span class="txt-kor">세금계산서 미처리</span><span class="txt-eng">Unprocessed tax invoice</span><span class="count"><span >{{ this.uncounts.untrEtax && this.uncounts.untrEtax.length > 0 ? this.uncounts.untrEtax[0].cnt : '' }}</span>건</span>
                </router-link>
            </li>
            <li class="blue blue03">
                <router-link to="/slipLst?slipStatCd=10">
                    <span class="txt-kor">전표미상신</span><span class="txt-eng">Not approved for slip</span><span class="count"><span>{{ this.uncounts.unApprSlip && this.uncounts.unApprSlip.length > 0 ? this.uncounts.unApprSlip[0].cnt : '' }}</span>건</span>
                </router-link>
            </li>
            <li class="blue blue04">
                <router-link to="/bdgtReqLst?budStatCd=10">
                    <span class="txt-kor">예산미상신</span><span class="txt-eng">Budget not approved</span><span class="count"><span>{{ this.uncounts.unApprBdgt && this.uncounts.unApprBdgt.length > 0 ? this.uncounts.unApprBdgt[0].cnt : '' }}</span>건</span>
                </router-link>
            </li>
            <li class="blue blue05">
                <router-link to="/apprPendLst">
                    <span class="txt-kor">결재</span><span class="txt-eng">Approve proposal</span><span class="count"><span>{{ this.uncounts.todoAppr && this.uncounts.todoAppr.length > 0 ? this.uncounts.todoAppr[0].cnt : '' }}</span>건</span>
                </router-link>
            </li>
            <li class="blue blue06">
                <router-link to="/apprCompLst?docStatCd=REJ">
                    <span class="txt-kor">반려</span><span class="txt-eng">Return a document</span><span class="count"><span>{{ this.uncounts.rjctAppr && this.uncounts.rjctAppr.length > 0 ? this.uncounts.rjctAppr[0].cnt : '' }}</span>건</span>
                </router-link>
            </li>
        </ul>
        <!-- 6.메인처리 예정건수-->

        </div>
        <!-- //inner -->
    </div>
    <!-- //contents -->
    <!-- footer -->
    <div class="footer2">
        <span class="copyright">COPYRIGHT © ILJIN ALL RIGHTS RESERVED.</span>
    </div>
    <!-- //footer -->
</div>
<!-- //wrap -->

</template>

<script>
import DhxGrid from '@/components/DhxGrid.vue';
import router from '@/router';


export default {
  name: 'MyMain',
  components: {
    DhxGrid
  },
  data() {
    return {
        //메인화면 전체데이터
        mymains: [],
        //1.메인메뉴
        mainmenus:[],
        menuheads:[],
        menulink:[],
        //2.메인바로가기(퀵메뉴)
        mysets:[],
        myquicks:[],
        six:[],
        quickIcon:[],
        //3.메인법인카드내역
        unCardLists:[],
        uCard:[],
        //4.메인경비처리내역
        rcSlipLists:[],
        rcSlipData:[],
        //5. 사용현황
        psConds:[],
        piData:[],
        //6.메인처리예정건수
        uncounts: [],

     }
  },
  /* 숫자에 콤마(,)넣기*/
  filters:{
    currency:function (value) {
        var num = new Number(value);
        return num.toFixed(0).replace(/(\d)(?=(\d{3})+(?:\.\d+)?$)/g,"$1,")
    }
  },

    mounted() {
      this.getMyMain();
      this.getMainMenu();
      this.getPsCond();
      this.getMySet();
      this.getRcSlipList();
      this.getUnCardList();
  },
  methods: {
      //로그아웃
      logout() {
          this.$http
              .get('/logout')
              .then(() => {
                  this.$store.commit('logout');
                  this.$cookie.delete('loginInfo');
              })
              .catch((e) => {
                  console.error(e);
              });
      },
    //메인화면 데이터 불러오기
    getMyMain() {
          this.$http.get(`/api/dashboard/${this.$store.state.loginInfo.compCd}/${this.$store.state.loginInfo.loginId}`)
              .then(response => {
                  //모든 데이터
                  this.mymains = response.data;
                  //1. 메인메뉴
                  this.mainmenus = response.data.menuList;
                  //6.메인처리예정건수
                  this.uncounts = response.data.counts;
              });
      },
      //1. 메인메뉴
      getMainMenu() {
          this.$http.get(`/api/dashboard/${this.$store.state.loginInfo.compCd}/${this.$store.state.loginInfo.loginId}`)
              .then(response => {
                  this.mainmenus = response.data.menuList;
                  let menuupper=[];
                  for(let i=0; i<this.mainmenus.length; i++){
                      if(this.mainmenus[i].upperMenuNo==0){
                          menuupper.push(this.mainmenus[i]);
                      }
                  }
                  this.menuheads =menuupper;
              });
      },
      //2.메인바로가기(퀵메뉴)
      getMySet() {
          this.$http.get(`/api/dashboard/${this.$store.state.loginInfo.compCd}/${this.$store.state.loginInfo.loginId}`)
              .then(response => {
                  this.myquicks = response.data.userMenuList;
                  if(this.myquicks==null){
                      this.six = 5;
                  }
                  else{
                      for(let ic=0; ic<this.myquicks.length; ic++){
                          switch (this.myquicks[ic].menuIconCd) {
                              case '10':
                                  this.quickIcon.push( "ico01 card");
                                  break;
                              case '20':
                                  this.quickIcon.push( "ico02 card");
                                  break;
                              case '30':
                                  this.quickIcon.push( "ico03 card");
                                  break;
                              case '40':
                                  this.quickIcon.push( "ico04 card");
                                  break;
                              case '50':
                                  this.quickIcon.push( "ico05 card");
                                  break;
                              case '60':
                                  this.quickIcon.push( "ico06 card");
                                  break;
                              case '70':
                                  this.quickIcon.push( "ico06-01 card");
                                  break;
                              case '80':
                                  this.quickIcon.push( "ico06-02 card");
                                  break;
                              case '90':
                                  this.quickIcon.push( "ico06-03 card");
                                  break;
                              case '100':
                                  this.quickIcon.push( "ico06-04 card");
                                  break;
                              case '110':
                                  this.quickIcon.push( "ico06-05 card");
                                  break;
                              case '120':
                                  this.quickIcon.push( "ico06-06 card");
                                  break;
                          }
                      }
                      if(this.myquicks.length!=6){
                          this.six = 5-this.myquicks.length;
                      }
                  }
              });
      },
    //3. 메인법인카드내역
      getUnCardList() {
          this.$http.get(`/api/dashboard/${this.$store.state.loginInfo.compCd}/${this.$store.state.loginInfo.loginId}`)
              .then(response => {
                  this.unCardLists = response.data.unCardList;
              });
      },
      goPage(params) {
          console.log("페이지이동", params)
          let targetName = (params.eaSlipNo === null || params.slipStatCd === '10') ? 'cardSlipReg' : 'billSlipMng';;
          this.$router.push({ name: targetName, params: params });
      },
    //4. 메인경비처리내역
      getRcSlipList() {
          this.$http.get(`/api/dashboard/${this.$store.state.loginInfo.compCd}/${this.$store.state.loginInfo.loginId}`)
              .then(response => {
                  this.rcSlipLists = response.data.rcSlipList;
                  let rc = [];
                  for(let x=0; x<this.rcSlipLists.length;x++){
                      switch (this.rcSlipLists[x].slipTypeCd) {
                          case 'E1':
                              if(this.rcSlipLists[x].slipStatCd==='10') {
                                  rc = '/cardSlipReg/'+ this.rcSlipLists[x].eaSlipNo;
                                  }
                              else{
                                  rc = '/billSlipMng/'+ this.rcSlipLists[x].eaSlipNo;
                                  }
                              break
                          case 'E2':
                              if(this.rcSlipLists[x].slipStatCd==='10') {
                                  rc = '/ebillSlipReg/'+ this.rcSlipLists[x].eaSlipNo;
                                  }
                              else{
                                  rc = '/billSlipMng/'+ this.rcSlipLists[x].eaSlipNo;
                              }
                              break
                          case 'E3':
                              if(this.rcSlipLists[x].slipStatCd==='10') {
                                  rc = '/billSlipReg/'+ this.rcSlipLists[x].eaSlipNo;
                                  }
                              else{
                                  rc = '/billSlipMng/'+ this.rcSlipLists[x].eaSlipNo;
                              }
                              break
                          case 'E4':
                              rc = '/evidSlip/'+ this.rcSlipLists[x].eaSlipNo;

                              break
                          case 'E6':
                              rc = '/whtSlip/'+ this.rcSlipLists[x].eaSlipNo;
                              break
                          default :
                              break
                      }
                      this.rcSlipData.push(rc);
                  }
              });
      },
    //5.메인사용현황
    getPsCond() {
      this.$http.get(`/api/dashboard/${this.$store.state.loginInfo.compCd}/${this.$store.state.loginInfo.loginId}`)
          .then(response => {
              this.psConds = response.data.psCond;
              let pieData=[];

              if(this.psConds.length>0){
                 pieData = this.psConds;

                  for(let i=0; i<pieData.length; i++){
                     if(i===0){
                         pieData[i].color="#2a84c9";
                     }
                      else if(i===1){
                          pieData[i].color="#f05f52";
                      }
                      else if(i===2){
                          pieData[i].color="#f5920c";
                      }
                      else if(i===3){
                          pieData[i].color="#14c7fe";
                      }
                      else if(i===4){
                          pieData[i].color="#69d697";
                      }
                      else {
                          pieData[i].color="#f3c563";
                      }
                  }
              }

              if(pieData.length===0){
                  pieData={
                      "sumAcctAmt" : 10000,
                      "color" : "#2a84c9",
                      "acctNm" : "사용전"
                  }
              }

              let myPieChart = new dhtmlXChart({
                  view:"donut",
                  container:"chartbox",
                  value:"#sumAcctAmt#",
                  color:"#color#",
                  radius:65,
                  innerRadius:30,
                  tooltip:"<b>#acctNm#: #sumAcctAmt#</b>",
                  shadow:false,

              });
              myPieChart.parse(pieData,"json");
          });
      },
  },
};

</script>


<style scoped lang="scss">
@import "public/css/main";

.wrap.lnb.minimized~.contents2 {
    left: 50px;
}

/* contents */

.contents2 {
    max-width: 100%;
    min-width: 1033px;
    position: absolute;
    right: 0;
    bottom: 0;
    z-index: 2;
    transition: .3s;
    padding: 0px 25px 33px 25px;
    /*overflow-y: auto;*/
}


.contents2>.inner-box {
    padding-bottom: 80px;
    min-height: 80vh;
}

.contents2 .content-name {
    margin-top: 33px;
}

.contents2 .content-name:after {
    clear: both;
    content: '';
    display: block;
}

.contents2 .content-name h2 {
    font-size: 24px;
    color: #061c3a;
    font-family: 'NotoM';
    float: left;
    line-height: 1;
}

.contents2 {
    /*overflow-y:auto;*/
    padding: 0;
}

.contents2>.inner-box {
    max-width: 100%;
    min-width: 1033px;
    padding: 0px 25px 33px 25px;
}
.contents2 div.gridbox_material.gridbox .xhdr {
    background: #f3f5f9;
    border-bottom: none;
    max-height: 100%;
    margin-top: -1px;
}

.contents2 .grid-tbl-box.type03 div.gridbox_material.gridbox .xhdr {
    height: 112px!important;
}
.contents2 div.gridbox_material.gridbox table.hdr td div.hdrcell {
    font-size: 14px;
    line-height: 24px;
    padding: 5.5px 0px;
    text-align: center;
    font-family: NotoM;
    color: #222;
}
.right .white-box .data-box{
    height: 239px;
}
</style>
