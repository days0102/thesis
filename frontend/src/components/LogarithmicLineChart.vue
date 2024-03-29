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
    // console.log(data);
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
      // console.log("LogLine", width, height);
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
      // console.log(width,margin,innerHeight,innerWidth)
      let devicePixelRatio = window.devicePixelRatio || 1;
      let data_domain =
        yAxisCoordinates != "per-column"
          ? log_scale_min_max
          : get_max_and_min_value_of_all_dimensions(data);
      // console.log("max_min", get_max_and_min_value_of_all_dimensions(data));
      var types = {
        Number: {
          key: "Number",
          coerce: function (d) {
            return +d;
          },
          extent: d3.extent,
          within: function (d, extent, dim) {
            return (
              extent[0] <= dim.scale(d) && dim.scale(d) <= extent[1]
              // d3.scaleLinear().range([0, innerHeight])
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
      // console.log(xscale)

      // Creates axis ticks at powers of 10
      function log10tick(x) {
        // console.log(typeof x,x,Math.log10(x).toFixed(3) % 1==0)
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
      // console.log( margin.top)
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
      // console.log(data)

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

          // 对数比例尺，最小值>0
          dim.domain = [
            data_domain[0] > 1 ? 1 : data_domain[0],
            data_domain[1],
          ];
        }
        if (!("scale" in dim)) {
          // use type's default scale for dimension
          dim.scale = dim.type.defaultScale.copy();
        }
        // console.log("domain", dim.domain[0]===null);
        dim.scale.domain(dim.domain);
        // var scaleDomain = dim.scale.domain();
        // console.log('s',scaleDomain)
        // console.log(dim.scale);
        // console.log("###", dim.scale(Number(0.1)));
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
          // console.log("d i", d, i);
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
        // console.log(
        //   "sc",
        //   d3
        //     .scaleLog()
        //     .range([innerHeight, 0])
        //     .ticks(3)
        //     .concat(d3.scaleLog().range([innerHeight, 0]).domain())
        // );
        // console.log(
        //   "dom",
        //   dimensions[2].scale.ticks(3).concat(dimensions[2].scale.domain())
        // );
        // console.log("ds", dimensions[0].scale);
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
          // console.log('d p',d,p, p.scale,Number(d[p.key]))
          // console.log('---')
          // console.log(d[p.key],[xscale(i), p.scale(Number(d[p.key]))])
          // check if data element has property and contains a value
          // I am remocing this check because of the null values in the data
          // For some reason, javascript is converting 0 to null in the object
          // if (!(p.key in d) || d[p.key] === null) return null;

          // if (!(p.key in d) || d[p.key] === null) {
          //   console.log("null");
          //   return [xscale(i), p.scale(Number(1))];
          // }
          // console.log(d[p.key],p.scale(Number(d[p.key])))
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

      function brushstart(event) {
        // console.log(event)
        // d3.event.sourceEvent.stopPropagation();
        event.sourceEvent.stopPropagation();
      }

      // Handles a brush event, toggling the display of foreground lines.
      function brush() {
        // console.log("---brush");

        render.invalidate();

        var actives = [];
        svg
          .selectAll(".axis .brush")
          .filter(function (d) {
            // if (d3.brushSelection(this) != null) {
            //   console.log("d", d);
            //   console.log(d3.brushSelection(this));
            // }
            return d3.brushSelection(this);
          })
          .each(function (d) {
            actives.push({
              dimension: d,
              extent: d3.brushSelection(this),
            });
          });
          // console.log(actives)

        var selected = data.filter(function (d) {
          if (
            actives.every(function (active) {
              var dim = active.dimension;
              // test if point is within extents for each active brush
              // console.log(dim.type.within(d[dim.key], active.extent, dim))
              return dim.type.within(d[dim.key], active.extent, dim);
            })
          ) {
            return true;
          }
        });

        // show ticks for active brush dimensions
        // and filter ticks to only those within brush extents

        // svg
        //   .selectAll(".axis")
        //   .filter(function (d) {
        //     return actives.indexOf(d) > -1 ? true : false;
        //   })
        //   .classed("active", true)
        //   .each(function (dimension, i) {
        //     var extent = extents[i];
        //     d3.select(this)
        //       .selectAll(".tick text")
        //       .style("display", function (d) {
        //         var value = dimension.type.coerce(d);
        //         return dimension.type.within(value, extent, dimension)
        //           ? null
        //           : "none";
        //       });
        //   });

        // reset dimensions without active brushes
        // svg
        //   .selectAll(".axis")
        //   .filter(function (d) {
        //     return actives.indexOf(d) > -1 ? false : true;
        //   })
        //   .classed("active", false)
        //   .selectAll(".tick text")
        //   .style("display", null);

        ctx.clearRect(0, 0, width, height);
        ctx.globalAlpha = d3.min([0.85 / Math.pow(selected.length, 0.3), 1]);
        // console.log("selected", selected);
        // console.log("data", data);
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

<style>
/* DEFAULTS */
svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}

svg text {
  pointer-events: none;
  font-size: 16px;
}

.parcoords {
  display: block;
  position: relative;
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

/* hide axes except main axis */
.hide-axis .tick text,
.hide-axis .tick {
  opacity: 0;
}

.foreground path {
  fill: none;
  stroke: steelblue;
}
</style>
