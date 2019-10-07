<template class="list-objects">
  <div class="list-frame" v-if="showObjects">
    <label class="font-weight-black d-flex">Object List</label>
    <carousel
      class="carousel mt-3"
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
      :margin="15"
      :nav="false"
      :touchDrag="false"
      :mouseDrag="false"
      v-if="objects.length > 0"
    >
      <div
        class="item cursor-pointer"
        v-for="item in objects"
        :key="item.id"
      >
        <img 
          class="frame-person image-carousel"
          :class="{active: object && object.id == item.id}"
          :src="item.url"
          alt="error"
          :id="item.id"
          @click="onClick(item)"
        />
      </div>

      <template slot="prev" class="prev">
        <i class="material-icons">chevron_left</i>
      </template>
      <template slot="next" class="next">
        <i class="material-icons" :class="{ 'visibility-hidden': objects.length < 8 }">chevron_right</i>
      </template>
    </carousel>
    <div class="mt-15 align-left" v-else>
      Objects Are Empty
    </div>
    <div v-if="object">
      <v-container fluid grid-list-xl>
        <v-layout wrap align-center row>
          <h2 class="my-2 ma-auto" style="font-weight: 400;">Frame</h2>
          <div id="img-frame" v-if="object">
            <img :src="object.frame_url" alt="error" />
          </div>
          <h3
            class="mt-2 ma-auto"
            style="font-weight: 400;"
          >{{ object.name }}</h3>
        </v-layout>
      </v-container>
    </div>
  </div>
</template>
<script>
import carousel from "vue-owl-carousel";

export default {
  components: { carousel },
  data() {
    return {
      object: null,
    }
  },
  props: {
    objects: {
      type: Array,
      required: true
    },
    showObjects: {
      type: Boolean,
      default: false
    }
  },
  watch: {
    showObjects(v) {
      if (v == false) {
        this.resetData();
      }
    }
  },
  methods: {
    onClick(object) {
      this.object = object;
    },
    resetData() {
      Object.assign(this.$data, this.$options.data.call(this));
    }
  }
}

</script>