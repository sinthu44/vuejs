<template class="cam-id">
  <v-form ref="form">
    <v-layout wrap align-center row style="min-height:114px;">
      <v-flex xs12 sm8 md8>
        <v-select
          hide-details
          :items="cameras"
          item-text="name"
          item-value="id"
          v-model="camId"
          label="Select camera"
          solo
        ></v-select>
      </v-flex>
      <v-flex xs12 sm3 offset-sm1 md3 offset-md1>
        <v-btn
          large
          block
          :disabled="disabled"
          color="primary"
          @click="loader = 'loading'"
          @click.native="onLoad"
        >
          Load
          <v-icon right v-if="loading">fa fa-spinner fa-pulse</v-icon>
        </v-btn>
      </v-flex>
      <v-flex xs12 sm12>
        <v-alert
          v-if="showAlert"
          :value="true"
          color="error"
          icon="warning"
          outline
        > Please select camera</v-alert>
      </v-flex>
    </v-layout>
  </v-form>
</template>
<script>
import { mapGetters, mapActions } from "vuex";
import { LOADING, DISABLED } from "@/constants/type";
import { bus } from "../main";

export default {
  name: "Cameras",
  props: {
    fetchFrames: {
      type: Function,
      required: true
    },
    camIdCurrent: {
      required: true
    },
    cameras: {
      type: Array,
      required: true,
    },
    resetFrames: Function,
  },
  data() {
    return {
      camId: null,
      showAlert: false,
      loading: LOADING.NO,
      disabled: DISABLED.NO
    };
  },
  watch: {
    camId(val) {
      if (val && this.camIdCurrent && val == this.camIdCurrent) {
        this.disabled = DISABLED.YES;
      } else {
        this.disabled = DISABLED.NO;
      }
    }
  },
  methods: {
    async onLoad() {
      const camId = this.camId;

      if (camId) {
        this.resetFrames && this.resetFrames();
        this.loading = LOADING.YES;
        this.disabled = DISABLED.YES;
        const payload = {
          camId,
        };

        await this.fetchFrames(payload).finally(() => {
          this.loading = LOADING.NO;
        });
        this.showAlert = false;
      } else {
        this.showAlert = true;
      }
    },
    resetData() {
      this.$refs.form.reset();
      Object.assign(this.$data, this.$options.data.call(this));
    },
    destroyed() {
      this.resetFrames && this.resetFrames();
    },
  },
};
</script>