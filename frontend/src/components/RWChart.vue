<!--
 * @Author       : Outsider
 * @Date         : 2024-03-16 22:55:49
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-03-27 21:14:49
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\components\RWChart.vue
-->
<script>
import { defineComponent, watch, ref } from "vue";
import { useWindowSize, useResizeObserver } from "@vueuse/core";
import {
  select,
  scaleLinear,
  scaleOrdinal,
  scaleBand,
  axisLeft,
  axisBottom,
  format,
} from "d3";

export default defineComponent({
  props: {
    data: null,
    height: 200,
    colorScale: null,
  },
  setup(props) {
    let dimension = useWindowSize();
    let height = props.height;
    const data = props.data;
    let dimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };
    const colorScale = props.colorScale;

    const svgRef = ref(null);
    const wrapperRef = ref(null);
    const canvasRef = ref(null);

    const get_data_domain = (data) => {
      let max_1 = data.reduce(
        (max, d) => (d.reads > max ? d.reads : max),
        data[0].reads
      );
      let max_2 = data.reduce(
        (max, d) => (d.writes > max ? d.writes : max),
        data[0].writes
      );
      return [0, Math.max(max_1, max_2)];
    };

    useResizeObserver(wrapperRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      dimensions.width.value = width;
      dimensions.height.value = height;
      // console.log("RW", width, height);
    });

    watch([dimensions.width, dimensions.height], () => {
      if (!dimensions) return;
      if (data.length < 1) return;

      let data_domain = get_data_domain(data);
      let leftPadding = 60;
      select(wrapperRef.value).style("padding", `0 20px 20px ${leftPadding}px`);

      const svg = select(svgRef.value).attr("height", height);

      const xScale = scaleBand()
        .domain(
          data.map((d) => {
            return d.group;
          })
        )
        .range([0, dimensions.width.value])
        .padding(0.1);
      svg
        .select(".x-axis")
        .attr("transform", "translate(0," + height + ")")
        // .call(axisBottom(xScale).tickSize(0))
        .call(axisBottom(xScale))
        .selectAll("text")
        .attr("y", 0)
        .attr("x", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end");

      const yScale = scaleLinear().domain(data_domain).range([height, 0]);
      svg.select(".y-axis").call(
        axisLeft(yScale)
          .ticks(4)
          .tickFormat((d) => d + "%")
      );

      var xSubgroup = scaleBand()
        .domain(["reads", "writes"])
        .range([0, xScale.bandwidth()])
        .padding([0.05]);

      var colorScale = scaleOrdinal()
        .domain(["reads", "writes"])
        .range(["#e41a1c", "#377eb8"]);

      function make_y_gridlines() {
        return axisLeft(yScale).tickValues(
          yScale.ticks(5).concat(yScale.domain())
        );
      }

      // add the Y gridlines
      svg
        .selectAll(".grid")
        .data([1])
        .join("g")
        .attr("class", "axis grid")
        .call(
          make_y_gridlines().tickSize(-dimensions.width.value).tickFormat("")
        );

      svg
        .selectAll(".bar-group")
        .data(["group"])
        .join("g")
        .attr("class", "bar-group")
        .selectAll("g")
        .data(data)
        .join("g")
        .attr("transform", function (d) {
          return "translate(" + xScale(d.group) + ",0)";
        })
        .selectAll("rect")
        .data(function (d) {
          return ["reads", "writes"].map(function (key) {
            return { key: key, value: Number(d[key]) };
          });
        })
        .join("rect")
        .attr("x", function (d) {
          return xSubgroup(d.key);
        })
        .attr("y", function (d) {
          return yScale(d.value);
        })
        .attr("width", xSubgroup.bandwidth())
        .attr("height", function (d) {
          return height - yScale(d.value);
        })
        .attr("fill", function (d) {
          return colorScale(d.key);
        })
        .selectAll("text")
        .attr("text-anchor", "start");

      // Draw tags
      const tags = [
        {
          title: "Reads",
          x: 0,
          y: 0,
          width: 60,
          height: 20,
          tx: 8,
          ty: 15,
          fill: "#e41a1c",
        },
        {
          title: "Writes",
          x: 0,
          y: 22,
          width: 60,
          height: 20,
          tx: 8,
          ty: 38,
          fill: "#377eb8",
        },
      ];
      const tag = svg
        .selectAll(".tags")
        .data([1])
        .join("g")
        .attr("class", "tags")
        .attr("transform", `translate( ${dimensions.width.value - 50}, 10)`);

      tag
        .selectAll("rect")
        .data(tags)
        .join("rect")
        .attr("x", (d) => d.x)
        .attr("y", (d) => d.y)
        .attr("width", (d) => d.width)
        .attr("height", (d) => d.height)
        .attr("fill", (d) => d.fill);

      tag
        .selectAll("text")
        .data(tags)
        .join("text")
        .text((d) => d.title)
        .attr("x", (d) => d.tx)
        .attr("y", (d) => d.ty)
        .attr("fill", "white");
    });
    return { wrapperRef, svgRef, canvasRef };
  },
});
</script>

<template>
  <div ref="wrapperRef">
    <svg id="group-bar-chart" ref="svgRef">
      <g class="x-axis"></g>
      <g class="y-axis"></g>
    </svg>
    <br />
    <br />
  </div>
</template>

<style>
#group-bar-chart .x-axis text {
  transform: rotate(-45deg) translate(-15px, 10px);
}

svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}

svg text {
  pointer-events: none;
  font-size: 16px;
}
/* 
.axis line,
.axis path {
	fill: none;
	stroke: #000;
	shape-rendering: crispEdges;
}

.axis text {
	text-shadow: 0 1px 0 #fff, 1px 0 0 #fff, 0 -1px 0 #fff, -1px 0 0 #fff;
	cursor: move;
} */
</style>
