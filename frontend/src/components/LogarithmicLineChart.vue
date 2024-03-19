<script>
import { defineComponent, watch, ref } from "vue";
import * as d3 from "d3";
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
import { useWindowSize, useResizeObserver } from "@vueuse/core";

export default defineComponent({
  props: {
    data: null,
    colorScale: null,
    height: 200,
  },
  setup(props) {
    const data = props.data;
    const colorScale = props.colorScale;

    const colorBy = "user";

    let dimension = useWindowSize();
    let height = props.height;
    let comDimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };

    const box = ref(null);
    const wrapperRef = ref(null);
    const canvasRef = ref(null);

    useResizeObserver(wrapperRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      comDimensions.width.value = width;
      comDimensions.height.value = height;
      console.log("LogLine", width, height);
    });

    const get_max_and_min_value_of_all_dimensions = (data) => {
      const max_value_1 = data.reduce(
        (max, node) =>
          node["I/O throughput [MiB/s]"] > max
            ? node["I/O throughput [MiB/s]"]
            : max,
        data[0]["I/O throughput [MiB/s]"]
      );
      const max_value_2 = data.reduce(
        (max, node) =>
          node["I/O volume [GiB]"] > max ? node["I/O volume [GiB]"] : max,
        data[0]["I/O volume [GiB]"]
      );
      const max_value_3 = data.reduce(
        (max, node) => (node["Runtime [s]"] > max ? node["Runtime [s]"] : max),
        data[0]["Runtime [s]"]
      );
      const max_value_4 = data.reduce(
        (max, node) =>
          node["R/W accesses (in 1000s)"] > max
            ? node["R/W accesses (in 1000s)"]
            : max,
        data[0]["R/W accesses (in 1000s)"]
      );
      const max_value_5 = data.reduce(
        (max, node) =>
          node["App size (nprocs)"] > max ? node["App size (nprocs)"] : max,
        data[0]["App size (nprocs)"]
      );
      const max_value_6 = data.reduce(
        (max, node) =>
          node["Files (count)"] > max ? node["Files (count)"] : max,
        data[0]["Files (count)"]
      );

      // Calc min Value
      const min_value_1 = data.reduce(
        (min, node) =>
          node["I/O throughput [MiB/s]"] < min
            ? node["I/O throughput [MiB/s]"]
            : min,
        data[0]["I/O throughput [MiB/s]"]
      );
      const min_value_2 = data.reduce(
        (min, node) =>
          node["I/O volume [GiB]"] < min ? node["I/O volume [GiB]"] : min,
        data[0]["I/O volume [GiB]"]
      );
      const min_value_3 = data.reduce(
        (min, node) => (node["Runtime [s]"] < min ? node["Runtime [s]"] : min),
        data[0]["Runtime [s]"]
      );
      const min_value_4 = data.reduce(
        (min, node) =>
          node["R/W accesses (in 1000s)"] < min
            ? node["R/W accesses (in 1000s)"]
            : min,
        data[0]["R/W accesses (in 1000s)"]
      );
      const min_value_5 = data.reduce(
        (min, node) =>
          node["App size (nprocs)"] < min ? node["App size (nprocs)"] : min,
        data[0]["App size (nprocs)"]
      );
      const min_value_6 = data.reduce(
        (min, node) =>
          node["Files (count)"] < min ? node["Files (count)"] : min,
        data[0]["Files (count)"]
      );

      return [
        Math.min(
          min_value_1,
          min_value_2,
          min_value_3,
          min_value_4,
          min_value_5,
          min_value_6
        ),
        Math.max(
          max_value_1,
          max_value_2,
          max_value_3,
          max_value_4,
          max_value_5,
          max_value_6
        ),
      ];
    };

    const generateAxisName = (d) => {
      const units = {
        "I/O THROUGHPUT": "[MiB/s]",
        "I/O VOLUME": "[GiB]",
        RUNTIME: "[s]",
        "R/W ACCESSES": "[# of accesses]",
        "APP SIZE": "[# of processes]",
        FILES: "[# of files]",
      };

      let word = d.key.split("(");
      if (word.length < 2) {
        let w = d.key.split("[")[0].toUpperCase().trim();
        return `<tspan>${w}</tspan> <tspan x="0" dx="0" dy="10">${units[w]}</tspan>`;
      }
      return `<tspan>${word[0]}</tspan> <tspan x="0" dx="0" dy="10">${
        units[word[0].toUpperCase().trim()]
      }</tspan>`;
    };

    watch([comDimensions.width, comDimensions.height], () => {
      if (!comDimensions) return;

      const yAxisCoordinates = "per-column";

      let width = comDimensions.width.value;
      let margin = { top: 10, left: 80, right: 20, bottom: 90 };
      let innerWidth = width - margin.left - margin.right;
      let innerHeight = height - margin.top - margin.bottom;
      let devicePixelRatio = window.devicePixelRatio || 1;
      let data_domain =
        yAxisCoordinates != "per-column"
          ? log_scale_min_max
          : get_max_and_min_value_of_all_dimensions(data);
      var types = {
        Number: {
          key: "Number",
          coerce: function (d) {
            return +d;
          },
          extent: d3.extent,
          within: function (d, extent, dim) {
            return (
              // extent[0] <= dim.scale(d) && dim.scale(d) <= extent[1]
              d3.scaleLinear().range([0, innerHeight])
            );
          },
          defaultScale: d3.scaleLinear().range([innerHeight, 0]),
        },
        String: {
          key: "String",
          coerce: String,
          extent: function (data) {
            return data.sort();
          },
          within: function (d, extent, dim) {
            return extent[0] <= dim.scale(d) && dim.scale(d) <= extent[1];
          },
          defaultScale: d3.scalePoint().range([0, innerHeight]),
        },
      };

      var dimensions = [
        {
          key: "I/O throughput [MiB/s]",
          type: types["Number"],
          scale: d3.scaleLog().range([innerHeight, 0]),
        },
        {
          key: "I/O volume [GiB]",
          type: types["Number"],
          scale: d3.scaleLog().range([innerHeight, 0]),
        },
        {
          key: "Runtime [s]",
          type: types["Number"],
          scale: d3.scaleLog().range([innerHeight, 0]),
        },
        {
          key: "R/W accesses (in 1000s)",
          type: types["Number"],
          scale: d3.scaleLog().range([innerHeight, 0]),
        },
        {
          key: "App size (nprocs)",
          type: types["Number"],
          scale: d3.scaleLog().range([innerHeight, 0]),
        },
        {
          key: "Files (count)",
          type: types["Number"],
          scale: d3.scaleLog().range([innerHeight, 0]),
        },
      ];

      var xscale = d3
        .scalePoint()
        .domain(d3.range(dimensions.length))
        .range([0, innerWidth]);

      // Creates axis ticks at powers of 10
      function log10tick(x) {
        if (Math.log10(x).toFixed(3) % 1 === 0) {
          if (x >= 1 && x < 10 ** 3) return String(x);
          if (x >= 10 ** 3 && x < 10 ** 6) return String(x / 10 ** 3) + "K";
          if (x >= 10 ** 6 && x < 10 ** 9) return String(x / 10 ** 6) + "M";
          if (x >= 10 ** 9 && x < 10 ** 12) return String(x / 10 ** 9) + "G";
          if (x >= 10 ** 12 && x < 10 ** 15) return String(x / 10 ** 12) + "T";
          if (x >= 10 ** 15 && x < 10 ** 18) return String(x / 10 ** 15) + "P";
        }

        return "";
      }

      var yAxis = d3.axisLeft();

      d3.select(wrapperRef.value)
        .style("width", width + "px")
        .style("height", height + "px")
        .attr("class", "parcoords");

      var svg = d3
        .select(box.value)
        .style("width", width + "px")
        .style("height", height + "px");

      svg = svg
        .selectAll(".axis-container")
        .data([""])
        .join("g")
        .attr("class", "axis-container")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var canvas = d3
        .select(canvasRef.value)
        .attr("width", innerWidth * devicePixelRatio)
        .attr("height", innerHeight * devicePixelRatio)
        .style("width", innerWidth + "px")
        .style("height", innerHeight + "px")
        .style("margin-top", margin.top + "px")
        .style("margin-left", margin.left + "px");

      var ctx = canvas.node().getContext("2d");
      ctx.globalCompositeOperation = "darken";
      ctx.globalAlpha = 0.15;
      ctx.lineWidth = 1.5;
      ctx.scale(devicePixelRatio, devicePixelRatio);
      ctx.clearRect(0, 0, width, height);
      // console.log('in',innerWidth);

      var axes = svg
        .selectAll(".axis")
        .data(dimensions)
        .join("g")
        .attr("class", "axis")
        .attr("transform", function (d, i) {
          // console.log(d, i);
          // console.log("log", xscale(i));
          // console.log(innerWidth);
          // console.log("translate(" + xscale(i) + ")");
          return "translate(" + xscale(i) + ")";
        });

      data.forEach(function (d) {
        dimensions.forEach(function (p) {
          d[p.key] = !d[p.key] ? null : p.type.coerce(d[p.key]);
        });

        // truncate long text strings to fit in data table
        for (var key in d) {
          if (d[key] && d[key].length > 35) d[key] = d[key].slice(0, 36);
        }
      });

      // type/dimension default setting happens here
      dimensions.forEach(function (dim) {
        if (!("domain" in dim)) {
          // detect domain using dimension type's extent function
          // dim.domain = d3_functor(dim.type.extent)(
          // 	data.map(function (d) {
          // 		return d[dim.key];
          // 	})
          // );
          // dim.domain = [
          // 	d3.min(data.map((d) => Number(d[dim.key]))),
          // 	max_data_value,
          // ];

          dim.domain = [
            data_domain[0] > 1 ? 1 : data_domain[0],
            data_domain[1],
          ];
        }
        if (!("scale" in dim)) {
          // use type's default scale for dimension
          dim.scale = dim.type.defaultScale.copy();
        }
        dim.scale.domain(dim.domain);
      });

      const renderQueue = function (func) {
        var _queue = [], // data to be rendered
          _rate = 1000, // number of calls per frame
          _invalidate = function () {}, // invalidate last render queue
          _clear = function () {}; // clearing function

        var rq = function (data) {
          if (data) rq.data(data);
          _invalidate();
          _clear();
          rq.render();
        };

        rq.render = function () {
          var valid = true;
          _invalidate = rq.invalidate = function () {
            valid = false;
          };

          function doFrame() {
            if (!valid) return true;
            var chunk = _queue.splice(0, _rate);
            chunk.map(func);
            timer_frame(doFrame);
          }

          doFrame();
        };

        rq.data = function (data) {
          _invalidate();
          _queue = data.slice(0); // creates a copy of the data
          return rq;
        };

        rq.add = function (data) {
          _queue = _queue.concat(data);
        };

        rq.rate = function (value) {
          if (!arguments.length) return _rate;
          _rate = value;
          return rq;
        };

        rq.remaining = function () {
          return _queue.length;
        };

        // clear the canvas
        rq.clear = function (func) {
          if (!arguments.length) {
            _clear();
            return rq;
          }
          _clear = func;
          return rq;
        };

        rq.invalidate = _invalidate;

        var timer_frame =
          window.requestAnimationFrame ||
          window.webkitRequestAnimationFrame ||
          window.mozRequestAnimationFrame ||
          window.oRequestAnimationFrame ||
          window.msRequestAnimationFrame ||
          function (callback) {
            setTimeout(callback, 1);
          };

        return rq;
      };

      var render = renderQueue(draw).rate(200);

      ctx.clearRect(0, 0, width, height);
      ctx.globalAlpha = d3.min([0.85 / Math.pow(data.length, 0.3), 1]);
      render(data);

      axes
        .select("g")
        .attr("class", "needle")
        .each(function (d, i) {
          var renderAxis = yAxis
            .scale(d.scale)
            .tickValues(d.scale.ticks(3).concat(d.scale.domain()))
            .tickFormat((x) => log10tick(x));
          if (i !== 0) {
            d3.select(this).attr("class", "hide-axis").call(renderAxis);
          }
          d3.select(this).call(renderAxis);
        })
        .append("text")
        .attr("class", "title")
        .attr("x", function (d) {
          yAxis.scale(d.scale);
        })
        .attr("y", innerHeight)
        .html(function (d) {
          return generateAxisName(d);
        });

      function make_y_gridlines() {
        return d3
          .axisLeft(dimensions[0].scale)
          .tickValues(
            dimensions[0].scale.ticks(3).concat(dimensions[0].scale.domain())
          );
      }

      svg
        .append("g")
        .attr("class", "axis grid")
        .call(make_y_gridlines().tickSize(-innerWidth).tickFormat(""));

      // Add and store a brush for each axis.
      axes
        .append("g")
        .attr("class", "brush")
        .each(function (d) {
          d3.select(this).call(
            (d.brush = d3
              .brushY()
              .extent([
                [-10, 0],
                [10, innerHeight],
              ])
              .on("start", brushstart)
              .on("brush", brush)
              .on("end", brush))
          );
        })
        .selectAll("rect")
        .attr("x", -8)
        .attr("width", 16);

      function project(d) {
        return dimensions.map(function (p, i) {
          // check if data element has property and contains a value
          // I am remocing this check because of the null values in the data
          // For some reason, javascript is converting 0 to null in the object
          // if (!(p.key in d) || d[p.key] === null) return null;
          return [xscale(i), p.scale(Number(d[p.key]))];
        });
      }

      function draw(d) {
        ctx.strokeStyle = colorScale.domain().includes(d[colorBy])
          ? colorScale(d[colorBy])
          : "#DEDEDE";
        ctx.beginPath();
        var coords = project(d);
        coords.forEach(function (p, i) {
          // this tricky bit avoids rendering null values as 0
          if (p === null) {
            // this bit renders horizontal lines on the previous/next
            // dimensions, so that sandwiched null values are visible
            if (i > 0) {
              var prev = coords[i - 1];
              if (prev !== null) {
                ctx.moveTo(prev[0], prev[1]);
                ctx.lineTo(prev[0] + 6, prev[1]);
              }
            }
            if (i < coords.length - 1) {
              var next = coords[i + 1];
              if (next !== null) {
                ctx.moveTo(next[0] - 6, next[1]);
              }
            }
            return;
          }

          if (i === 0) {
            ctx.moveTo(p[0], p[1]);
            return;
          }

          ctx.lineTo(p[0], p[1]);
        });
        ctx.stroke();
      }

      function brushstart() {
        d3.event.sourceEvent.stopPropagation();
      }

      // Handles a brush event, toggling the display of foreground lines.
      function brush() {
        render.invalidate();

        var actives = [];
        svg
          .selectAll(".axis .brush")
          .filter(function (d) {
            return d3.brushSelection(this);
          })
          .each(function (d) {
            actives.push({
              dimension: d,
              extent: d3.brushSelection(this),
            });
          });

        var selected = data.filter(function (d) {
          if (
            actives.every(function (active) {
              var dim = active.dimension;
              // test if point is within extents for each active brush
              return dim.type.within(d[dim.key], active.extent, dim);
            })
          ) {
            return true;
          }
        });

        ctx.clearRect(0, 0, width, height);
        ctx.globalAlpha = d3.min([0.85 / Math.pow(selected.length, 0.3), 1]);
        render(selected);
      }
    });
    return { box, wrapperRef, canvasRef };
  },
});
</script>

<template>
  <div ref="wrapperRef">
    <div id="parChart2">
      <svg ref="box"></svg>
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<style scoped>
/* DEFAULTS */
svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}

svg circle {
  /* fill: #005073; */
  stroke: black;
  cursor: pointer;
}

svg circle:hover {
  fill: #1ebbd7;
}

svg text {
  pointer-events: none;
  font-size: 16px;
}

svg :deep(.tooltip) {
  display: block;
  font-weight: bold;
  opacity: 1 !important;
}

/* TREE COMPONENT STYLES*/
svg :deep(.link) {
  fill: none;
  stroke: gray;
}

svg /deep/ .name {
  font-size: 12px;
  fill: white;
}

svg :deep(.tooltipText) {
  font-size: 18px;
  fill: white;
}
svg :deep(.tooltipText2) {
  font-size: 18px;
  fill: white;
}

svg :deep(.dot) {
  fill: #005073;
  stroke: none;
}

/* SELECTED NODES */
.Alpha,
.Alpha-text {
  fill: red;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}
.Beta,
.Beta-text {
  fill: blue;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}
.Gamma,
.Gamma-text {
  fill: purple;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}
.Delta,
.Delta-text {
  fill: green;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}

/* Parallel Plot */
svg {
  font: 10px sans-serif;
}

.background path {
  fill: none;
  stroke: #ddd;
  shape-rendering: crispEdges;
}

.foreground path {
  fill: none;
  stroke: steelblue;
}

.brush .extent {
  fill-opacity: 0.3;
  stroke: #fff;
  shape-rendering: crispEdges;
}

.axis line,
.axis path {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.axis text {
  text-shadow:
    0 1px 0 #fff,
    1px 0 0 #fff,
    0 -1px 0 #fff,
    -1px 0 0 #fff;
  cursor: move;
}

#group-bar-chart .x-axis text {
  transform: rotate(-45deg) translate(-15px, 10px);
}

/* GLOBALS */
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

body {
  height: 100%;
  position: relative;
  overflow-y: scroll;
}

.row-fix {
  /* This will overwrite the margins bootstrap has on the row component*/
  margin: 0 !important;
  width: 100%;
}

#root {
  height: 100%;
}
/* App.js Styles */
.sidebar,
.main-content {
  padding: 0 !important;
}

.sidebar {
  background-color: #141414;
}

/* Navbar.js Styles */
#navbar {
  width: 100%;
  height: 75px;
  background-color: #141414;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 50px;
}

#headerLogo {
  height: 50px;
}

#viewMenu {
  height: 50px;
  color: rgb(106, 130, 255);
  z-index: 1001;
  display: flex;
  width: 75px;
  justify-content: space-around;
}

.grow {
  z-index: 10;
}
/* Sidemenu.js Styles */
#sidemenu {
  width: 100%;
  height: 100vh;
  background-color: #141414;
  color: #fff;
}

#sidemenu .side-menu-title {
  margin: 0;
  padding: 10px 0;
  display: block;
  width: 100%;
  text-align: center;
  text-transform: uppercase;
  font-size: 1.5em;
  letter-spacing: 4px;
  border-bottom: 1px solid #545454;
  font-weight: 400;
}

#sidemenu nav {
  margin: 0 20px;
}

#sidemenu ul li {
  font-size: 1em;
  height: 40px;
  margin-top: 5px;
  padding-left: 40px;
  cursor: pointer;
  line-height: 2.3;
  font-weight: 100;
  letter-spacing: 1px;
}

#sidemenu i {
  margin-right: 10px;
  line-height: 1.5;
  font-size: 1.2em;
}

#sidemenu ul li:hover {
  display: block;
  background-color: teal;
}

/* Dashboard.js Styles */
.title {
  margin: 0 20px;
  font-size: 1.5em;
  display: block;
  width: 100%;
  text-transform: uppercase;
  padding: 5px 10px;
  color: #a1a1a1;
  font-weight: 100;
  border-bottom: 1px solid#858585;
}

.chart-box {
  margin-top: 15px !important;
  flex-wrap: nowrap !important;
}
.dash-menu {
  padding: 0 !important;
  max-width: 60px !important;
  margin: 0 5px;
  float: left;
}
.dash-menu ul li {
  text-align: center;
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #141414;
  cursor: pointer;
}

/* .dash-menu ul {
	position: absolute;
} */

.dash-menu ul li i {
  font-size: 2em;
}

.tree-icon ul {
  margin-top: 10px;
}

/* DashColumn.js Styles */
.col-dash-head {
  background-color: #141414;
  width: 100%;
  height: 30px;
  color: #fff;
}

.col-dash-head i {
  line-height: 1.8;
  float: right;
  margin-right: 15px;
  cursor: pointer;
}

.col-title {
  color: 141414;
  font-size: 1.5em;
  margin-left: 15px;
  /* background-color: rgb(106, 130, 255); */
}

.form-row {
  /* overwrite bootstrap rules */
  margin: 0 !important;
  padding: 0 10px;
}

.form-check {
  /* overwrite bootstrap rules */
  padding-left: 2.5rem !important;
}

/* GraphGrid.js Styles */
.graph-grid {
  margin-bottom: 30px;
}

/* Material-UI Overwrite */
.MuiInputBase-root {
  display: block !important;
}

h3 {
  text-align: center;
}

.MuiAutocomplete-inputRoot[class*="MuiOutlinedInput-root"]
  .MuiAutocomplete-input:first-child {
  width: 100%;
}

.parcoords {
  display: block;
}

.parcoords svg,
.parcoords canvas {
  font: 10px sans-serif;
  position: absolute;
  display: block;
  width: 100%;
}

.parcoords canvas {
  opacity: 0.9;
  pointer-events: none;
}

.axis .title {
  font-size: 10px;
  transform: rotate(-45deg) translate(-85px, -25px);
  fill: #222;
}

#parChart2 .axis .title {
  transform: rotate(-45deg) translate(-70px, -20px) !important;
}

.axis line,
.axis path {
  stroke: #ccc;
  stroke-width: 1px;
}

.axis .tick text {
  fill: #222;
  pointer-events: none;
  z-index: 10000;
}

.axis.manufac_name .tick text,
.axis.food_group .tick text {
  opacity: 1;
}

.axis.active .title {
  font-weight: bold;
}

.axis.active .tick text {
  opacity: 1;
  font-weight: bold;
}

.brush .extent {
  fill-opacity: 0.3;
  stroke: #fff;
  stroke-width: 1px;
}

pre {
  width: 100%;
  height: 300px;
  margin: 6px 12px;
  tab-size: 40;
  font-size: 10px;
  overflow: auto;
}

/* hide axes except main axis */
.hide-axis .tick text,
.hide-axis .tick {
  opacity: 0;
}
</style>
