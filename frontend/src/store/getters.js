const currentUser = (state) => {
  return state.user;
};

const loading = (state) => {
  return state.loading;
};

export default {
  currentUser,
  loading,
};
