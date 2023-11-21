import { API, Auth } from "aws-amplify";

async function getHeaders() {
  const headers = {
    "Content-Type": "application/json",
  };

  let session = null;

  try {
    session = await Auth.currentSession();
  } catch (error) {
    console.error(`Error getting current session: ${error}`);
  }

  if (session) {
    headers["Authorization"] = session.getIdToken().jwtToken;
  }

  return headers;
}

export async function getProducts() {
  return getHeaders().then((headers) =>
    API.get("ProductServiceAPI", "/product", {
      headers: headers,
      withCredentials: true,
    }),
  );
}
