<template>
  <div>
    <div class="container" v-html="text_html"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "LogAnalysisView",
  mounted() {
    console.log(this.$route.query.select);
    fetch("/api/analysis", {
      method: "post",
      mode: "cors",
      cache: "no-cache",
      credentials: "same-origin",
      body: JSON.stringify({
        path: this.$route.query.select,
        width: this.getCharacterWidth(),
      }),
      headers: new Headers({
        "Content-Type": "application/json",
      }),
      redirect: "follow",
    }) //.then()为异步方法，保证前面执行完后再开始，可以避免数据没有获取到
      .then((v) => {
        console.log(v);
        return v.json();
      })
      .then((v) => {
        console.log(v);
        v = v.replace("body {", "tbody {");
        v = v.replace(
          "td, p, li, th {",
          "tbody td, tbody p, tbody li, tbody th {"
        );

        this.text_html = v;
      });
  },
  watch: {
    "$route.query.select"(newSelect) {
      fetch("/api/analysis", {
        method: "post",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        body: JSON.stringify({
          path: this.$route.query.select,
          width: this.getCharacterWidth(),
        }),
        headers: new Headers({
          "Content-Type": "application/json",
        }),
        redirect: "follow",
      }) //.then()为异步方法，保证前面执行完后再开始，可以避免数据没有获取到
        .then((v) => {
          return v.json();
        })
        .then((v) => {
          v = v.replace("body {", "tbody {");
          v = v.replace(
            "td, p, li, th {",
            "tbody td, tbody p, tbody li, tbody th {"
          );

          this.text_html = v;
        });
    },
  },
  data() {
    return {
      width: document.body.clientWidth,
      placeholderText: "A", // 用于计算字符宽度的占位文本，确保与实际文本的样式相似
      text_html: "",
    };
  },
  created() {
    window.addEventListener("resize", this.WindowResize);
  },
  beforeDestroy: function () {
    window.removeEventListener("resize", this.WindowResize);
  },
  methods: {
    analysis() {
      fetch("/api/analysis", {
        method: "post",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        body: JSON.stringify({
          width: this.getCharacterWidth(),
        }),
        headers: new Headers({
          "Content-Type": "application/json",
        }),
        redirect: "follow",
      }) //.then()为异步方法，保证前面执行完后再开始，可以避免数据没有获取到
        .then((v) => {
          console.log(v);
          return v.json();
        })
        .then((v) => {
          v = v.replace("body {", "tbody {");
          v = v.replace(
            "td, p, li, th {",
            "tbody td, tbody p, tbody li, tbody th {"
          );

          this.text_html = v;
        });
    },
    getCharacterWidth() {
      // 创建一个隐藏的span元素，用于计算字符宽度
      const span = document.createElement("span");
      span.textContent = this.placeholderText;

      // 设置span元素样式（确保与实际文本相同的样式）
      span.style.visibility = "hidden";

      // 将span元素添加到body中
      document.body.appendChild(span);
      // 获取span元素的宽度
      const characterWidth = span.offsetWidth;

      // 从body中移除span元素
      document.body.removeChild(span);

      // 计算一行能容纳的字符数
      const characters = Math.floor(this.width / characterWidth);

      return characters;
    },
    WindowResize(event) {
      this.width = document.body.clientWidth;
      console.log(this.width);
    },
  },
});
</script>

<style scope>
@media (min-width: 1024px) {
  .container {
    min-height: 100%;
  }
}
</style>
