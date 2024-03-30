<template>
  <div
    class="echart"
    ref="mychart"
    id="mychart"
    :style="{ float: 'left', width: '100%', height: '400px' }"
  ></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  data() {
    return {
      name: "张雪",
      xData: ["2020-02", "2020-03", "2020-04", "2020-05"], //横坐标数据
      yData: [30, 132, 80, 134], //纵坐标数据，与横坐标对应
    };
  },
  mounted() {
    this.initEcharts();
  },
  methods: {
    initEcharts() {
  
      const option = {
        parallelAxis: [
          { dim: 0, name: "Price" },
          { dim: 1, name: "Net Weight" },
          { dim: 2, name: "Amount" },
          {
            dim: 3,
            name: "Score",
            type: "category",
            data: ["Excellent", "Good", "OK", "Bad"],
          },
        ],
        series: {
          type: "parallel",
          lineStyle: {
            width: 4,
          },
          data: [
            [12.99, 100, 82, "Good"],
            [9.99, 80, 77, "OK"],
            [20, 120, 60, "Excellent"],
          ],
        },
      };
      const myChart = echarts.init(this.$refs.mychart); // 图标初始化
      myChart.setOption(option); // 渲染页面
      //随着屏幕大小调节图表
      window.addEventListener("resize", () => {
        myChart.resize();
      });
    },
  },
};
</script>
