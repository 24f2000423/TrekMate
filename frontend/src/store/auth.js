import { reactive, computed } from 'vue';
import api from '../api';

const state = reactive({
  token: localStorage.getItem('tma_token') || null,
  user: JSON.parse(localStorage.getItem('tma_user') || 'null'),
  notifications: [],
  unreadNotifsCount: 0,
});

export const useAuth = () => {
  const isLoggedIn = computed(() => !!state.token && !!state.user);
  const user = computed(() => state.user);
  const role = computed(() => state.user?.role || null);
  const isAdmin = computed(() => state.user?.role === 'admin');
  const isStaff = computed(() => state.user?.role === 'staff');
  const isTrekker = computed(() => state.user?.role === 'user');

  const setAuth = (token, userData) => {
    state.token = token;
    state.user = userData;
    localStorage.setItem('tma_token', token);
    localStorage.setItem('tma_user', JSON.stringify(userData));
  };

  const logout = () => {
    state.token = null;
    state.user = null;
    state.notifications = [];
    state.unreadNotifsCount = 0;
    localStorage.removeItem('tma_token');
    localStorage.removeItem('tma_user');
  };

  const fetchProfile = async () => {
    if (!state.token) return;
    try {
      const res = await api.get('/auth/me');
      state.user = res.data.user;
      localStorage.setItem('tma_user', JSON.stringify(res.data.user));
    } catch (err) {
      console.error('Failed to fetch profile', err);
    }
  };

  const fetchNotifications = async () => {
    if (!state.token) return;
    try {
      const res = await api.get('/reports/notifications');
      state.notifications = res.data.notifications || [];
      state.unreadNotifsCount = res.data.unread_count || 0;
    } catch (err) {
      console.error('Failed to fetch notifications', err);
    }
  };

  const markNotificationAsRead = async (notifId) => {
    try {
      await api.put(`/reports/notifications/${notifId}/read`);
      const notif = state.notifications.find(n => n.id === notifId);
      if (notif && !notif.is_read) {
        notif.is_read = true;
        state.unreadNotifsCount = Math.max(0, state.unreadNotifsCount - 1);
      }
    } catch (err) {
      console.error('Failed to mark notification as read', err);
    }
  };

  const markAllNotificationsAsRead = async () => {
    try {
      await api.put('/reports/notifications/read-all');
      state.notifications.forEach(n => { n.is_read = true; });
      state.unreadNotifsCount = 0;
    } catch (err) {
      console.error('Failed to mark all as read', err);
    }
  };

  return {
    state,
    isLoggedIn,
    user,
    role,
    isAdmin,
    isStaff,
    isTrekker,
    setAuth,
    logout,
    fetchProfile,
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
  };
};
