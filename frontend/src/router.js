import VueRouter from "vue-router";
import Vue from "vue";
import store from "@/store/store.js";
import Home from "@/views/Home.vue";
import Auth from "@/views/Auth.vue";
import { AmplifyEventBus } from "aws-amplify-vue";
import * as AmplifyModules from "aws-amplify";
import { AmplifyPlugin } from "aws-amplify-vue";

Vue.use(AmplifyPlugin, AmplifyModules);

getUser().then((user) => {
  if (user) {
    router.push({ path: "/" }).catch(() => {});
  }
});

AmplifyEventBus.$on("authState", async (state) => {
  if (state === "signedOut") {
    store.commit("setUser", null);
    router
      .push({
        path: "/auth",
      })
      .catch(() => {});
  } else if (state === "signedIn") {
    router
      .push({
        path: new URLSearchParams(window.location.search).get("redirect") || "/",
      })
      .catch(() => {});
  }
});

function getUser() {
  return Vue.prototype.$Amplify.Auth.currentAuthenticatedUser()
    .then((data) => {
      if (data && data.signInUserSession) {
        store.commit("setUser", data);
        return data;
      }
    })
    .catch(() => {
      store.commit("setUser", null);
      return null;
    });
}
const routes = [
  {
    path: "/",
    component: Home,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/auth",
    name: "Authenticator",
    component: Auth,
  },
];

const router = new VueRouter({
  mode: "history",
  routes,
});

router.beforeResolve(async (to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    let user = await getUser();
    if (!user) {
      return next({
        path: "/auth",
        query: {
          redirect: to.fullPath,
        },
      });
    }
    return next();
  }
  return next();
});

export default router;
