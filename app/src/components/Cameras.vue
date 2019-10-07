<template class="cam-id">
  <v-form 
    ref="form" 
    @submit.prevent
    v-model="valid"
    lazy-validation
  >
    <v-layout wrap align-start row >
      <v-flex xs12 sm8 md8 pb-0>
        <v-select
          :items="cameras"
          item-text="name"
          item-value="id"
          v-model="camId"
          label="Select camera"
          solo
          :error-messages="camIdErrors"
          @input="$v.camId.$touch()"
          @blur="$v.camId.$touch()"
        ></v-select>
      </v-flex>
      <v-flex xs12 sm3 offset-sm1 md3 offset-md1>
        <v-btn
          large
          block
          :disabled="disabled"
          @click="loader = 'loading'"
          @click.native="onLoad"
          class="my-1 main-color color-white"
        >
          Load
          <v-icon right v-if="loading">fa fa-spinner fa-pulse</v-icon>
        </v-btn>
      </v-flex>
    </v-layout>
  </v-form>
</template>
<script>
import { LOADING, DISABLED } from "@/constants/type";
import { required } from 'vuelidate/lib/validators'
import { validationMixin } from 'vuelidate'

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
      valid: true,
      camId: null,
      loading: LOADING.NO,
      disabled: DISABLED.NO
    };
  },
  mixins: [validationMixin],
  validations: {
    camId: {
      required,
    },
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
  computed: {
    camIdErrors () {
      const errors = [];
      if (!this.$v.camId.$dirty) {
        return errors;
      }
      
      !this.$v.camId.required && errors.push('Camera is required');

      return errors;
    },
  },
  methods: {
    async onLoad() {
      await this.$v.$touch();

      if (!this.valid) {
        return;
      }

      const camId = this.camId;

      this.resetFrames && this.resetFrames();
      this.loading = LOADING.YES;
      this.disabled = DISABLED.YES;
      const payload = {
        camId,
      };

        await this.fetchFrames(payload).catch(() => {
          this.disabled = DISABLED.NO;
        }).finally(() => {
          this.loading = LOADING.NO;
        });

    },
    resetData() {
      this.$refs.form.reset();
      Object.assign(this.$data, this.$options.data.call(this));
    },
  },
  destroyed () {
    this.resetFrames && this.resetFrames();
  },
};
</script>