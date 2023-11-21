<template>
  <v-btn fixed right rounded small text icon x-large @click.stop="toggleDrawer">
    <v-icon color="black" x-large>mdi-cart</v-icon>
  </v-btn>
</template>

<script>
export default {
  name: "cart-button",
  methods: {
    toggleDrawer() {
      this.$emit("drawerChange");
    },
  },
};
</script>
