<template>
  <Spin size="large" :spinning="loadingMaster" tip="Loading..." wrapperClassName="custom-spin">
    <MenuTop />
    <Duration
      :stateData="stateData"
      :fetchState="fetchState"
      :startRecording="startRecording"
      :stopRecording="stopRecording"
      :loadingStart="loadingStart"
      :setLoadingStart="setLoadingStart"
    />
    <div class="none-event" :disabled="loadingStart">
      <v-layout 
        wrap
        justify-center
        row
        mx-5
        mb-3
        v-if="disabledDebug()"
        align-center
        class="card p-16"
      >
        <v-flex md4 mb-4>
          <Cameras 
            :fetchFrames="fetchFrames" 
            :camIdCurrent="frames.camId" 
            :cameras="cameras"
            :resetFrames="resetFrames"
          />
        </v-flex>
        <v-flex md7 offset-md1>
          <ReIdCams :cameras="cameras"/>
        </v-flex>
        <v-flex md12 xs12>
          <FramesToVideo 
            :frames="frames.frames"
            :fps="frames.fps"
          />
        </v-flex>
      </v-layout>
    </div>
  </Spin>
</template>
<script>
import MenuTop from "@/components/MenuTop";
import FramesToVideo from "@/components/FramesToVideo";
import Duration from "@/components/Duration"
import Cameras from "@/components/Cameras";
import ReIdCams from "@/components/ReIdCams";
import { STATUS } from "@/constants/type";
import { mapGetters, mapActions } from "vuex";
import { Spin } from 'ant-design-vue'

export default {
  name: "HomePage",
  components: {
    MenuTop,
    FramesToVideo,
    Cameras,
    Duration,
    ReIdCams,
    Spin
  },
  data() {
    return {
      numtop: null
    };
  },
  watch: {
    "stateData.status" (val) {
      if (val === STATUS.READY_VIEWING) {
        this.fetchCameras();
      }
    }
  },
  computed: {
    ...mapGetters({
      stateData: "duration/stateData",
      loadingStart: "duration/loadingStart",
      cameras: "cameras/cameras",
      frames: "frames/frames",
      loadingMaster: "loadingMaster/loadingMaster",
    })
  },
  methods: {
    ...mapActions({
      fetchState: "duration/fetchState",
      startRecording: "duration/startRecording",
      stopRecording: "duration/stopRecording",
      setLoadingStart: "duration/setLoadingStart",
      fetchCameras: "cameras/fetchCameras",
      fetchFrames: "frames/fetchFrames",
      resetFrames: "frames/resetFrames",
    }),
    resetData() {
      Object.assign(this.$data, this.$options.data.call(this));
    },
    disabledDebug() {
      if (this.stateData.status === STATUS.READY_VIEWING) {
        return true;
      } else {
        return false;
      }
    },
  },
};
</script>