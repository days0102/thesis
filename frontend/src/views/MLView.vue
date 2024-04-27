<!--
 * @Author       : Outsider
 * @Date         : 2024-04-06 10:10:25
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-04-23 09:48:08
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\views\MLView.vue
-->
<template>
  <splitpanes class="default-theme">
    <pane size="65" :key="1" style="background-color: inherit;">
      <div v-loading="loading" style="margin: 3px; border: 1px;" ref="divRef">
        <svg ref="shap"></svg>
      </div>
      <!-- <el-dialog v-model="visible" title="SHAP" :fullscreen="true" center append-to-body destroy-on-close @close="() => {
        visible = false;
      }
        " custom-class="dialog">
        <template #header>
          <div class="dialog-header" style="text-align: center; margin: 5px">
            <h3 style="margin-bottom: 12px">SHAP</h3>
          </div>
        </template>
        <div style="text-align: center">
          <h3>Force Plot</h3>
          <img :src="force_img" alt="SHAP Image" class="shap-image" />
          <h3 style="margin-top:25px">Local Feature Importance</h3>
          <img :src="bar_img" alt="SHAP Image" class="shap-image" />
        </div>
      </el-dialog> -->
    </pane>
    <pane ref="rightRef" size="35" :key="2" style="overflow-y: auto;background-color: inherit;padding: 5px;">
      <div v-if="select_node == -1">
        <h3>请选择一个作业</h3>
      </div>
      <div v-else v-loading="fig_loading" style="text-align: center">
        <!-- <h3>Node-{{ select_node }}</h3>
        <h4>AppName : {{ app_name }}</h4> -->
        <div v-html="html_data"></div>
        <h5> force-plot</h5>
        <img v-if="!fig_loading" :src="force_img" alt="SHAP Image" class="shap-image" />
        <h5 style="margin-top:25px"> local-feature-importance</h5>
        <img v-if="!fig_loading" :src="bar_img" alt="SHAP Image" class="shap-image" />
      </div>
    </pane>
  </splitpanes>
</template>

<script>
import { defineComponent, onMounted, ref, watch } from "vue";
import { useWindowSize, useResizeObserver } from "@vueuse/core";
import { useRoute } from "vue-router";
import * as d3 from "d3";

import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

import { ElMessage } from 'element-plus'

export default defineComponent({
  components: {
    Splitpanes, Pane
  },
  setup() {
    const visible = ref(false);

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
    const df = ref(null);
    const shap = ref(null);
    const divRef = ref(null);
    const rightRef = ref(null);
    const loading = ref(true);
    const fig_loading = ref(true);
    const html_data = ref('');

    const colorbar = ref(true);

    let select_node = ref(-1)

    let force_img = ref(null);
    let bar_img = ref(null);

    let app_name = ref('')

    useResizeObserver(divRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      dimensions.width.value = width;
      dimensions.height.value = height;
      // console.log("ml", width, height);
    });

    let right_width = ref(0)

    useResizeObserver(rightRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      right_width.value = width
      // console.log("Right", right_width.value, height);
    });

    onMounted(() => {
      fetch(`/api/ml/${cid}`, {
        method: "GET",
      })
        .then((d) => {
          // console.log(d.json())
          return d.json();
        })
        .then((d) => {
          // console.log(d);
          // console.log(JSON.parse(d.shap))
          datas.value = JSON.parse(d.shap);
          df.value = JSON.parse(d.data);

          // console.log("d", datas);
          // console.log("d", df);
          loading.value = false;

          // fetch(`/api/ml/${cid}/data`, {
          //   method: "GET",
          //   mode: "cors",
          //   cache: "no-cache",
          //   credentials: "same-origin",
          //   headers: new Headers({
          //     "Content-Type": "application/json",
          //   }),
          //   redirect: "follow",
          //   data: JSON.stringify({
          //     columns: datas.value.columns,
          //   }),
          // })
          //   .then((d) => {
          //     // console.log(d.json())
          //     return d.json();
          //   })
          //   .then((d) => {
          //     console.log(d);
          //     df.value = d;
          //     loading.value = false;
          //   });
        }).catch(() => {
          ElMessage.error({
            duration: 0,
            showClose: true,
            message: 'Oops, 服务端错误.',
            type: 'error',
            grouping: true,
          })
        });
    });

    watch([datas, dimensions.width, dimensions.height], () => {
      // console.log(dimensions);
      // console.log("data", datas);
      if (datas.value == null) return;

      const structDatas = (data, columns, df_data) => {
        let structData = [];
        // console.log(data, columns);
        for (let v in data) {
          for (let c in columns) {
            // console.log(v, c);
            structData.push({
              index: v,
              value: data[v][c],
              column: columns[c],
              data: df_data[v][c],
            });
          }
        }
        return structData;
      };

      const data = structDatas(
        datas.value.data,
        datas.value.columns,
        df.value.data
      );
      // console.log(data);

      const marginTop = 25;
      const marginRight = 20;
      const marginBottom = 35;
      const marginLeft = 280;

      const svgPadding = 10;
      const svgMargin = 20

      // 获取所有列名（纵坐标）
      var columns = datas.value.columns;

      // 获得 data 中的所有值
      const allValues = datas.value.data.flat();

      const all_data = df.value.data.flat();

      const get_min_max_value = (data, columns) => {
        const result = [];
        // for (let v in data) {
        //   result.push([Math.min(...data[v]), Math.max(...data[v])]);
        //   console.log(data[v]);
        //   console.log(Math.min(...data[v]));
        //   console.log(Math.max(...data[v]));
        // }
        for (let j in columns) {
          // 初始化列的最大值和最小值为第一个元素
          let max = data[0][j];
          let min = data[0][j];
          for (let i in data) {
            // console.log(i, j);
            max = Math.max(max, data[i][j]);
            min = Math.min(min, data[i][j]);
          }
          result.push({
            column: columns[j],
            min: min,
            max: max,
          });
        }
        return result;
      };
      const min_max_value = get_min_max_value(df.value.data, df.value.columns);
      // console.log(min_max_value);

      const build_colorScales = (rangs) => {
        const cs = {};
        rangs.forEach((item) => {
          // 使用 item.column 作为对象的键，值是一个函数
          cs[item.column] = d3
            .scaleLinear()
            .domain([item.min, item.max]) // 设置输入的数据范围
            .range(["blue", "red"]); // 设置颜色范围
        });
        return cs;
      };

      const getCharacterWidth = () => {
        // 创建一个隐藏的span元素，用于计算字符宽度
        const placeholderText = "A"
        const span = document.createElement("span");
        span.textContent = placeholderText;

        // 设置span元素样式（确保与实际文本相同的样式）
        span.style.visibility = "hidden";

        // 将span元素添加到body中
        document.body.appendChild(span);
        // 获取span元素的宽度
        const characterWidth = span.offsetWidth;

        // 从body中移除span元素
        document.body.removeChild(span);

        // 计算一行能容纳的字符数
        const characters = Math.floor(right_width.value / characterWidth);

        return characters;
      }

      // console.log(build_colorScales(min_max_value));

      // 计算最大值和最小值
      const maxValue = Math.max(...allValues);
      const minValue = Math.min(...allValues);

      // console.log("最大值:", maxValue);
      // console.log("最小值:", minValue);
      const colorScale = build_colorScales(min_max_value);

      // 添加颜色条说明
      const legendWidth = 20;
      const legendHeight = height - marginTop - marginBottom;
      const legendMargin = 20;

      // 计算预留空间所对应的数值范围
      const paddingPercentage = 0.1; // 10% 的预留空间
      const padding = (maxValue - minValue) * paddingPercentage;
      // 定义横轴比例尺
      var xScale = d3
        .scaleLinear()
        .domain([minValue - padding, maxValue + padding])
        .range([marginLeft, dimensions.width.value - marginRight - legendWidth - legendMargin]);
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
        .style("width", dimensions.width.value - svgPadding + "px")
        .style("height", height - svgPadding + "px")
      // .style("margin", `${svgMargin}`);


      // 创建一个组用于放置颜色条
      const legendGroup = svg.append("g")
        .attr("transform", `translate(${dimensions.width.value - marginRight - legendWidth}, ${marginTop})`);

      const legendGradient = svg.append("defs")
        .append("linearGradient")
        .attr("id", "legendGradient")
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "0%").attr("y2", "100%").style("padding", `20px 20px 20px 20px`);
      legendGradient.append("stop").attr("offset", "0%").style("stop-color", "red");
      legendGradient.append("stop").attr("offset", "100%").style("stop-color", "blue");
      svg.append("rect")
        .attr("x", dimensions.width.value - marginRight - legendWidth)
        .attr("y", marginTop)
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#legendGradient)");
      // 添加文本标签
      svg.append("text")
        .attr("x", dimensions.width.value - marginRight - legendWidth / 2)
        .attr("y", marginTop - legendMargin / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "end")
        .text("high")
        .attr("fill", "#707070");
      // svg.append("text")
      //   .attr("x", dimensions.width.value - marginRight - legendWidth / 2)
      //   .attr("y", height - marginTop + legendMargin)
      //   .attr("dy", "0.35em")
      //   .attr("text-anchor", "end")
      //   .text("Low");

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
        .attr("transform", `translate(${-xScale(0) + 15})`)
        .attr("fill", "#707070");

      // 添加散点
      svg
        .selectAll("circle")
        .data(data) // 将一维数组绑定到选择集
        .enter()
        .append("circle")
        .attr("r", 5)
        .style("fill", (d) => colorScale[d.column](d.data))
        .attr("cx", (d, i) => xScale(d.value)) // 使用数据和索引来计算 x 坐标
        .attr("cy", (d, i) => yScale(d.column)) // 使用数据和索引来计算 y 坐标
        .on("click", (event, d) => {
          fig_loading.value = true;
          // console.log("click", d);
          select_node.value = d.index
          fetch(`/api/ml/${cid}/shap/${d.index}`, {
            method: "post",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            body: JSON.stringify({
              width: getCharacterWidth(),
            }),
            headers: new Headers({
              "Content-Type": "application/json",
            }),
            redirect: "follow",
          })
            .then((v) => {
              return v.json();
            })
            .then((v) => {
              // console.log(v);
              if (v.status === 0) {
                force_img.value = "data:image/jpg;base64," + v.force_image;
                bar_img.value = "data:image/jpg;base64," + v.bar_image;
                app_name.value = v.app
                let h = v.html_data
                h = h.replace("body {", "tbody {");
                h = h.replace(
                  "td, p, li, th {",
                  "tbody td, tbody p, tbody li, tbody th {"
                );
                html_data.value = h
                fig_loading.value = false;
              }
              else {
                ElMessage.error('Oops, 请刷新页面.')
              }
            }).catch(() => {
              ElMessage.error({
                duration: 0,
                showClose: true,
                message: 'Oops, 服务端错误.',
                type: 'error',
                grouping: true,
              })
            });
          visible.value = true;
        }).on('mouseenter', function () {
          d3.select(this).transition()
            .duration(200)
            .attr("r", 10);
        }).on('mouseleave', function () {
          d3.select(this).transition()
            .duration(200)
            .attr("r", 5);
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
        // console.log(sel);
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

          // // 计算放大倍数
          // const scaleX =
          //   (maxValue - minValue) / (xScale.domain()[1] - xScale.domain()[0]);
          // const scaleY = (yValues.length - 1) / (columns.length - 1);
          // const zoomScale = Math.max(scaleX, scaleY).toFixed(2); // 保留两位小数
          // svg
          //   .append("text")
          //   .attr("class", "tooltip")
          //   .attr("x", dimensions.width.value - marginRight - 100)
          //   .attr("y", marginTop)
          //   .text(`Scale: ${zoomScale}`);
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
          .attr("transform", `translate(${-xScale(0) + 15})`)
          .attr("fill", "#707070");
        // 更新散点位置
        svg.selectAll("circle").remove();

        svg
          .selectAll("circle")
          .data(
            data.filter((d) => {
              return (
                typeof xScale(d.value) !== "undefined" &&
                xScale(d.value) > marginLeft &&
                xScale(d.value) < dimensions.width.value - legendWidth - legendMargin - svgMargin &&
                typeof yScale(d.column) !== "undefined"
              );
            })
          ) // 将一维数组绑定到选择集
          .enter()
          .append("circle")
          .attr("r", 5)
          .style("fill", (d) => colorScale[d.column](d.data))
          .attr("cx", (d, i) => xScale(d.value)) // 使用数据和索引来计算 x 坐标
          .attr("cy", (d, i) => yScale(d.column)) // 使用数据和索引来计算 y 坐标
          .on("click", (event, d, i) => {
            // console.log("click", d);
            fig_loading.value = true;
            select_node.value = d.index

            fetch(`/api/ml/${cid}/shap/${d.index}`, {
              method: "post",
              mode: "cors",
              cache: "no-cache",
              credentials: "same-origin",
              body: JSON.stringify({
                width: getCharacterWidth(),
              }),
              headers: new Headers({
                "Content-Type": "application/json",
              }),
              redirect: "follow",
            })
              .then((v) => {
                return v.json();
              })
              .then((v) => {
                // console.log(v);
                if (v.status === 0) {
                  force_img.value = "data:image/jpg;base64," + v.force_image;
                  bar_img.value = "data:image/jpg;base64," + v.bar_image;
                  app_name.value = v.app
                  let h = v.html_data
                  h = h.replace("body {", "tbody {");
                  h = h.replace(
                    "td, p, li, th {",
                    "tbody td, tbody p, tbody li, tbody th {"
                  );
                  html_data.value = h
                  fig_loading.value = false;
                }
                else {
                  ElMessage.error('Oops, 请刷新页面.')
                }
              }).catch(() => {
                ElMessage.error({
                  duration: 0,
                  showClose: true,
                  message: 'Oops, 服务端错误.',
                  type: 'error',
                  grouping: true,
                })
              })
            visible.value = true;
          }).on('mouseenter', function () {
            d3.select(this).transition()
              .duration(200)
              .attr("r", 10);
          }).on('mouseleave', function () {
            d3.select(this).transition()
              .duration(200)
              .attr("r", 5);
          });

        // 移除之前的刷子绘制框
        svg.selectAll(".brush .selection").attr("width", 0);
      }
    });
    return {
      datas, shap, divRef, loading, visible, force_img,
      bar_img, colorbar, fig_loading, select_node, app_name,
      html_data, rightRef
    };
  },
  mounted() { },
  methods: {
  },
});
</script>

<style>
.axis .tick text {
  fill: #222;
  pointer-events: none;
  z-index: 10000;
  font-size: 14px;
  color: #707070;
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

.shap-image {
  max-width: 100%;
  /* 图片最大宽度为容器的100% */
  max-height: 100%;
  /* 图片最大高度为容器的100% */
  overflow: scroll;
}
</style>

<style lang="scss">
.dialog {
  .ep-dialog__header {
    pointer-events: auto !important;
    padding: 5px;
  }

  .ep-dialog__body {
    pointer-events: auto !important;
    overflow: auto;
    padding: 5px 25px;
  }
}
</style>
