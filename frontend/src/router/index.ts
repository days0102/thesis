/*
 * @Author       : Outsider
 * @Date         : 2023-11-24 09:39:25
 * @LastEditors  : Outsider
 * @LastEditTime : 2023-11-30 10:04:29
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\router\index.ts
 */
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/analysis',
      name: 'analysis',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/LogAnalysisView.vue')
    },
    {
      path: '/bank',
      name: 'bank',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/BankView.vue')
    }
  ]
})

export default router
