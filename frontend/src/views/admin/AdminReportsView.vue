<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">📊 Monthly Activity Reports & Batch Jobs</h2>
        <p class="text-muted mb-0">Celery scheduled reports, PDF/HTML document generators, and automated dispatch</p>
      </div>
    </div>

    <!-- Alert -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show shadow-sm" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Top Action Cards -->
    <div class="row g-4 mb-4">
      <!-- Generate Report Card -->
      <div class="col-md-6">
        <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
          <div class="d-flex align-items-center mb-3">
            <div class="rounded-circle bg-success-subtle text-success p-3 me-3">
              <i class="bi bi-file-earmark-pdf fs-4"></i>
            </div>
            <div>
              <h5 class="fw-bold mb-0">Trigger Monthly Activity Report</h5>
              <small class="text-muted">Generates HTML & downloadable PDF with metrics & popular treks</small>
            </div>
          </div>

          <form @submit.prevent="generateReport" class="mt-2">
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-bold">Month</label>
                <select v-model="reportForm.month" class="form-select">
                  <option v-for="m in 12" :key="m" :value="m">
                    {{ new Date(2026, m - 1, 1).toLocaleString('default', { month: 'long' }) }}
                  </option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label small fw-bold">Year</label>
                <input type="number" v-model="reportForm.year" class="form-control" min="2020" max="2030" />
              </div>
            </div>

            <button type="submit" class="btn btn-success w-100 fw-bold" :disabled="generating">
              <span v-if="generating" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-gear-wide-connected me-1"></i>
              Generate Monthly Report (Celery)
            </button>
          </form>
        </div>
      </div>

      <!-- Test Daily Reminders Card -->
      <div class="col-md-6">
        <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
          <div class="d-flex align-items-center mb-3">
            <div class="rounded-circle bg-primary-subtle text-primary p-3 me-3">
              <i class="bi bi-bell-fill fs-4"></i>
            </div>
            <div>
              <h5 class="fw-bold mb-0">Scheduled Daily Reminders</h5>
              <small class="text-muted">Sends upcoming trek alerts (start dates, packing gear, instructions)</small>
            </div>
          </div>

          <p class="small text-muted mb-4">
            Runs daily at 8:00 AM via Celery Beat scheduler. Scans for treks starting in the next 3 days and dispatches notifications & simulated webhook logs.
          </p>

          <button class="btn btn-outline-primary w-100 fw-bold" :disabled="runningReminders" @click="runReminders">
            <span v-if="runningReminders" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-send-check me-1"></i>
            Trigger Daily Reminders Now
          </button>
        </div>
      </div>
    </div>

    <!-- Available Generated Reports Table -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
        <h5 class="fw-bold mb-0">
          <i class="bi bi-folder2-open text-success me-2"></i>Generated Monthly Reports ({{ reports.length }})
        </h5>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchReports">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
        </div>

        <div v-else-if="reports.length === 0" class="text-center py-5 text-muted">
          <i class="bi bi-file-earmark-x display-4 d-block mb-2"></i>
          <h5>No reports generated yet</h5>
          <p>Click "Generate Monthly Report" above to compile the report.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Format</th>
                <th>File Name</th>
                <th>File Size</th>
                <th>Generated At</th>
                <th class="text-end">Download / View</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in reports" :key="r.filename">
                <td>
                  <span class="badge" :class="r.file_type === 'PDF' ? 'bg-danger' : 'bg-primary'">
                    <i :class="r.file_type === 'PDF' ? 'bi bi-filetype-pdf' : 'bi bi-filetype-html'" class="me-1"></i>
                    {{ r.file_type }}
                  </span>
                </td>
                <td class="fw-bold text-dark">{{ r.filename }}</td>
                <td class="small text-muted">{{ (r.size_bytes / 1024).toFixed(1) }} KB</td>
                <td class="small text-muted">{{ r.created_at }}</td>
                <td class="text-end">
                  <div class="btn-group">
                    <a
                      :href="r.download_url"
                      target="_blank"
                      class="btn btn-sm btn-outline-secondary"
                      title="Open in Browser"
                    >
                      <i class="bi bi-box-arrow-up-right me-1"></i> View
                    </a>
                    <a
                      :href="`${r.download_url}?download=true`"
                      class="btn btn-sm btn-success"
                      download
                      title="Download Document"
                    >
                      <i class="bi bi-download me-1"></i> Download
                    </a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api';

const reports = ref([]);
const loading = ref(true);
const generating = ref(false);
const runningReminders = ref(false);
const successMsg = ref('');
const errorMsg = ref('');

const today = new Date();
const reportForm = reactive({
  month: today.getMonth() + 1,
  year: today.getFullYear()
});

const fetchReports = async () => {
  loading.value = true;
  try {
    const res = await api.get('/reports/monthly-reports');
    reports.value = res.data.reports || [];
  } catch (err) {
    console.error('Failed to load reports', err);
  } finally {
    loading.value = false;
  }
};

const generateReport = async () => {
  generating.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.post('/reports/generate-monthly-report', reportForm);
    successMsg.value = res.data.message || 'Report generated successfully!';
    await fetchReports();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to generate report';
  } finally {
    generating.value = false;
  }
};

const runReminders = async () => {
  runningReminders.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.post('/reports/trigger-daily-reminders');
    successMsg.value = res.data.message || 'Daily reminders dispatched!';
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to run daily reminders';
  } finally {
    runningReminders.value = false;
  }
};

onMounted(() => {
  fetchReports();
});
</script>
