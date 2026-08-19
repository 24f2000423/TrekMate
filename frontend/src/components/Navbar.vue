<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-success sticky-top shadow-sm">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center fw-bold fs-4" to="/">
        <span class="me-2">🏔️</span> TMA <span class="badge bg-light text-success ms-2 fs-6">V2</span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarMain"
        aria-controls="navbarMain"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarMain">
        <!-- Left Side Navigation -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" to="/">
              <i class="bi bi-house-door me-1"></i> Home
            </router-link>
          </li>

          <!-- User / Trekker Links -->
          <template v-if="isTrekker">
            <li class="nav-item">
              <router-link class="nav-link" to="/user/dashboard">
                <i class="bi bi-speedometer2 me-1"></i> Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/bookings">
                <i class="bi bi-calendar-check me-1"></i> My Bookings
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/history">
                <i class="bi bi-clock-history me-1"></i> Trek History & Export
              </router-link>
            </li>
          </template>

          <!-- Staff Links -->
          <template v-if="isStaff">
            <li class="nav-item">
              <router-link class="nav-link" to="/staff/dashboard">
                <i class="bi bi-person-badge me-1"></i> Staff Portal
              </router-link>
            </li>
          </template>

          <!-- Admin Links -->
          <template v-if="isAdmin">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard">
                <i class="bi bi-graph-up-arrow me-1"></i> Admin Analytics
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/treks">
                <i class="bi bi-map me-1"></i> Manage Treks
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/staff">
                <i class="bi bi-people me-1"></i> Staff Roster
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/users">
                <i class="bi bi-shield-check me-1"></i> User Moderation
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/reports">
                <i class="bi bi-file-earmark-bar-graph me-1"></i> Reports
              </router-link>
            </li>
          </template>
        </ul>

        <!-- Right Side Nav / User Controls -->
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center">
          <template v-if="isLoggedIn">
            <!-- Notifications Dropdown -->
            <li class="nav-item dropdown me-3">
              <a
                class="nav-link position-relative text-white dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                @click="loadNotifications"
              >
                <i class="bi bi-bell fs-5"></i>
                <span
                  v-if="state.unreadNotifsCount > 0"
                  class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                >
                  {{ state.unreadNotifsCount }}
                </span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow p-2" style="min-width: 320px; max-height: 400px; overflow-y: auto;">
                <li class="d-flex justify-content-between align-items-center px-2 py-1 border-bottom">
                  <span class="fw-bold small text-muted">Notifications</span>
                  <button
                    v-if="state.unreadNotifsCount > 0"
                    class="btn btn-link btn-sm text-decoration-none p-0 text-success"
                    @click.stop="markAllNotificationsAsRead"
                  >
                    Mark all read
                  </button>
                </li>
                <li v-if="state.notifications.length === 0" class="text-center py-3 text-muted small">
                  No notifications yet
                </li>
                <li
                  v-for="notif in state.notifications"
                  :key="notif.id"
                  class="dropdown-item rounded p-2 my-1"
                  :class="{'bg-light fw-bold': !notif.is_read}"
                  @click="markAsRead(notif.id)"
                  style="cursor: pointer; white-space: normal;"
                >
                  <div class="d-flex align-items-center justify-content-between">
                    <span class="badge" :class="getNotifBadgeClass(notif.type)">{{ notif.type }}</span>
                    <small class="text-muted" style="font-size: 10px;">{{ notif.created_at }}</small>
                  </div>
                  <div class="small mt-1 text-dark">{{ notif.title }}</div>
                  <div class="text-muted" style="font-size: 11px;">{{ notif.message }}</div>
                </li>
              </ul>
            </li>

            <!-- User Profile Dropdown -->
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle text-white d-flex align-items-center"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <div class="rounded-circle bg-white text-success fw-bold d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px;">
                  {{ user?.name ? user.name.charAt(0).toUpperCase() : 'U' }}
                </div>
                <span>{{ user?.name }}</span>
                <span class="badge bg-dark ms-2 text-uppercase" style="font-size: 10px;">{{ user?.role }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person me-2"></i> My Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <button class="dropdown-item text-danger" @click="handleLogout">
                    <i class="bi bi-box-arrow-right me-2"></i> Log Out
                  </button>
                </li>
              </ul>
            </li>
          </template>

          <template v-else>
            <li class="nav-item">
              <router-link class="btn btn-outline-light btn-sm me-2 px-3" to="/login">
                <i class="bi bi-box-arrow-in-right me-1"></i> Log In
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="btn btn-warning btn-sm text-dark fw-bold px-3" to="/register">
                <i class="bi bi-person-plus me-1"></i> Register
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../store/auth';

const router = useRouter();
const {
  state,
  isLoggedIn,
  user,
  isAdmin,
  isStaff,
  isTrekker,
  logout,
  fetchNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead
} = useAuth();

const loadNotifications = () => {
  if (isLoggedIn.value) {
    fetchNotifications();
  }
};

const markAsRead = (id) => {
  markNotificationAsRead(id);
};

const getNotifBadgeClass = (type) => {
  switch (type) {
    case 'reminder': return 'bg-warning text-dark';
    case 'booking': return 'bg-success';
    case 'cancellation': return 'bg-danger';
    case 'report': return 'bg-info text-dark';
    default: return 'bg-secondary';
  }
};

const handleLogout = () => {
  logout();
  router.push('/login');
};

onMounted(() => {
  if (isLoggedIn.value) {
    fetchNotifications();
  }
});
</script>
