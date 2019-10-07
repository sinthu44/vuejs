<template>
  <v-content>
    <v-toolbar class="main-color" fixed dark app>
      <v-toolbar-title class="ml-0 pl-2"></v-toolbar-title>
      DEBUG VIDEO SERVER
      <v-spacer></v-spacer>
      <v-btn icon @click="handleFullScreen()">
        <v-icon>fullscreen</v-icon>
      </v-btn>
    </v-toolbar>
  </v-content>
</template>
<script>
import Util from "@/util";
export default {
  name: "MenuTop",
  data: () => ({}),
  computed: {},
  methods: {
    handleFullScreen() {
      Util.toggleFullScreen();
    }
  }
};
</script>

<style>
.v-toolbar__content {
  height: 60px !important;
}
</style>