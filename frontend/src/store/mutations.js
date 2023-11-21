const setUser = (state, user) => {
  state.user = user;
};

const setUpProducts = (state, productsPayload) => {
  state.products = productsPayload;
};

export default {
  setUser,
  setUpProducts,
};
