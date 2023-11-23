<template>
  <v-container grid-list-md fluid class="mt-0" pt-8>
    <v-layout row wrap>
      <v-flex v-for="product in products" :key="product.productId" xs12 lg4 sm6>
        <product :product="product" :key="product.productId" />
      </v-flex>
      <v-flex v-if="products.length === 0 && !loading">
        <v-icon style="color: var(--amazonOrange)" x-large>mdi-book</v-icon
        ><strong style="vertical-align: middle"> No products available! </strong>
      </v-flex>
      <v-flex v-if="loading">
        <v-icon style="color: var(--amazonOrange)" x-large>mdi-progress-helper</v-icon
        ><strong style="vertical-align: middle"> Loading ... </strong>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  computed: {
    products() {
      return this.$store.state.products || [];
    },
    loading() {
      return this.$store.state.loading;
    },
  },
  created() {
    this.$store.dispatch("fetchProducts");
  },
};
</script>
