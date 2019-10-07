<template>
  <v-form 
    ref="form"
    v-model="valid"
    lazy-validation
    @submit.prevent
  >
  <v-layout wrap row align-center pb-4>
    <v-flex md3 sm3 xs12 mb-1 d-flex align-center class="label-and-input">
      <span class="style-span-in-input">Top num :</span>
      <v-text-field
        label="Num"
        solo
        :rules="[isInteger, requiredNumTop, minNumTop]"
        type="number"
        min="0"
        v-model.number="numTopTxt"
        @keyup="changeNumTop"
      ></v-text-field>
    </v-flex>
    <v-flex md9 sm9 xs12 class="label-and-input pl-sm-3" d-flex align-center>
      <span class="style-span-in-input">ReID Cam :</span>
      <v-select
        v-model="reIdCams"
        :items="cameras"
        item-text="name"
        item-value="id"
        label="ReID Cam"
        clearable
        multiple
        solo
        small-reIdCams
        @change="changeCamera"
        v-if="updateCombobox"
        :rules="[requiredChips]"
        color="#009688"
        item-color="#009688"
      >
        <v-list-tile
          slot="prepend-item"
          ripple
          @click="toggle"
        >
          <v-list-tile-action>
            <v-icon :class="reIdCams.length > 0 ? 'color' : ''">{{ showIcon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Select all cams</v-list-tile-title>
        </v-list-tile>
        <template v-slot:selection="{attrs, item, index, select, selected}">
          <v-chip
            v-bind="attrs"
            :input-value="selected"
            close
            @input="remove(item)"
            v-if="index === 0"
          >
            <strong>{{item.name}}</strong>
          </v-chip>
          <span
          v-if="index === 1"
          class="grey--text caption"
        >(+{{ reIdCams.length - 1 }} others)</span>
        </template>
      </v-select>
    </v-flex>
  </v-layout>
  </v-form>
</template>
<script>
import { mapGetters, mapActions } from "vuex";

export default {
  name: "ReIdCam",
  data() {
    return {
      valid: true,
      reIdCams: [],
      hidden: false,
      updateCombobox: true,
      numTopTxt: ""
    };
  },
  props: {
    cameras: {
      type: Array,
      required: true,
    }
  },
  watch: {
    cameras() {
      this.reIdCams = [...this.cameras];
      this.setReIdCams(this.reIdCams.map(m=>m.id).sort((a, b) => a - b));
    },
    valid(v) {
      this.setValidValidate(v);
    }
  },
  computed: {
    ...mapGetters({
      numTop: "reIdCams/numTop",
    }),
    likesAllFruit () {
      return this.reIdCams.length === this.cameras.length;
    },
    likesSomeFruit () {
      return this.reIdCams.length > 0 && !this.likesAllFruit;
    },
    showIcon () {
      if (this.likesAllFruit) return 'close'
      if (this.likesSomeFruit) return 'remove'
      return 'check_box_outline_blank'
    },
    requiredNumTop() {
      if(!this.numTopTxt) {
        return "Top num is required.";
      } else {
        return true;
      }
    },
    minNumTop() {
      if(this.numTopTxt <= 0) {
        return "Num top greater than 0.";
      } else {
        return true;
      }
    },
    requiredChips() {
      if (this.reIdCams.length==0) {
        return "ReIDCam is required.";
      } else {
        return true;
      }
    },
    isInteger() {
      if (this.numTopTxt%1 != 0) {
        return "Top num is integer.";
      } else {
        return true;
      }
    },
  },
  methods: {
    ...mapActions({
      setNumTop: "reIdCams/setNumTop",
      setReIdCams: "reIdCams/setReIdCams",
      setValidValidate: "reIdCams/setValidValidate"
    }),
    toggle () {
      this.$nextTick(() => {
        if (this.likesAllFruit) {
          this.reIdCams = [];
        } else {
          this.reIdCams = this.cameras.slice();
        }
        this.setReIdCams(this.reIdCams.map(m=>m.id).sort((a, b) => a - b));
      })
    },
    changeCamera(id){
      this.reIdCams=id;
      this.setReIdCams(id.sort((a, b) => a - b));
    },
    remove(item){
      this.reIdCams.splice(this.reIdCams.indexOf(item),1);
      this.reIdCams=[...this.reIdCams];
      this.setReIdCams(this.reIdCams.map(m=>m.id).sort((a, b) => a - b));
    },
    changeNumTop() {
      this.setNumTop(event.target.value);
    }
  },
  created() {
    this.setReIdCams(this.cameras);
    this.numTopTxt= this.numTop;
  },
};
</script>