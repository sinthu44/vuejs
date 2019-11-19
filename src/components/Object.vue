<template>
  <v-container fluid grid-list-xl>
    <v-layout wrap align-center row>
      <h2 class="my-2 ma-auto" style="font-weight: 400;">Frame</h2>
      <div id="img-frame" v-if="link!=''">
        <img :src="`${link}`" alt="error" />
      </div>
      <h3
        class="mt-2 ma-auto"
        style="font-weight: 400;"
      >{{trackId}} - {{objectId}} - 2019-08-30 01:01:01</h3>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  props: ["link", "trackId", "objectId"],
  data() {
    return {};
  },
  computed: {},
  watch: {},
  methods: {},
  created() {}
};
</script>

