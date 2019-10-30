<template>
    <div class="table-b">
        <div class="table-header">
            <div class="table-name">
                <h3 class="ico_table_name">{{title}}</h3>
            </div>
        </div>
        <div class="grid-wrap">
            <dhx-grid class="slip-grid" v-model="slipDetails" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
        </div>
    </div>
</template>
<script>
    /* eslint-disable */
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import DhxGrid from '@/components/DhxGrid.vue'
    import _ from 'lodash'

    export default {
        name: 'SlipGridRO',
        props: ['slipDetails'],
        mixins: [ mixin, mixinSlip ],
        components: {DhxGrid},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'itemSeq', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'dcNm', type: 'ro', align: 'center', sort: 'na', value: '유형', width: 40},
                        {id: 'taxCd', type: 'ro', align: 'center', sort: 'na', value: '세금코드', width: 60},
                        {id: 'ioNo', type: 'ro', align: 'center', sort: 'na', value: 'IO', width: 40},
                        {id: 'cctrCd', type: 'ro', align: 'center', sort: 'na', value: '귀속부서', width: 100},
                        {id: 'cctrNm', type: 'ro', align: 'left', sort: 'na', value: '귀속부서명', width: 120},
                        {id: 'acctCd', type: 'ro', align: 'center', sort: 'na', value: '계정코드', width: 80},
                        {id: 'acctNm', type: 'ro', align: 'left', sort: 'na', value: '계정명', width: 140},
                        {id: 'debitAmt', type: 'ron', align: 'right', sort: 'na', value: '차변금액', width: 90},
                        {id: 'creditAmt', type: 'ron', align: 'right', sort: 'na', value: '대변금액', width: 90},
                        {id: 'lnSgtxt', type: 'ro', align: 'left', sort: 'na', value: '적요'},
                        {id: 'dcCd', type: 'ro', align: 'center', sort: 'na', value: '', width: 0},
                        {id: 'lnTypeCd', type: 'ro', align: 'center', sort: 'na', value: '', width: 0},
                    ],
                    height: 200,
                    afterRefreshData(grid, data) {
                        this.$nextTick(() => {
                            _.forEach(data, (item, index) => {
                                var rId = index + 1
                                this.$parent.setCellClassName(grid, rId, [5, 7, 10], 'tal');
                                this.$parent.setCellClassName(grid, rId, [8, 9], 'tar');
                            })
                        })
                    }
                },
                title: '세부항목',
                infoDetails :[]
            };
        },
        methods: {
            constructGridSuccessful(grid) {
                var header_style = 'color:#222;text-align:center;'
                var stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'

                grid.attachHeader(
                    ["합계","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#stat_total","#stat_total",""],
                    [header_style, '', '', '', '', '', '', '', stat_total_text, stat_total_text,'']
                )
                grid.setNumberFormat("0,000",8,'.',',');
                grid.setNumberFormat("0,000",9,'.',',');
                grid.setColumnHidden(11,true);
                grid.setColumnHidden(12,true);
            },
        },
        watch: {
            slipDetails() {
                console.log("라인정보 SET!!")
                this.slipDetails.forEach(function(item, index, array) {
                    if(item.dcCd === 'C') {
                        item.creditAmt = item.acctAmt;
                    } else if(item.dcCd === 'D') {
                        item.debitAmt = item.acctAmt;
                    }
                })

                this.$forceUpdate();
            }
        },
    };
</script>

<style lang="scss" scoped>
    .slip-grid {
        :global(.xhdr table tbody tr:last-child) {
            background-color: #f9f9f3;
        }

        :global(.xhdr table tbody tr:last-child td) {
            background-color: transparent !important;
        }

        :global(.xhdr table tbody tr:last-child td div) {
            background-color: transparent !important;
            color: inherit !important;
            text-align: inherit !important;
        }
    }
</style>
