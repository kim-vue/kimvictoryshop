<template>
  <v-ons-page>
    <v-ons-toolbar>
      <div class="left">
        <v-ons-back-button>이전</v-ons-back-button>
      </div>
      <div class="center">작업통계</div>
    </v-ons-toolbar>
    <div class="small">
      <!-- <line-chart :chart-data="datacollection"></line-chart> -->
      <bar-chart :chart-data="datacollection"></bar-chart>
      <hr>
      <v-ons-button @click="fillData()">변경변경</v-ons-button>
      <v-ons-button @click="fillData()">Randomize</v-ons-button>
      <hr>
      <doughnut-chart :chart-data="datacollection" :options="options"></doughnut-chart>
    </div>
  </v-ons-page>
</template>


<script>
  // import LineChart from '@/components/LineChart.js'
  import BarChart from '@/components/BarChart.js'
  // import PieChart from '@/components/PieChart.js'
  import DoughnutChart from '@/components/DoughnutChart.js'

  export default {
    components: {
      BarChart, DoughnutChart
    },
    data () {
      return {
        datacollection: null,
        options: {
          animation: {
            animateScale	: false
          },
          elements: {
              center: {
              text: this.getRandomInt(),
              color: '#36A2EB', //Default black
              fontStyle: 'Helvetica', //Default Arial
              sidePadding: 15 //Default 20 (as a percentage)
            }
          }
        }
      }
    },
    mounted () {
      this.fillData()
    },
    methods: {
      fillData () {
        this.datacollection = {
          labels: ['one', 'two'],
          datasets: [
            {
              label: 'Data One',
              backgroundColor: ['#f87979', 'steelblue', 'yellow', 'red','green'],
              data: [this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt()],
              text: '1, 297\n(104.8%)'
            }, 
            // {
            //   label: 'Data Two',
            //   backgroundColor: 'blue',
            //   data: [this.getRandomInt()]
            // }
          ]
        }
      },
      getRandomInt () {
        return Math.floor(Math.random() * (50 - 5 + 1)) + 5
      }
    }
  }
</script>

<style scoped>
 .small {
    max-width: 30rem;
    /* margin:  150px auto; */
  }
</style>