<!--
 * @Author       : Outsider
 * @Date         : 2024-03-16 09:06:49
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-04-02 22:33:55
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\components\BarChart.vue
-->
<script lang="js">
import { watch, ref, defineComponent } from "vue";

import { useWindowSize, useResizeObserver } from "@vueuse/core";

import {
  select,
  scaleLinear,
  scaleBand,
  axisLeft,
  axisBottom,
  max,
  scaleOrdinal,
  schemeSet1,
} from "d3";

export default defineComponent({
  props: {
    data: null,
    colorScale: null,
  },
  watch: {
    // 监听到父组件传递过来的数据后，加工一下，
    // 存到data中去，然后在页面上使用
    data(newnew, oldold) {
      console.log("监听", newnew, oldold);
    },
  },
  setup(props) {
    // console.log("barchart", props.data);
    const data = props.data;
    const colorScale = props.colorScale;
    // console.log("BarChart", props);

    const divRef = ref(null);

    const svgRef = ref(null);
    const wrapperRef = ref();
    let dimension = useWindowSize();
    let height = 100;
    let dimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };
    useResizeObserver(divRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      dimensions.width.value = width;
      dimensions.height.value = height;
      // console.log(width, height);
    });

    // We will manually calculate how much margin to assign based on the length of the longest name
    const calcWidthOfName = (name) => {
      if (name.length < 4) return name.length * 16;
      if (name.length >= 4 && name.length <= 8) return name.length * 12;
      // if (name.length > 8 && name.length < 20) return name.length * 9;
      // if (name.length > 20) return name.length * 8.3;
    };

    const nameMap = {};

    const shortenName = (data) => {
      for (let i in data) {
        let name = data[i].key;
        if (name.length > 14) {
          data[i].key = name.slice(0, 10) + "...";
        }
        nameMap[data[i].key] = name;
      }
      return data;
    };
    shortenName(data);
    // console.log(nameMap)

    watch([dimensions.width, dimensions.height], (newValue, oldValue) => {
      // Return if no data is available
      // select("#dialog-box").selectAll("*").remove();
      // select(svgRef.value).selectAll("*").remove();
      // console.log(data);
      if (data.length < 1) return;

      // shotening names that are too large from the node

      // Adjusting the container to fit the svg
      // let leftPadding = max(data.map((d) => calcWidthOfName(d.key)));
      let leftPadding = 80;
      select(divRef.value).style("padding", `0 50px 30px ${leftPadding}px`);

      // Main drawing canvas
      // console.log("svgRef", svgRef.value);
      const svg = select(svgRef.value).attr("height", height);

      // Define our scales
      const xScale = scaleLinear()
        .domain([0, max(data.map((d) => d.value))])
        .range([0, dimensions.width.value]);

      const yScale = scaleBand()
        .domain(data.map((d) => d.key))
        .range([0, height])
        .padding(0.1);

      // Define and draw our axis
      const xAxis = axisBottom(xScale).ticks(2);
      // svg
      //   .join(".x-axis")
      //   .style("transform", `translateY(${height}px)`)
      //   .call(xAxis);
      svg
        .select(".x-axis")
        .style("transform", `translateY(${height}px)`)
        .call(xAxis);

      const yAxis = axisLeft(yScale);
      // svg.join(".y-axis").call(yAxis);

      const yAxisGroup = svg.select(".y-axis").call(yAxis);

      yAxisGroup
        .selectAll("text")
        .on("mouseenter", function (event, text) {
          // todo 文本过长才添加事件 滚动
          // console.log(text)
          select(this).text(nameMap[text]);
        })
        .on("mouseleave", function (event, text) {
          // console.log(text)
          select(this).text(text);
        });

      // Draw the rect to their proper position
      svg
        .selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", (d) => xScale(0))
        .attr("y", (d) => yScale(d.key))
        .attr("width", (d) => xScale(d.value))
        .attr("height", yScale.bandwidth())
        .attr("fill", (d) => {
          // console.log(d)
          if (colorScale != null) {
            if (d.key === "other") {
              return "#DEDEDE";
            } else {
              // console.log(colorScale(d.key));
              return colorScale(nameMap[d.key]);
            }
          }
        })
        .on("mouseenter", (event, d) => {
          svg
            .selectAll(".tooltip")
            .data([d])
            .join("text")
            .attr("class", "tooltip")
            .attr("x", xScale(d.value) / 2)
            .attr("y", yScale(d.key) + yScale.bandwidth() * 3 / 4)
            .text(d.value)
            .attr("text-anchor", "middle")
            .transition()
            .attr("opacity", 1);
        })
        .on("mouseleave", () => svg.select(".tooltip").remove())
        .transition();

      // // 选择坐标轴上的文本元素，并设置文本内容
      // select(".y-axis text").text(function () {
      //   // 获取原始文本内容
      //   let text = select(this).text();
      //   console.log('text',text)
      //   // 如果文本长度超过最大长度，则截取并添加省略号
      //   if (text.length >10) {
      //     return text.substring(0, 10) + "...";
      //   } else {
      //     return text;
      //   }
      // });
      select(".y-axis")
        .selectAll(".tick")
        .each(function (d, i) {
          // select(this).select("text").attr("width", 10);
          // console.log("d i",d,i)
          // let text = select(this).text();
          // console.log('text',text)
          // // 如果文本长度超过最大长度，则截取并添加省略号
          // if (text.length >10) {
          //   select(this).text(text.substring(0, 10) + "...");
          // } else {
          //   select(this).text(text);
          // }
          // text = select(this).text();
          // console.log('af text',text)
        });
    });
    return { divRef, svgRef };
  },
});
</script>

<template>
  <div ref="divRef">
    <svg ref="svgRef">
      <g class="x-axis"></g>
      <g class="y-axis"></g>
    </svg>
  </div>
</template>

<style scoped>
svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}
svg :deep(text) {
  pointer-events: all;
  font-size: 15px;
}

svg :deep(.tooltip) {
  display: block;
  font-weight: bold;
  opacity: 1 !important;
}
</style>
