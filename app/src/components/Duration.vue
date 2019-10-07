<template>
  <div>
    <div v-if="checkStateLoading">
      <h1 class="align-center">
        Debug server is loading page
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
            <div class="card px-3">
              <v-layout wrap row>
                <v-flex xs12 md12>
                  <v-layout wrap row>
                    <v-flex xs12 sm12 md8 lg6 pb-0>
                      <v-layout wrap row>
                        <v-flex xs12 sm5 md6 lg7 class="d-flex-custom align-center mt-1">
                          <span class="mr-2 style-span-in-input">Duration :</span>
                          <v-text-field
                            style="width:calc( 100% - 124px)"
                            label="Second"
                            solo
                            type="number"
                            :error-messages="durationErrors"
                            @input="$v.duration.$touch()"
                            @blur="$v.duration.$touch()"
                            v-model.number="duration"
                            :disabled="checkDisabled('START')"
                            @keypress.enter="clickStart()"
                          ></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm7 md6 lg5 mb-3>
                          <v-radio-group
                            v-model="modelVersion"
                            row 
                            :disabled="checkDisabled('START')"
                          >
                            <v-radio label="v1.0" style="padding-right: 40px" value="v1.0" color="#009688"></v-radio>
                            <v-radio label="v1.5" value="v1.5" color="#009688"></v-radio>
                          </v-radio-group>
                        </v-flex>
                      </v-layout>
                    </v-flex>
                    <v-flex xs6 sm6 md2 lg3 pb-0>
                      <v-btn
                        large
                        block
                        :disabled="checkDisabled('START') || !valid || duration <= 0"
                        class="main-color color-white"
                        @click="clickStart()"
                      >
                        Start<v-icon right dark v-if="this.loadingStart">fa fa-spinner fa-pulse</v-icon>
                      </v-btn>
                    </v-flex>
                    <v-flex xs6 sm6 md2 lg3 pb-0>
                      <v-btn
                        large
                        block
                        :disabled="checkDisabled('STOP')"
                        color="error"
                        @click.native="dialog=true"
                      >
                        Stop<v-icon right dark v-if="this.loadingStop">fa fa-spinner fa-pulse</v-icon>
                      </v-btn>
                    </v-flex>
                    <v-flex
                      xs12
                      d-flex
                      justify-center
                      pt-0
                      class="letter-spacing pb-0"
                    >
                      <v-progress-linear
                        v-model="progress"
                        height="20"
                        reactive
                        :indeterminate="progressIndeterminate"
                        color="#009688"
                        class="align-center custom-progress"
                        v-if="!checkStateNoRecord"
                        :query="progressSerializing"
                      >
                        <strong>
                          {{progress}}% {{progressSerializing ? '(Initializing)' : ''}}
                        </strong>
                      </v-progress-linear>
                    </v-flex>
                  </v-layout>
                </v-flex>
              </v-layout>
            </div>
          </v-flex>
        </v-layout>
      </v-form>
      <div class="align-center op-3 mt-100 noselect" v-if="checkStateNoRecord">
        <h2 class="mb-0">No Recorded Data</h2>
        <v-icon large>info</v-icon>
      </div>
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
import { required } from 'vuelidate/lib/validators'
import { validationMixin } from 'vuelidate'

const integer = (value) => {
  if (value%1 == 0) {
    return true;
  } else {
    return false;
  }
}

export default {
  data() {
    return {
      valid: true,
      duration: null,
      dialog:false,
      interval: null,
      timeInterVal: 1500,
      loadingStop: LOADING.NO,
      isStop:false,
      modelVersion: 'v1.0',
    };
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
    setLoadingStart: {
      type: Function,
      required: true
    },
    loadingStart: {
      type: Boolean,
      required: true
    },
  },
  mixins: [validationMixin],
  validations: {
    duration: {
      required,
      integer
    },
  },
  computed: {
    durationErrors () {
      const errors = [];
      if (!this.$v.duration.$dirty) {
        return errors;
      }

      !this.betweenDuration && errors.push(`Duration must be between 10 and ${this.stateData.max_duration}`);
      !this.$v.duration.required && errors.push('Duration is required');
      !this.$v.duration.integer && errors.push('Duration is integer.')

      return errors;
    },
    min_duration () {
      return 10;
    },
    betweenDuration() {
      if (this.duration < this.min_duration || this.duration > this.stateData.max_duration) {
        return false;
      } else {
        return true
      }
    },
    progress() {
      return this.stateData.recording_time >= 100 ? 100 : this.stateData.recording_time;
    },
    progressIndeterminate() {
      return this.checkStateRecording && (this.progress >= 100 || this.progress <= 0)
    },
    progressSerializing() {
      return this.checkStateRecording && this.progress <= 0
    },
    checkStateLoading() {
      return this.stateData.status === STATUS.LOADING_PAGE;
    },
    checkStateNoRecord() {
      return this.stateData.status === STATUS.READY_RECORDING;
    },
    checkStateReadyView() {
      return this.stateData.status === STATUS.READY_VIEWING;
    },
    checkStateRecording() {
      return this.stateData.status === STATUS.RECORDING;
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
      let dataReset = this.$options.data.call(this);
      delete dataReset.modelVersion;
      Object.assign(this.$data, dataReset);
    },
    async clickStart() {
      await this.$v.$touch();

      if (!this.valid) {
        return;
      }

      const payload = {
        duration: this.duration,
        modelVersion: this.modelVersion
      };

      this.setLoadingStart(LOADING.YES)

      this.startRecording(payload).then(() => {
      }).finally(() => {
        this.getState().finally(() => {
          this.setLoadingStart(LOADING.NO)
        });
      });
    },
    clickStop() {
      this.dialog = false;

      this.loadingStop = LOADING.YES;

      this.stopRecording().then(() => {
        this.isStop = true;
      }).finally(() => {
        this.getState().finally(() => {
          this.loadingStop = LOADING.NO;
        });
      });
    },
    async getState() {
      await this.fetchState();
    },
    checkDisabled(type='START') {
      if (this.checkStateLoading) {
       return true;
      } else {
        if (type == 'START') {
          return this.checkStateRecording || this.loadingStart;
        } else if (type == 'STOP') {
          return !this.checkStateRecording || this.isStop || this.loadingStop;
        }
      }

      return true;
    },
  },
  created() {
    this.getState()
  },
  destroyed() {
    this.setLoadingStart(LOADING.NO);
    clearInterval(this.interval);
  },
};
</script>

