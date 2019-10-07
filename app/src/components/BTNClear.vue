<template>
    <v-layout wrap align-center row justify-center>
      <v-flex xs12 sm11 md11 d-flex justify-end>
        <v-flex xs12 sm3 md2>
          <v-btn
            large
            block
            color="primary"
            class="px-3"
            @click.prevent="btnClear"
          >Clear</v-btn>
        </v-flex>
      </v-flex>
    </v-layout>
</template>

<script>
import { mapActions } from 'vuex';
import { bus } from '../main';
export default {
  data() {
    return {};
  },
  computed: {},
  watch: {

  },
  methods: {
    ...mapActions({
      resetImageDefault: "images/resetImageDefault",
    }),
    btnClear(){
      this.resetImageDefault();
      bus.$emit('someEventReset',"click");
    }
  },
  created() {}
};
</script>
