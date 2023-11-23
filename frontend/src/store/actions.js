import store from "@/store/store.js";
import { getProducts } from "@/backend/api.js";

const fetchProducts = ({ commit }) => {
  store.commit("startLoading");

  getProducts().then((response) => {
    store.commit("stopLoading");
    commit("setUpProducts", response.products);
  });
};

export default {
  fetchProducts,
};
