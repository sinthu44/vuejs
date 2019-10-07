<template>
  <v-form 
    ref="form"
    v-model="valid"
    lazy-validation
    @submit.prevent
  >
  <v-layout wrap row align-center pb-4>
    <v-flex md3 sm3 xs12 mb-1 d-flex align-center class="label-and-input">
      <label class="text-xs-left style-span-in-input">Top num :</label>
      <v-text-field
        label="Num"
        solo
        :error-messages="numTopErrors"
        @input="$v.numTopTxt.$touch()"
        @blur="$v.numTopTxt.$touch()"
        :rules="[checkPointNumTop]"
        type="number"
        min="0"
        v-model="numTopTxt"
        @keyup="changeNumTop"
      ></v-text-field>
    </v-flex>
    <v-flex md9 sm9 xs12 class="label-and-input pl-sm-3" d-flex align-center>
      <label class="style-span-in-input">ReID Cam :</label>
      <v-combobox
        v-model="chips"
        :items="cameras"
        item-text="name"
        item-value="id"
        label="ReID Cam"
        chips
        clearable
        :error-messages="chipsErrors"
        @input="$v.chips.$touch()"
        @blur="$v.chips.$touch()"
        :rules="[lengthChipsErrors]"
        solo
        multiple
        v-on:change="changeReIdCam"
        v-if="updateCombobox"
      >
      <v-list-tile
        slot="prepend-item"
        ripple
        @click="toggle"
        :color="chips.length > 0 ? 'blue darken-4' : ''"
      >
        <v-list-tile-action>
          <v-icon :color="chips.length > 0 ? 'blue darken-4' : ''">{{ icon }}</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Select all cams</v-list-tile-title>
      </v-list-tile>
        <template v-slot:selection="data">
          <v-chip :selected="data.selected" close @input="remove(data.item)">
            <strong>{{ data.item.name }}</strong>&nbsp;
          </v-chip>
        </template>
      </v-combobox>
    </v-flex>
  </v-layout>
  </v-form>
</template>
<script>
import { mapGetters, mapActions } from "vuex";
import { validationMixin } from 'vuelidate';
import { required } from 'vuelidate/lib/validators';
export default {
  name: "ReIdCam",
  data() {
    return {
      valid: true,
      chips: [],
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
  mounted() {
    this.getListChipsSelect(this.cameras);
  },
  watch: {
    cameras(v) {
      this.chips = [...this.cameras];
      this.getListChipsSelect(this.chips);
    },
  },
  mixins: [validationMixin],
  validations: {
    numTopTxt: {
      required,
    },
    chips: {
      required,
    },
  },
  computed: {
    ...mapGetters({
      numTop: "reIdCam/numTop",
    }),
    likesAllFruit () {
      return this.chips.length === this.cameras.length;
    },
    likesSomeFruit () {
      return this.chips.length > 0 && !this.likesAllFruit;
    },
    icon () {
      if (this.likesAllFruit) return 'close'
      if (this.likesSomeFruit) return 'remove'
      return 'check_box_outline_blank'
    },
    numTopErrors() {
      const errors = [];
      if (!this.$v.numTopTxt.$dirty) {
        return errors;
      }
      !this.$v.numTopTxt.required && errors.push('Num top is required');
      return errors;
    },
    chipsErrors() {
      const errors = [];
      if (!this.$v.chips.$dirty) {
        return errors;
      }
      !this.$v.chips.required && errors.push('ReIDCam is required.');
      return errors;
    },
    lengthChipsErrors() {
      if (this.chips.filter(f=>f.id).length==0) {
        return "ReIDCam is required.";
      } else {
        return true;
      }
    },
    checkPointNumTop() {
      if (this.numTopTxt%1 != 0) {
        return "Top num is integer.";
      } else {
        return true;
      }
    },
  },
  methods: {
    ...mapActions({
      getNumTop: "reIdCam/getNumTop",
      getListChipsSelect: "reIdCam/getListChipsSelect",
    }),
    toggle () {
      this.$nextTick(() => {
        if (this.likesAllFruit) {
          this.chips = [];
        } else {
          this.chips = this.cameras.slice();
        }
        this.getListChipsSelect(this.chips.map(m=>m.id).sort((a, b) => a - b));
      })
    },
    changeReIdCam(e) {
      this.chips = e;
      this.getListChipsSelect(this.chips.filter(f=> f.id && f!= undefined).map(m=>m.id).sort((a, b) => a - b));
    },
    remove(item) {
      this.chips.splice(this.chips.indexOf(item), 1);
      this.chips = [...this.chips];
      this.getListChipsSelect(this.chips.map(m=>m.id).sort((a, b) => a - b));
    },
    changeNumTop() {
      this.getNumTop(event.target.value);
    }
  },
  created() {
    this.numTopTxt= this.numTop;
  },
};
</script>