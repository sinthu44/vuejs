<template class="list-trackId-id">
  <div>
    <label class="font-weight-black d-flex">List TrackIDs</label>
    <carousel
      class="carousel mt-3 mb-4"
      :dots="false"
      :loop="false"
      :responsive="{0:{items:3},600:{items:3},1200:{items:5},1600:{items:7}}"
      :margin="20"
      :nav="false"
      v-if="carouselListTrackRender"
    >
      <div
        class="item"
        v-for="trackID in listTrack"
        :key="trackID.id"
        @click.prevent="clicktrackId(trackID.id)"
      >
        <div class="frame-person" :class="{active:trackId==trackID.id}">
          <img :src="`${trackID.url}`" alt="error">
          <p class="pt-3 mb-2">{{trackID.label}}</p>
        </div>
      </div>

      <template slot="prev" class="prev">
        <i class="material-icons">chevron_left</i>
      </template>
      <template slot="next" class="next">
        <i class="material-icons" :class="{ 'visibility-hidden': listTrack.length<7 }">chevron_right</i>
      </template>
    </carousel>
    <div class="list-frame">
      <label class="font-weight-black d-flex" :class="{ 'visibility-hidden': trackId=='' || !showListObjects }">List Objects</label>
      <carousel
        class="carousel mt-3"
        :dots="false"
        :loop="false"
        :responsive="{0:{items:3},600:{items:3},1200:{items:6}}"
        :margin="10"
        :nav="false"
        :class="{ 'visibility-hidden': trackId=='' || !showListObjects }"
        v-if="carouselRender"
      >
        <div
          class="item"
          v-for="item in Objects"
          :key="item.id"
        >
          <img :src="`${item.url}`" alt="error" :id="item.id" @mouseover="mouseOver(item.id, item.frame_url)"
          @mouseout="mouseOut()"/>
        </div>

        <template slot="prev" class="prev">
          <i class="material-icons">chevron_left</i>
        </template>
        <template slot="next" class="next">
          <i class="material-icons" :class="{ 'visibility-hidden': Objects.length<6 }">chevron_right</i>
        </template>
      </carousel>
      <div :id="trackId" :class="{'d-none':(objectId==null)}">
        <Object :link="link" :trackId="trackId" :objectId="objectId" />
      </div>
    </div>

    <div class="vh-80" />
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import carousel from "vue-owl-carousel";
import Object from "./Object";
export default {
  components: { carousel, Object },
  props: {
    listTrack: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      trackId: "", //trackId id click
      objectId: null,
      link: "",
      carouselRender: true,
      carouselListTrackRender: true,
      showListObjects:false,
    };
  },
  watch: {
    listTrack(v){
      this.showListObjects=false;
      this.carouselListTrackRender=false;
      this.$nextTick().then(() => {
        this.carouselListTrackRender = true;
      });
    }
  },
  computed: {
    ...mapGetters({
      Objects: "objects/Objects",
      numTop: "reIdCam/numTop",
      listChips: "reIdCam/listChips",
      camId: "images/camId",
    })
  },
  methods: {
    ...mapActions({
      fetchObjects: "objects/fetchObjects",
    }),
    clicktrackId(id) {
      if (+this.numTop > 0 && +this.numTop%1==0 && this.trackId != id && this.listChips.length>0) {
        this.showListObjects=true;
        this.trackId = id;
        this.carouselRender = false;
        const frameID = this.listTrack[0].id;
        this.fetchObjects(1,1,this.trackId,null,null).then(() => {
          this.$nextTick().then(() => {
            this.carouselRender = true;
          });
        });
      }
    },
    mouseOver: function(id, img) {
      this.objectId = id; //id object list trackId id
      this.link = img;
    },
    mouseOut() {
      this.objectId = null;
      this.link = "";
    },
    resetData() {
      Object.assign(this.$data, this.$options.data.call(this));
    }
  },
  created() {
    this.carouselRender = false;
  }
};
</script>
