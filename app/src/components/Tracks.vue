<template class="list-trackId-id">
  <div class="list-frame noselect">
    <label class="font-weight-black d-flex">TrackID List</label>
    <carousel
      class="carousel mt-3 mb-4"
      :dots="false"
      :loop="false"
      :responsive="{
        0:{items:1},
        450:{items:2},
        560:{items:3},
        680:{items:4},
        815:{items:5},
        960:{items:3},
        1150:{items:4},
        1400:{items:5},
        1600:{items:6},
        1800:{items:7}
      }"
      :margin="20"
      :nav="false"
      :touchDrag="false"
      :mouseDrag="false"
      v-if="carouselListTrackRender"
    >
      <div
      v-for="item in tracks"
        class="none-event cursor-pointer item"
        :key="item.id"
        @click.prevent="clickTrack(item.id)"
        :disabled="disabledTrack()"
      >
        <Tooltip :title="item.label">
          <img
            class="frame-person image-carousel"
            :class="{active:trackId==item.id}"
            :src="item.url"
            alt="error"
          >
        </Tooltip>
      </div>
      <template slot="prev" class="prev">
        <i class="material-icons">chevron_left</i>
      </template>
      <template slot="next" class="next">
        <i class="material-icons" :class="{ 'visibility-hidden': tracks.length<8 }">chevron_right</i>
      </template>
    </carousel>
    <Objects 
      :showObjects="showObjects"
      :objects="objects"
    />
    <div class="vh-80" />
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import Objects from "./Objects";
import { LOADING } from "@/constants/type";
import carousel from "vue-owl-carousel";
import { Spin, Tooltip } from 'ant-design-vue'

export default {
  components: { carousel, Objects, Spin, Tooltip },
  props: {
    tracks: {
      type: Array,
      required: true
    },
    frameId: Number,
  },
  data() {
    return {
      trackId: null,
      showObjects: false,
      carouselListTrackRender: true,
    };
  },
  watch: {
    tracks() {
      this.carouselListTrackRender=false;
      this.$nextTick().then(() => {
        this.resetData();
      });

    }
  },
  computed: {
    ...mapGetters({
      objects: "objects/objects",
      frames: "frames/frames",
      numTop: "reIdCams/numTop",
      reIdCams: "reIdCams/reIdCams",
      validValidate: "reIdCams/validValidate",
    }),
  },
  methods: {
    ...mapActions({
      fetchObjects: "objects/fetchObjects",
      resetObjects: "objects/resetObjects",
      setLoadingMaster: "loadingMaster/setLoadingMaster",
    }),
    clickTrack(trackIdCurrent) {
      this.resetObjects();
      this.setLoadingMaster(LOADING.YES);
      this.trackId = trackIdCurrent;
      this.showObjects = false;
      const payload = {
        topNum: this.numTop,
        reIdCams: this.reIdCams,
        camId: this.frames.camId,
        frameId: this.frameId,
        trackId: this.trackId
      };

      this.fetchObjects(payload)
        .then(() => {
          this.showObjects = true;
        }).catch(() => {
          this.trackId = null;
        }).finally(() => {
          this.setLoadingMaster(LOADING.NO);
        })
    },
    resetData() {
      this.resetObjects();
      this.setLoadingMaster(LOADING.NO);
      Object.assign(this.$data, this.$options.data.call(this));
    },
    disabledTrack() {
      return !this.validValidate;
    }
  },
  destroyed() {
    this.resetData();
  }
};
</script>
