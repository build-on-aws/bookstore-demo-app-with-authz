import { getProducts } from "@/backend/api.js";

const fetchProducts = ({ commit }) => {
  getProducts().then((response) => {
    commit("setUpProducts", response.products);
  });
};

export default {
  fetchProducts,
};
