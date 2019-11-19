<template>
  <div>
    <div v-if="checkNoRecord()">
      <h1 class="align-center">
        There is no camera to debug
      </h1>
    </div>
    <v-container fluid grid-list-xl px-5 v-else>
      <v-form 
        ref="form"
        v-model="valid"
        lazy-validation
        @submit.prevent
      >
        <v-layout wrap align-center row justify-center class="duration">
          <v-flex>
            <div class="px-3" style="background: rgb(241, 241, 241);">
              <v-layout wrap row>
                <v-flex xs12 md12 lg8 class="style-duration">
                  <v-layout wrap row>
                    <v-flex xs12 md6 lg6 pb-0>
                      <div class="d-flex-custom align-center mt-1">
                        <span class="mr-1 style-span-in-input">Duration :</span>
                        <v-text-field
                          style="width:calc( 100% - 124px)"
                          label="Minute"
                          solo
                          type="number"
                          min="0"
                          max="3600"
                          :error-messages="durationErrors"
                          @input="$v.duration.$touch()"
                          @blur="$v.duration.$touch()"
                          v-model="duration"
                          :disabled="checkDisabled('START')"
                          @keypress.enter="clickStart()"
                        ></v-text-field>
                        <span class="ml-2 style-span-in-input">min</span>
                      </div>
                    </v-flex>
                    <v-flex xs6 md3 lg2 pb-0>
                      <v-btn
                        large
                        block
                        :disabled="checkDisabled('START') || !valid || duration <= 0"
                        color="primary"
                        @click="clickStart()"
                      >Start<v-icon right dark v-if="this.loadingStart">fa fa-spinner fa-pulse</v-icon></v-btn>
                    </v-flex>
                    <v-flex xs6 md3 lg2 pb-0>
                      <v-btn
                        large
                        block
                        :disabled="checkDisabled('STOP')"
                        color="error"
                        @click.native="dialog=true"
                      >Stop<v-icon right dark v-if="this.loadingStop">fa fa-spinner fa-pulse</v-icon></v-btn>
                    </v-flex>
                    <v-flex
                      xs12
                      d-flex
                      justify-center
                      pt-0
                      class="letter-spacing"
                    >
                      <span class="align-center" v-if="showRecording()">
                        <v-icon right small>fa fa-spinner fa-pulse</v-icon>
                        ... get {{Math.floor(stateData.recording_time/60)}} minutes {{Math.floor(stateData.recording_time%60)}} seconds stream
                      </span>
                    </v-flex>
                  </v-layout>
                </v-flex>
              </v-layout>
            </div>
          </v-flex>
        </v-layout>
      </v-form>
      <v-dialog v-model="dialog" max-width="290">
        <v-card>
          <v-card-text>Are you sure you want to stop ?</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="dialog = false">Cancel</v-btn>
            <v-btn color="primary" @click.prevent="clickStop">Yes</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { STATUS, LOADING } from "@/constants/type";
import { between, required } from 'vuelidate/lib/validators'
import { validationMixin } from 'vuelidate'

export default {
  data() {
    return {
      valid: true,
      duration: null,
      dialog:false,
      interval: null,
      timeInterVal: 5000,
      loadingStart: LOADING.NO,
      loadingStop: LOADING.NO,
    };
  },
  mixins: [validationMixin],
  validations: {
    duration: {
      between: between(1, 60),
      required,
    },
  },
  computed: {
    durationErrors () {
      const errors = [];
      if (!this.$v.duration.$dirty) {
        return errors;
      }

      !this.$v.duration.between && errors.push(`Must be between ${this.$v.duration.$params.between.min} and ${this.$v.duration.$params.between.max}`);
      !this.$v.duration.required && errors.push('Duration is required');

      return errors;
    }
  },
  props: {
    stateData: {
      type: Object,
      required: true
    },
    fetchState: {
      type: Function,
      required: true
    },
    startRecording: {
      type: Function,
      required: true
    },
    stopRecording: {
      type: Function,
      required: true
    },
  },
  watch: {
    'stateData.status' (val) {
      if(val == STATUS.RECORDING) {
        this.duration = this.stateData.duration;

        this.interval = setInterval(() => {
          this.fetchState();
        }, this.timeInterVal);
      } else {
        this.resetData();
      }
    },
  },
  methods: {
    resetData() {
      this.$v.$reset()
      clearInterval(this.interval);
      Object.assign(this.$data, this.$options.data.call(this));
    },
    async clickStart() {
      await this.$v.$touch();

      if (!this.valid) {
        return;
      }

      const seft = this;
      const payload = {
        duration: this.duration,
      };

      this.loadingStart = LOADING.YES;

      this.startRecording(payload).then(() => {
        seft.getState();
      }).finally(() => {
        seft.loadingStart = LOADING.NO;
      });
    },
    clickStop() {
      this.dialog = false;

      const seft = this;
      this.loadingStop = LOADING.YES;

      this.stopRecording().then(() => {
        seft.getState()
      }).finally(() => {
        this.loadingStop = LOADING.NO;
      });
    },
    getState() {
      this.fetchState();
    },
    checkDisabled(type='START') {
      if (this.stateData.status === STATUS.NO_RECORD) {
       return true;
      } else {
        if (type == 'START') {
          return this.stateData.status === STATUS.RECORDING || this.loadingStart;
        } else if (type == 'STOP') {
          return this.stateData.status !== STATUS.RECORDING || this.loadingStop;
        }
      }

      return true;
    },
    showRecording()
    {
      return this.stateData.status === STATUS.RECORDING 
    },
    checkNoRecord() {
      return this.stateData.status == STATUS.NO_RECORD;
    },
  },
  created() {
    this.getState()
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
};
</script>

