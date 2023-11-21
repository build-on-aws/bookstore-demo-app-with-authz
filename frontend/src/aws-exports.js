const awsmobile = {
  Auth: {
    region: process.env.VUE_APP_AWS_REGION,
    userPoolId: process.env.VUE_APP_USER_POOL_ID,
    userPoolWebClientId: process.env.VUE_APP_USER_POOL_CLIENT_ID,
  },
  API: {
    endpoints: [
      {
        name: "ProductServiceAPI",
        endpoint: process.env.VUE_APP_PRODUCT_SERVICE_API_URL,
      },
    ],
  },
};
export default awsmobile;
