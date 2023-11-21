<template>
  <div class="items">
    <v-list-item>
      <v-icon>mdi-cart</v-icon>
      <v-list-item-content>
        <v-list-item-title class="accent--text font-weight-bold">SHOPPING CART</v-list-item-title>
      </v-list-item-content>
    </v-list-item>

    <v-divider></v-divider>

    <v-list dense>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>Cart functionality not available.</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </div>
</template>

<script>
export default {
  name: "cart-drawer",
};
</script>

<style>
.header {
  font-weight: bold !important;
  font-size: 30px !important;
  text-decoration: none;
}
</style>
