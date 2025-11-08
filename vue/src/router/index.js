import { createWebHistory, createRouter } from 'vue-router'
import StationSelector from "@/views/StationSelector.vue";
import StationSummary from "@/views/StationSummary.vue";

const routes = [
  // {
  //   redirect: { name: 'Home' },
  // },
  {
    // path: '/home',
    path: '/',
    component: StationSelector,
    name: 'Home',
  },
  {
    path: '/station/:station_id',
    component: StationSummary,
    name: 'Station',
  },
]



const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
