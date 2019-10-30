<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-gray fl_left" @click="submit"><span class="btn-icon"><i class="fas fa-check"></i></span> 저장</button>
            </div>
        </div>

        <!-- 테이블 -->
        <div class="table-area">
            <div class="table-a fixed-th">
                <table id="basic" class="table" >
                    <tbody>
                    <tr>
                        <th width="10px">선택</th>
                        <th width="10px">메인</th>
                        <th>메뉴</th>
                        <th>아이콘</th>
                        <th>아이콘 이미지</th>
                    </tr>

                    <tr v-for="(mySet,i) in mysets" :key="i">
                        <td v-if="mySet.regYn=='1'" >
                            <input type="checkbox" class="chkbox" :id="mySet.menuNo" v-if="mySet.regYn=='1'" checked="true"  @change="apply"/><label :for="mySet.menuNo" style="padding:12px;"></label>
                            <!-- <input type="checkbox" id="payCust" /><label for="payCust">실지급처</label>-->
                        </td>
                        <td v-else class="chkbox">
                            <input type="checkbox" class="chkbox" :id="mySet.menuNo" @change="apply"/><label :for="mySet.menuNo" style="padding:12px;"></label>
                        </td>
                        <td v-if="mySet.regYn ==='1'" class="register">
                            등록
                        </td>
                        <td v-else class="register">

                        </td>
                        <td>
                            {{mySet.menuName}}
                        </td>
                        <!--아이콘 셀렉트박스-->
                        <td>
                            <select v-if="mySet.menuIconCd===null" :id="i" class="select is-fullwidth" @change="handleChange($event)">
                                <option value=''>==선택==</option>
                                <option
                                        v-for="item in menuIconCds"
                                        :key="item.key"
                                        :value="item.key"
                                        v-text="item.value">
                                </option>
                            </select>

                            <select v-else :id="i" class="select is-fullwidth" @change="handleChange($event)">
                                <option value=''>==선택==</option>
                                <option
                                        v-for="item in menuIconCds"
                                        :key="item.key"
                                        :value="item.key"
                                        v-text="item.value"
                                        :selected="mySet.menuIconCd==item.key">
                                </option>
                            </select>
                        </td>
                        <!--아이콘 셀렉트박스-->
                        <!--아이콘 보여주기-->
                        <td>
                            <span class="IconId">
                                <img v-if="mySet.menuIconCd==='10'" src="img/ico_main01.png">
                                <img v-else-if="mySet.menuIconCd==='20'" src="img/ico_main02.png">
                                <img v-else-if="mySet.menuIconCd==='30'" src="img/ico_main03.png">
                                <img v-else-if="mySet.menuIconCd==='40'" src="img/ico_main04.png">
                                <img v-else-if="mySet.menuIconCd==='50'" src="img/ico_main05.png">
                                <img v-else-if="mySet.menuIconCd==='60'" src="img/ico_main06.png">
                                <img v-else-if="mySet.menuIconCd==='70'" src="img/ico_main06_01.png">
                                <img v-else-if="mySet.menuIconCd==='80'" src="img/ico_main06_02.png">
                                <img v-else-if="mySet.menuIconCd==='90'" src="img/ico_main06_03.png">
                                <img v-else-if="mySet.menuIconCd==='100'" src="img/ico_main06_04.png">
                                <img v-else-if="mySet.menuIconCd==='110'" src="img/ico_main06_05.png">
                                <img v-else-if="mySet.menuIconCd==='120'" src="img/ico_main06_06.png">
                            </span>
                        </td>
                        <td style="display:none;" class="HdIconId">
                            {{mySet.menuIconCd}}
                        </td>
                        <td style="display:none;">
                            {{mySet.menuNo}}
                        </td>
                    </tr>

                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>

    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import DhxGrid from '@/components/DhxGrid.vue'

    export default {
        name: 'QuickSetting',
        mixins: [mixin, mixinSlip],
        components: {DhxGrid,},
        //props : {'menuIconCd'},
        data() {
            return {
                title: '메인설정',
                mysets:[],
                menuIconCds:[],
                menuNo:[],
                authority: '',
                compCd:'',
                loginId:'',
                checkId:[],
                checkList:[],
                chkSaveList:[],
                IconCdv:[],
                Icon:[],
                saveCheck:[],
                saveCheckID:[],
                resultId:[],
                resultCd:[],
                id:'chk',
            };
        },

        methods: {
            /*설정화면 전체 데이터 가져오기*/
            getMySet() {
                this.$http.get(`/api/dashboard/settings/${this.$store.state.loginInfo.loginId}`)
                    .then(response => {
                        this.mysets = response.data;
                        for(let j=0; j<this.mysets.length; j++){
                            this.menuNo[j] = this.mysets[j].menuNo;
                            if(this.mysets[j].regYn=='1'){
                                this.chkSaveList.push(this.mysets[j]);
                            }
                        }
                    });
            },
            /*아이콘 셀렉트박스 코드값 가져오기*/
            getMenuIconCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "MENU_ICON_CD"}})
                    .then(response => {
                        this.menuIconCds = response.data;
                    });
            },

            /*아이콘 셀렉트박스 이벤트*/
            handleChange(e){
                let x = document.getElementsByClassName("IconId"); //클래스 명이 IconId인 곳에 넣어주겠다.
                let z = document.getElementsByClassName("HdIconId");
                let i = e.target.id;
                let imgtag='';
                switch (e.target.value) {
                    case '10':
                        imgtag = '<img src="img/ico_main01.png"/>';
                        break;
                    case '20':
                        imgtag = '<img src="img/ico_main02.png"/>';
                        break;
                    case '30':
                        imgtag = '<img src="img/ico_main03.png"/>';
                        break;
                    case '40':
                        imgtag = '<img src="img/ico_main04.png"/>';
                        break;
                    case '50':
                        imgtag = '<img src="img/ico_main05.png"/>';
                        break;
                    case '60':
                        imgtag = '<img src="img/ico_main06.png"/>';
                        break;
                    case '70':
                        imgtag = '<img src="img/ico_main06_01.png"/>';
                        break;
                    case '80':
                        imgtag = '<img src="img/ico_main06_02.png"/>';
                        break;
                    case '90':
                        imgtag = '<img src="img/ico_main06_03.png"/>';
                        break;
                    case '100':
                        imgtag = '<img src="img/ico_main06_04.png"/>';
                        break;
                    case '110':
                        imgtag = '<img src="img/ico_main06_05.png"/>';
                        break;
                    case '120':
                        imgtag = '<img src="img/ico_main06_06.png"/>';
                        break;
                }
                x[i].innerHTML =imgtag;
                z[i].innerHTML = e.target.value;
            },
            apply() {

            },
            submit() {
                this.checkList=[];
                /* 체크된 데이터 가져오기*/
                this.saveCheck=[];
                this.saveCheckID = [];
                let test1 = document.getElementById("basic");
                let checkBoxes = test1.getElementsByTagName("input");
                for (let c = 0; c < checkBoxes.length; c++) {
                    if (checkBoxes[c].checked) {
                        let row = checkBoxes[c].parentNode.parentNode;
                        this.saveCheck[c] =row.cells[5].innerHTML.trim() ;
                        this.saveCheckID[c]=row.cells[6].innerHTML.trim();
                    }
                }
                let saveId =[];
                let saveCd =[];

                for(let k=0; k < this.saveCheckID.length; k++){
                    if(typeof this.saveCheckID[k] != "undefined" ){
                        saveId.push(this.saveCheckID[k]);
                    }
                    if(typeof this.saveCheck[k] != "undefined" ){
                        saveCd.push(this.saveCheck[k]);
                    }
                }
                this.resultId = saveId;
                this.resultCd = saveCd;

                /* 저장*/
                if(this.resultId.length>6){
                    this.$swal({ type: 'warning', text: '메인아이콘은 6개를 초과할 수 없습니다.' });
                }
                else{
                    for(let k = 0; k<this.resultCd.length; k++) {
                        if (this.resultCd[k] === "") {
                            this.$swal({type: 'warning', text: '아이콘을 선택해 주세요.'});
                            return;
                        }
                    }
                    for (let j = 0; j < this.resultId.length; j++) {
                        let saveQuick = {
                            "compCd": this.compCd,
                            "loginId": this.loginId,
                            "menuNo": this.resultId[j],
                            "menuIconCd": this.resultCd[j]
                        };
                        this.checkList.push(saveQuick);
                    }
                    this.$http.put(`/api/dashboard/settings`, this.checkList);
                    this.$router.go();
                }
            },

        },

        mounted() {
            this.authority = this.$store.state.loginInfo.authorities[0].roleCd;
            this.loginId = this.$store.state.loginInfo.loginId;
            this.compCd = this.$store.state.loginInfo.compCd;
            this.getMenuIconCdCombo();
            this.getMySet();


        }
    };
</script>

<style scoped>

    .table th {
        text-align: center;
    }

    .table td {
        text-align: center;
        height : 100px;
    }

    .table .left {
        text-align: left;
    }


</style>

