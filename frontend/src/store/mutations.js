const setUser = (state, user) => {
  state.user = user;
};

const setUpProducts = (state, productsPayload) => {
  productsPayload.forEach((product) => {
    product.addLoading = false;
    product.removeLoading = false;
  });
  state.products = productsPayload;
};

const setLoading = (state, payload) => {
  state.loading = payload.value;
  state.loadingText = payload.message;
};
const setProductLoading = (state, { product, btn, value }) => {
  let prod = state.products.find((prod) => prod.productId === product.productId);
  prod[btn + "Loading"] = value;
};

export default {
  setUser,
  setUpProducts,
  setLoading,
  setProductLoading,
};
