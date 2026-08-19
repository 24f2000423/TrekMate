import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ProfileView from '../views/ProfileView.vue';
import TrekDetailsView from '../views/TrekDetailsView.vue';

// User Views
import UserDashboardView from '../views/user/UserDashboardView.vue';
import UserBookingsView from '../views/user/UserBookingsView.vue';
import UserHistoryView from '../views/user/UserHistoryView.vue';

// Staff Views
import StaffDashboardView from '../views/staff/StaffDashboardView.vue';
import StaffTrekDetailView from '../views/staff/StaffTrekDetailView.vue';

// Admin Views
import AdminDashboardView from '../views/admin/AdminDashboardView.vue';
import AdminTreksView from '../views/admin/AdminTreksView.vue';
import AdminStaffView from '../views/admin/AdminStaffView.vue';
import AdminUsersView from '../views/admin/AdminUsersView.vue';
import AdminReportsView from '../views/admin/AdminReportsView.vue';

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/trek/:id', name: 'trek-details', component: TrekDetailsView },

  // User (Trekker) Routes
  { path: '/user/dashboard', name: 'user-dashboard', component: UserDashboardView, meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/user/bookings', name: 'user-bookings', component: UserBookingsView, meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/user/history', name: 'user-history', component: UserHistoryView, meta: { requiresAuth: true, roles: ['user'] } },

  // Staff Routes
  { path: '/staff/dashboard', name: 'staff-dashboard', component: StaffDashboardView, meta: { requiresAuth: true, roles: ['staff', 'admin'] } },
  { path: '/staff/trek/:id', name: 'staff-trek-detail', component: StaffTrekDetailView, meta: { requiresAuth: true, roles: ['staff', 'admin'] } },

  // Admin Routes
  { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/treks', name: 'admin-treks', component: AdminTreksView, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/staff', name: 'admin-staff', component: AdminStaffView, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/users', name: 'admin-users', component: AdminUsersView, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/reports', name: 'admin-reports', component: AdminReportsView, meta: { requiresAuth: true, roles: ['admin'] } },

  // Catch-all
  { path: '/:pathMatch(.*)*', redirect: '/' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('tma_token');
  const user = JSON.parse(localStorage.getItem('tma_user') || 'null');

  if (to.meta.requiresAuth) {
    if (!token || !user) {
      return next({ path: '/login', query: { redirect: to.fullPath } });
    }

    if (to.meta.roles && !to.meta.roles.includes(user.role)) {
      // Unauthorized role, redirect to appropriate home
      if (user.role === 'admin') return next('/admin/dashboard');
      if (user.role === 'staff') return next('/staff/dashboard');
      return next('/user/dashboard');
    }
  }

  next();
});

export default router;
