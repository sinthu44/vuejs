<template>
  <div>
    <MenuTop />
    <Duration
      :stateData="stateData"
      :fetchState="fetchState"
      :startRecording="startRecording"
      :stopRecording="stopRecording"
    />
    <v-layout wrap justify-center row mx-5 mb-3 v-if="disabledDebug()" align-center>
      <v-flex md4 mb-4>
        <Cameras 
        :fetchFrames="fetchFrames" 
        :camIdCurrent="frames.camId" 
        :cameras="cameras"
        :resetFrames="resetFrames"
      />
      </v-flex>
      <v-flex md7 offset-md1>
        <ReIdCam :cameras="cameras"/>
      </v-flex>
      <v-flex md12 xs12>
        <FramesToVideo 
          :frames="frames.frames"
          :fps="frames.fps"
        />
      </v-flex>
    </v-layout>
  </div>
</template>
<script>
import MenuTop from "@/components/MenuTop";
import FramesToVideo from "@/components/FramesToVideo";
import Duration from "@/components/Duration"
import Cameras from "@/components/Cameras";
import ReIdCam from "@/components/ReIdCam";
import { STATUS } from "@/constants/type";
import { mapGetters, mapActions } from "vuex";
import { bus } from "../main";

export default {
  name: "HomePage",
  components: {
    MenuTop,
    FramesToVideo,
    Cameras,
    Duration,
    ReIdCam
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
      cameras: "cameras/cameras",
      frames: "frames/frames",
    })
  },
  methods: {
    ...mapActions({
      fetchState: "duration/fetchState",
      startRecording: "duration/startRecording",
      stopRecording: "duration/stopRecording",
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
  created() {
    bus.$on("someEventReset", obj => this.resetData());
  }
};
</script>
<style scoped>
</style>