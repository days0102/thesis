<!--
 * @Author       : Outsider
 * @Date         : 2024-04-06 10:10:25
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-04-08 23:17:06
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\views\MLView.vue
-->
<template>
  <div v-loading="loading" style="margin: 3px; border: 1px" ref="divRef">
    <svg ref="shap"></svg>
  </div>
</template>

<script>
import { defineComponent, onMounted, ref, watch } from "vue";
import { useWindowSize, useResizeObserver } from "@vueuse/core";
import { useRoute } from "vue-router";
import * as d3 from "d3";

export default defineComponent({
  setup() {
    const route = useRoute();
    // console.log(route.params.cluster_id);
    const cid = route.params.cluster_id;

    let dimension = useWindowSize();
    let height = document.body.clientHeight * 0.8;
    let dimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };

    const datas = ref(null);
    const shap = ref(null);
    const divRef = ref(null);
    const loading = ref(true);

    useResizeObserver(divRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      dimensions.width.value = width;
      dimensions.height.value = height;
      console.log("ml", width, height);
    });

    onMounted(() => {
      fetch(`/api/ml/${cid}`, {
        method: "GET",
      })
        .then((d) => {
          return d.json();
        })
        .then((d) => {
          // console.log(d);
          datas.value = d;
          loading.value = false;
        });
    });

    watch([datas, dimensions.width, dimensions.height], () => {
      // console.log(dimensions);
      // console.log("data", datas);
      if (datas.value == null) return;

      const structDatas = (data, columns) => {
        let structData = [];
        console.log(data, columns);
        for (let v in data) {
          for (let c in columns) {
            console.log(v, c);
            structData.push({
              index: v,
              value: data[v][c],
              column: columns[c],
            });
          }
        }
        return structData;
      };

      const data = structDatas(datas.value.data, datas.value.columns);
      console.log(data);

      const marginTop = 25;
      const marginRight = 20;
      const marginBottom = 35;
      const marginLeft = 300;

      // 获取所有列名（纵坐标）
      var columns = datas.value.columns;

      // 获得 data 中的所有值
      const allValues = datas.value.data.flat();

      // 计算最大值和最小值
      const maxValue = Math.max(...allValues);
      const minValue = Math.min(...allValues);

      // console.log("最大值:", maxValue);
      // console.log("最小值:", minValue);
      const colorScale = d3
        .scaleLinear()
        .domain([minValue, maxValue]) // 设置输入的数据范围
        .range(["blue", "red"]); // 设置颜色范围

      // 计算预留空间所对应的数值范围
      const paddingPercentage = 0.1; // 10% 的预留空间
      const padding = (maxValue - minValue) * paddingPercentage;
      // 定义横轴比例尺
      var xScale = d3
        .scaleLinear()
        .domain([minValue - padding, maxValue + padding])
        .range([marginLeft, dimensions.width.value - marginRight]);
      // 定义纵轴比例尺
      var yScale = d3
        .scalePoint()
        .domain(columns)
        .range([height - marginBottom, marginTop])
        .padding(0.5);

      // console.log(columns.length);
      d3.select(shap.value).selectAll("*").remove();

      const svg = d3
        .select(shap.value)
        .style("width", dimensions.width.value + "px")
        .style("height", height + "px");
      // 绘制横轴
      const xAxis = svg
        .append("g")
        .attr("class", "axis axis-x")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(xScale));
      // console.log("x", xScale(0));
      // 绘制纵轴
      const yAxis = svg
        .append("g")
        // .attr("transform", "translate(0,350)")
        .attr("class", "axis axis-y")
        .attr("transform", `translate(${xScale(0)},0)`)
        .call(d3.axisLeft(yScale).tickSize(0));
      yAxis
        .selectAll("text")
        .style("text-anchor", "start") // 设置文本锚点为起始位置
        .attr("transform", `translate(${-xScale(0) + 15})`);

      // 添加散点
      svg
        .selectAll("circle")
        .data(data) // 将一维数组绑定到选择集
        .enter()
        .append("circle")
        .attr("r", 5)
        .style("fill", (d) => colorScale(d.value))
        .attr("cx", (d, i) => xScale(d.value)) // 使用数据和索引来计算 x 坐标
        .attr("cy", (d, i) => yScale(d.column)) // 使用数据和索引来计算 y 坐标
        .on("click", (event, d) => {
          console.log("click", d);
        });

      const brush = d3
        .brush()
        // Calling a function on brush change
        .on("end", brushed)

        /* Initialise the brush area:start at 0, 0
         and finishes at given width, height*/
        .extent([
          [marginLeft, marginTop],
          [
            dimensions.width.value - marginRight,
            dimensions.height.value - marginBottom,
          ],
        ]);
      svg.append("g").attr("class", "brush").call(brush);

      function brushed(event) {
        // console.log("brushended event", event);
        var sel = event.selection;
        console.log(sel);
        svg.selectAll(".tooltip").remove();
        if (!sel) {
          // 如果没有选择区域，则恢复原始比例尺范围
          xScale.domain([minValue - padding, maxValue + padding]);
          yScale.domain(columns); // 更新为原始列的数量范围
        } else {
          // 如果有选择区域，则根据所选区域的范围更新比例尺范围
          xScale.domain([xScale.invert(sel[0][0]), xScale.invert(sel[1][0])]);
          // 根据选择区域的范围更新 y 轴的域
          const y0 = sel[0][1];
          const y1 = sel[1][1];
          const yValues = columns.filter((column) => {
            const y = yScale(column);
            return y >= y0 && y <= y1;
          });
          yScale.domain(yValues);

          // 计算放大倍数
          const scaleX =
            (maxValue - minValue) / (xScale.domain()[1] - xScale.domain()[0]);
          const scaleY = (yValues.length - 1) / (columns.length - 1);
          const zoomScale = Math.max(scaleX, scaleY).toFixed(2); // 保留两位小数
          svg
            .append("text")
            .attr("class", "tooltip")
            .attr("x", dimensions.width.value - marginRight - 100)
            .attr("y", marginTop)
            .text(`Scale: ${zoomScale}`);
        }

        // 更新坐标轴
        svg
          .select(".axis-x")
          .attr("transform", `translate(0,${height - marginBottom})`)
          .call(d3.axisBottom(xScale));
        svg
          .select(".axis-y")
          .call(d3.axisLeft(yScale).tickSize(0))
          .attr("transform", `translate(${xScale(0)},0)`);
        yAxis
          .selectAll("text")
          .style("text-anchor", "start") // 设置文本锚点为起始位置
          .attr("transform", `translate(${-xScale(0) + 15})`);
        // 更新散点位置
        svg.selectAll("circle").remove();

        svg
          .selectAll("circle")
          .data(
            data.filter((d) => {
              return (
                typeof xScale(d.value) !== "undefined" &&
                typeof yScale(d.column) !== "undefined"
              );
            })
          ) // 将一维数组绑定到选择集
          .enter()
          .append("circle")
          .attr("r", 5)
          .style("fill", (d) => colorScale(d.value))
          .attr("cx", (d, i) => xScale(d.value)) // 使用数据和索引来计算 x 坐标
          .attr("cy", (d, i) => yScale(d.column)) // 使用数据和索引来计算 y 坐标
          .on("click", (event, d, i) => {
            console.log("click", d);
          });

        // 移除之前的刷子绘制框
        svg.selectAll(".brush .selection").attr("width", 0);
      }
    });
    return { datas, shap, divRef, loading };
  },
  mounted() {},
  methods: {},
});
</script>

<style>
.axis .tick text {
  fill: #222;
  pointer-events: none;
  z-index: 10000;
  font-size: 16px;
}
.axis.active .tick text {
  opacity: 1;
  font-weight: bold;
}
</style>

<style scoped>
svg :deep(.tooltip) {
  display: block;
  font-weight: bold;
  opacity: 1 !important;
}
</style>
