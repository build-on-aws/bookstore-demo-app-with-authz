import { getProducts } from "@/backend/api.js";

const setLoading = ({ commit }, payload) => {
  commit("setLoading", { value: payload.value, message: payload.message });
};

const fetchProducts = ({ commit }) => {
  getProducts().then((response) => {
    commit("setUpProducts", response.products);
  });
};

export default {
  setLoading,
  fetchProducts,
};
