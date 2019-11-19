<template>
  <v-content>
    <v-toolbar color="primary" fixed dark app>
      <v-toolbar-title class="ml-0 pl-2"></v-toolbar-title>
      <v-toolbar-side-icon></v-toolbar-side-icon>DEBUG VIDEO SERVER
      <v-spacer></v-spacer>
      <v-btn icon @click="handleFullScreen()">
        <v-icon>fullscreen</v-icon>
      </v-btn>
    </v-toolbar>
  </v-content>
</template>
<script>
import * as helpers from "../../../helpers";
export default {
  name: "MenuTop",
  data: () => ({}),
  computed: {},
  methods: {
    handleFullScreen() {
      this.$helpers.toggleFullScreen();
    }
  }
};
</script>

<style>
.v-toolbar__content {
  height: 60px !important;
}
</style>