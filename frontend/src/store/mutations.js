const setUser = (state, user) => {
  state.user = user;
};

const startLoading = (state) => {
  state.loading = true;
};

const stopLoading = (state) => {
  state.loading = false;
};

const setUpProducts = (state, productsPayload) => {
  state.products = productsPayload;
};

export default {
  setUser,
  setUpProducts,
  startLoading,
  stopLoading,
};
