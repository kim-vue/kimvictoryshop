/*jshint es5: false */

import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/chart/Chartindex.vue'
import Chart from './views/chart/Chart.vue'



Vue.use(Router);

export default new Router({
    mode: 'history',
    // base: process.env.BASE_URL, 
    routes: [


        {
            path: '/todoRestful',
            name: 'todoRestful',
            component: () => import('./components/todoApp-restful.vue'),

        },
        {
            path: '/restapp',
            name: 'restapp',
            component: () => import('./components/todoApp.vue'),

        },

        {
            path: '/cardSlipReg',
            name: 'cardSlipReg',
            props: true,
            component: () =>
                import('./views/CardSlipReg.vue'),
        },
        {
            path: '/cardSlipQry',
            name: 'cardSlipQry',
            props: true,
            component: () =>
                import('./views/CardSlipQry.vue'),
        },
        {
            path: '/cardSlipUseLst',
            name: 'cardSlipUseLst',
            props: true,
            component: () =>
                import('./views/CardSlipUseLst.vue'),
        },
        {
            path: '/ebillSlipReg',
            name: 'ebillSlipReg',
            props: true,
            component: () =>
                import('./views/EbillSlipReg.vue'),
        },
        {
            path: '/ebillSlipRcvLst',
            name: 'ebillSlipRcvLst',
            component: () =>
                import('./views/EbillSlipRcvLst.vue'),
        },
        {
            path: '/slipLst',
            name: 'slipLst',
            component: () =>
                import('./views/SlipLst.vue'),
        },
        {
            path: '/billSlipQry/:eaSlipNo',
            name: 'billSlipQry',
            props: true,
            component: () =>
                import('./views/BillSlipQry.vue'),
        },
        {
            path: '/billSlipMng/:eaSlipNo',
            name: 'billSlipMng',
            props: true,
            component: () =>
                import('./views/BillSlipMng.vue'),
        },
        {
            path: '/billSlipReg/:eaSlipNo',
            name: 'billSlipRegEdit',
            props: true,
            component: () =>
                import('./views/BillSlipReg.vue'),
        },
        {
            path: '/billSlipReg',
            name: 'billSlipReg',
            props: true,
            component: () =>
                import('./views/BillSlipReg.vue'),
        },
        {
            path: '/quickSetting',
            name: 'quickSetting',
            component: () =>
                import('./views/QuickSetting.vue'),
        },
        {
            path: '/',
            name: 'main',
            component: () =>
                import('./views/MyMain.vue'),
        },
        {
            path: '/test',
            name: 'testMain',
            component: () =>
                import('./views/TestMain.vue'),
        },
        {
            path: '/apprPendLst',
            name: 'apprPendLst',
            component: () =>
                import('./views/ApprPendLst.vue'),
        },
        {
            path: '/apprDtlQry/:docMngNo',
            name: 'apprDtlQry',
            props: true,
            component: () =>
                import('./views/ApprDtlQry.vue'),
        },
        {
            path: '/mobile/apprDtlQry/:docMngNo',
            name: 'apprDtlQry',
            props: true,
            component: () =>
                import('./views/ApprDtlQry.vue'),
        },
        {
            path: '/apprCompLst',
            name: 'apprCompLst',
            component: () =>
                import('./views/ApprCompLst.vue'),
        },
        {
            path: '/apprReqLst',
            name: 'apprReqLst',
            component: () =>
                import('./views/ApprReqLst.vue'),
        },
        {
            path: '/apprMndSet',
            name: 'apprMndSet',
            component: () =>
                import('./views/ApprMndSet.vue'),
        },
        {
            path: '/apprRuleSet',
            name: 'apprRuleSet',
            component: () =>
                import('./views/ApprRuleSet.vue'),
        },
        {
            path: '/cardInfoMng',
            name: 'cardInfoMng',
            component: () =>
                import('./views/CardInfoMng.vue'),
        },
        {
            path: '/cardMndMng',
            name: 'cardMndMng',
            component: () =>
                import('./views/CardMndMng.vue'),
        },
        {
            path: '/cardUseLst',
            name: 'cardUseLst',
            component: () =>
                import('./views/CardUseLst.vue'),
        },
        {
            path: '/cardInvLst',
            name: 'cardInvLst',
            component: () =>
                import('./views/CardInvLst.vue'),
        },
        {
            path: '/cardCoprMng',
            name: 'cardCoprMng',
            component: () =>
                import('./views/CardCoprMng.vue'),
        },
        {
            path: '/slipMng',
            name: 'slipMng',
            component: () => import('./views/SlipMng.vue')
        },
        {
            path: '/slipGrAppr',
            name: 'slipGrAppr',
            component: () => import('./views/SlipGrAppr.vue')
        },
        //모니터링

        {

            path: '/ChartMonitor',
            name: 'ChartMonitor',

            //component: () => import('./views/slipMngItemSet.vue')
            component: () => import('./views/ChartMonitor.vue')

        },
        {
            path: '/evidSlip',
            name: 'evidSlipNew',
            props: true,
            component: () => import('./views/EvidSlip.vue')
        },
        {
            path: '/evidSlip/:eaSlipNo',
            name: 'evidSlipEdit',
            props: true,
            component: () => import('./views/EvidSlip.vue')
        },
        {
            path: '/whtSlip',
            name: 'whtSlipNew',
            props: true,
            component: () => import('./views/WhtSlip.vue')
        },
        {
            path: '/whtSlip/:eaSlipNo',
            name: 'whtSlipEdit',
            props: true,
            component: () => import('./views/WhtSlip.vue')
        },
        {
            path: '/bdgtReqReg',
            name: 'bdgtReqReg',
            component: () => import('./views/BdgtReqReg.vue')
        },
        {
            path: '/bdgtReq',
            name: 'bdgtReqNew',
            component: () => import('./views/BdgtReq.vue')
        },
        {
            path: '/bdgtReq/:budReqNo',
            name: 'bdgtReqEdit',
            props: true,
            component: () => import('./views/BdgtReq.vue')
        },
        {
            path: '/bdgtReqMng/:budReqNo',
            name: 'bdgtReqMngEdit',
            props: (route) => {
                return {
                    budReqNo: route.params.budReqNo,
                    manage: true
                }
            },
            component: () => import('./views/BdgtReq.vue')
        },
        {
            path: '/bdgtReqLst',
            name: 'bdgtReqLst',
            component: () => import('./views/BdgtReqLst.vue')
        },
        {
            path: '/bdgtReqMng',
            name: 'bdgtReqMng',
            component: () => import('./views/BdgtReqMng.vue')
        },
        {
            path: '/deptBdgLst',
            name: 'deptBdgLst',
            component: () => import('./views/DeptBdgLst.vue')
        },
        {
            path: '/authMng',
            name: 'authMng',
            component: () => import('./views/AuthMng.vue')
        },
        {
            path: '/pgmMng',
            name: 'pgmMng',
            component: () => import('./views/PgmMng.vue')
        },
        {
            path: '/codeMng',
            name: 'codeMng',
            component: () =>
                import('./views/CodeMng.vue'),
        },
        {
            path: '/acctMng',
            name: 'acctMng',
            component: () =>
                import('./views/AcctMng.vue'),
        },
        {
            path: '/taxMng',
            name: 'taxMng',
            component: () =>
                import('./views/TaxMng.vue'),
        },
        {
            path: '/closeMng',
            name: 'closeMng',
            component: () =>
                import('./views/CloseMng.vue'),
        },
        {
            path: '/oilPcePop',
            name: 'oilPcePop',
            component: () =>
                import('./views/oilPcePop.vue'),
        },
    ]
});