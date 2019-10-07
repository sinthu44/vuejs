<template>
  <v-layout row wrap>
    <template v-if="!disabled">
      <v-flex md4 mb-4>
        <div 
          class="wrapper-frame noselect none-outline"
          :tabindex="checkFrameOutSize('-') && checkFrameOutSize('+') ? '' : '1'" 
          @keypress.enter="onPlay()"
          @keydown="onKeyDown($event)"
        >
          <img 
            class="frame-custom"
            :src="frames.length > 0 ? frames[indexFrame].url : '/static/DxnWF8.gif'" 
            alt 
          />
          <div class="frame-btn">
            <v-icon
              @click="onPrevious()"
              :disabled="checkFrameOutSize('-')"
              color="primary"
              large
            >fast_rewind</v-icon>
            <v-icon
              @click="onPlay()"
              color="primary"
              :disabled="checkFrameOutSize('-') && checkFrameOutSize('+')"
              large
            >
              {{ statusVideo == 'play' ? 'play_circle_filled' : 'pause_circle_filled' }}
            </v-icon>
            <v-icon
              @click="onNext()"
              :disabled="checkFrameOutSize('+')"
              color="primary"
              large
            >fast_forward</v-icon>
          </div>
        </div>
      </v-flex>
    </template>
    <v-flex md7 offset-md1>
      <Tracks
        v-if="showTracks()"
        :tracks="frames[indexFrame].trackIDs"
        :frameId="frames[indexFrame].id"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import Tracks from "@/components/Tracks";
import { DISABLED } from "@/constants/type";
export default {
  name: "FramesToVideo",
  components: {
    Tracks
  },
  props: {
    frames: {
      type: Array,
      required: true
    },
    fps: {
      default: 10,
      type: Number
    },
    disabled: {
      default: DISABLED.NO,
      type: Boolean
    },
    skipFrame: {
      default: 1,
      type: Number
    },
  },
  data() {
    return {
      indexFrame: 0,
      interval: null,
      statusVideo: "play",
      showListTrack: true
    };
  },
  watch: {
    disabled (val, oldVal) {
      if (val !== oldVal) {
        this.resetData();
      }
    },
    frames (val, oldVal) {
      if (JSON.stringify(val) !== JSON.stringify(oldVal)) {
        this.resetData();
      }
    }
  },
  methods: {
    async onKeyDown(e) {
      let keyCode = e.keyCode ? e.keyCode : e.which;
      // case 1: key next
      // case 2: key previous
      if (keyCode == 39 && !this.checkFrameOutSize('+')) {
        await this.onNext();
      } else if(keyCode == 37 && !this.checkFrameOutSize('-')) {
        await this.onPrevious();
      }
    },
    onPlay() {
      if (this.statusVideo == "play") {
        this.playVideo();
      } else {
        this.stopVideo();
      }
    },
    playVideo() {
      if (
        this.checkFrameOutSize("+") ||
        this.checkFrameOutSize("-")
      ) {
        this.indexFrame = 0;
      }

      let self = this;

      this.statusVideo = "stop";
      this.showListTrack = false;

      this.interval = setInterval(function() {
        if (self.checkFrameOutSize("+")) {
          self.stopVideo();
        } else {
          self.indexFrame++;
        }
      }, 1000 / this.fps);
    },
    stopVideo() {
      this.statusVideo = "play";
      this.showListTrack = true;
      clearInterval(this.interval);
    },
    onPrevious() {
      if (this.checkFrameOutSize("-")) {
        return;
      } else {
        // because array start is 0 but length of array start is 1
        let indexFrameNew = this.indexFrame - this.skipFrame;
        if (indexFrameNew <= 0) {
          this.indexFrame = 0;
        } else {
          this.indexFrame -= this.skipFrame;
        }
      }
    },
    onNext() {
      if (this.checkFrameOutSize("+")) {
        return;
      } else {
        // because array start is 0 but length of array start is 1
        let indexFrameNew = this.indexFrame + this.skipFrame + 1;
        if (indexFrameNew >= this.frames.length) {
          this.indexFrame = this.frames.length - 1;
        } else {
          this.indexFrame += this.skipFrame;
        }
      }
    },
    checkFrameOutSize(type) {
      if (type == "+") {
        return this.indexFrame + 1 >= this.frames.length;
      } else if (type == "-") {
        return this.indexFrame <= 0;
      }

      return true;
    },
    showTracks() {
      return this.showListTrack 
        && this.frames[this.indexFrame]
        && this.frames[this.indexFrame].trackIDs.length > 0;
    },
    resetData() {
      clearInterval(this.interval);
      Object.assign(this.$data, this.$options.data.call(this));
    },
  },
};
</script>