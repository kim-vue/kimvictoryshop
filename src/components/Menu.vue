<template>
  <div class="lnb">
    <ul class="menu-depth01">
      <li>
        <router-link class="navbar-item" to="/restapp">rest api</router-link>
      </li>

      <li>
        <a href="#none" title="고객-모니터링시스템">
          <i class="lnb-icon fas fa-chalkboard-teacher"></i> 고객-모니터링시스템
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/cardSlipUseLst">고객메인</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/ChartMonitor">장비모니터링</router-link>
          </li>
          <!-- <li><a href="#none" title="">전자세금계산서 - XML</a></li> -->
          <li>
            <router-link
              class="navbar-item"
              :to="{ name: 'billSlipRegEdit', params: { eaSlipNo: '0' } }"
            >작업통계</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/evidSlip">작업통계-기간별</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/whtSlip">가공이력</router-link>
          </li>
        </ul>
      </li>
      <li>
        <a href="#none" title="HK-모니터링시스템">
          <i class="lnb-icon far fa-folder-open"></i> HK-모니터링시스템
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/slipLst">장비현황</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/slipGrAppr">작업통계기간별</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/slipMng">가공이력</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/slipMngItemSet">기준정보관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/slipMngItemSet">시스템관리</router-link>
          </li>
        </ul>
      </li>
      <li>
        <a href="#none" title="전자결재">
          <i class="lnb-icon far fa-check-circle"></i> 전자결재
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/apprPendLst">결재할 문서</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/apprCompLst">결재한 문서</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/apprReqLst">상신한 문서</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/apprMndSet">결재위임</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/apprRuleSet">전결규정관리</router-link>
          </li>
        </ul>
      </li>
      <li>
        <a href="#none" title="예산관리">
          <i class="lnb-icon fas fa-coins"></i> 예산관리
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/bdgtReqReg">기초예산등록</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/bdgtReq">예산신청</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/bdgtReqLst">예산신청내역</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/bdgtReqMng">예산신청관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/deptBdgLst">예산실적내역</router-link>
          </li>
        </ul>
      </li>
      <li>
        <a href="#none" title="법인카드관리">
          <i class="lnb-icon far fa-credit-card"></i> 법인카드관리
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/cardInfoMng">법인카드정보관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/cardMndMng">법인카드위임</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/cardUseLst">법인카드사용현황</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/cardInvLst">법인카드청구현황</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/cardCoprMng">법인카드대사관리</router-link>
          </li>
        </ul>
      </li>
      <li>
        <a href="#none" title="기준정보관리">
          <i class="lnb-icon fas fa-cog"></i> 기준정보관리
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/closeMng">회계기간관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/acctMng">계정과목관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/taxMng">세금코드관리</router-link>
          </li>
          <li>
            <a href="#none" title>거래처관리</a>
          </li>
          <li>
            <router-link class="navbar-item" to="/oilPcePop">유류단가관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/codeMng">코드관리</router-link>
          </li>
        </ul>
      </li>
      <li>
        <a href="#none" title="시스템관리">
          <i class="lnb-icon fas fa-cog"></i> 시스템관리
        </a>
        <ul class="menu-depth02">
          <li>
            <router-link class="navbar-item" to="/pgmMng">메뉴관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/authMng">권한관리</router-link>
          </li>
          <li>
            <router-link class="navbar-item" to="/quickSetting">환경설정</router-link>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "Menu",
  data() {
    return {};
  },
  methods: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
