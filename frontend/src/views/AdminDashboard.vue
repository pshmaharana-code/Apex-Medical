<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios';

// --- CHART.JS IMPORTS ---
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js'
import { Pie, Doughnut } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, Title)

const authStore = useAuthStore()
const router = useRouter()

const activeTab = ref('overview')

// --- OVERVIEW STATE ---
const stats = ref({
    total_doctors: 0,
    total_patients: 0,
    total_appointments: 0,
    recent_activity: [],
    charts: null // Holds the raw chart data from Flask
})
const isLoading = ref(true)
const errorMessage = ref('')

// --- DEPARTMENT & STAFF/PATIENT STATE ---
const departments = ref([])
const newDepartment = ref({ name: '', description: '' })
const isAddingDept = ref(false)
const deptMessage = ref(''); const deptError = ref('')

const newDoctor = ref({ name: '', email: '', username: '', password: '', department_id: '', experience: '' })
// --- CUSTOM DROPDOWN STATE ---
const isDeptDropdownOpen = ref(false)

const getSelectedDeptName = computed(() => {
    if (!newDoctor.value.department_id) return 'Select a Department...'
    const dept = departments.value.find(d => d.id === newDoctor.value.department_id)
    return dept ? dept.name : 'Select a Department...'
})

const selectDept = (id) => {
    newDoctor.value.department_id = id
    isDeptDropdownOpen.value = false
}
const isRegistering = ref(false)
const registerMessage = ref(''); const registerError = ref('')

const systemUsers = ref({ doctors: [], patients: [] })

// --- CHART DATA FORMATTING (COMPUTED PROPS) ---
// These automatically format the Flask data into the exact structure Chart.js demands
const departmentChartData = computed(() => {
    if (!stats.value.charts) return null;
    return {
        labels: stats.value.charts.departments.labels,
        datasets: [{
            data: stats.value.charts.departments.data,
            // Executive Amethyst Palette
            backgroundColor: ['#7c3aed', '#9333ea', '#c026d3', '#db2777', '#4f46e5', '#3b82f6'],
            borderWidth: 0,
            hoverOffset: 4
        }]
    }
})

const appointmentChartData = computed(() => {
    if (!stats.value.charts) return null;
    return {
        labels: stats.value.charts.appointments.labels,
        datasets: [{
            data: stats.value.charts.appointments.data,
            // Blue (Booked), Green (Completed), Red (Cancelled)
            backgroundColor: ['#3b82f6', '#10b981', '#ef4444'], 
            borderWidth: 0,
            hoverOffset: 4
        }]
    }
})
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%', // Makes the Doughnut/Pie look sleeker and modern
    plugins: {
        legend: { 
            position: 'bottom',
            labels: { 
                color: '#64748b', 
                font: { family: 'Plus Jakarta Sans', weight: '700', size: 12 },
                padding: 20,
                usePointStyle: true,
                pointStyle: 'circle'
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleFont: { family: 'Outfit', size: 14, weight: '800' },
            bodyFont: { family: 'Plus Jakarta Sans', size: 13, weight: '500' },
            padding: 12,
            cornerRadius: 12,
            boxPadding: 6
        }
    }
}

// --- FETCH FUNCTIONS ---
const fetchDashboard = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/dashboard', { headers: { Authorization: `Bearer ${authStore.token}` } })
        stats.value = response.data
    } catch (error) {
        errorMessage.value = "Could not load hospital analytics."
    } finally {
        isLoading.value = false
    }
}

const fetchDepartments = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/departments', { headers: { Authorization: `Bearer ${authStore.token}` } })
        departments.value = response.data
    } catch (error) {}
}

const fetchSystemUsers = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/system-users', { headers: { Authorization: `Bearer ${authStore.token}` } })
        systemUsers.value = response.data
    } catch (error) {}
}

// --- CRUD & ACTION FUNCTIONS ---
const addDepartment = async () => {
    isAddingDept.value = true; deptMessage.value = ''; deptError.value = ''
    try {
        const response = await axios.post('http://127.0.0.1:5000/api/admin/departments', newDepartment.value, { headers: { Authorization: `Bearer ${authStore.token}` } })
        deptMessage.value = response.data.msg
        newDepartment.value = { name: '', description: '' }
        fetchDepartments()
    } catch (error) { deptError.value = error.response?.data?.msg || "Failed to add department." } 
    finally { isAddingDept.value = false }
}

const deleteDepartment = async (id) => {
    if (!confirm("Are you sure you want to delete this department?")) return;
    try {
        const response = await axios.delete(`http://127.0.0.1:5000/api/admin/departments/${id}`, { headers: { Authorization: `Bearer ${authStore.token}` } })
        alert(response.data.msg)
        fetchDepartments()
    } catch (error) { alert(error.response?.data?.msg || "Failed to delete department.") }
}

const registerDoctor = async () => {
    isRegistering.value = true; registerMessage.value = ''; registerError.value = ''
    try {
        const response = await axios.post('http://127.0.0.1:5000/api/admin/doctors', newDoctor.value, { headers: { Authorization: `Bearer ${authStore.token}` } })
        registerMessage.value = response.data.msg
        newDoctor.value = { name: '', email: '', username: '', password: '', department_id: '', experience: '' }
        fetchDashboard(); fetchDepartments(); fetchSystemUsers();
    } catch (error) { registerError.value = error.response?.data?.msg || "Failed to register the doctor." } 
    finally { isRegistering.value = false }
}

const toggleUserStatus = async (userId, currentStatus) => {
    const action = currentStatus === 'active' ? 'blacklist' : 'reactivate';
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;
    try {
        const response = await axios.patch(`http://127.0.0.1:5000/api/admin/users/${userId}/toggle-status`, {}, { headers: { Authorization: `Bearer ${authStore.token}` } })
        alert(response.data.msg)
        fetchSystemUsers()
    } catch (error) { alert(error.response?.data?.msg || "Failed to update user status.") }
}

const handleLogout = () => {
    authStore.logout(); router.push('/login')
}


// --- GLOBAL RADIO RECEIVER (ADMIN SSE) ---
const setupAdminLiveUpdates = () => {
    // 1. Tune the radio directly to the master 'admin_alerts' channel
    const eventSource = new EventSource('http://127.0.0.1:5000/stream?channel=admin_alerts');

    // 2. Listen for the 'new_appointment' global broadcast
    eventSource.addEventListener('new_appointment', (event) => {
        const data = JSON.parse(event.data);
        console.log("GLOBAL ALERT RECEIVED:", data.message);
        
        // 3. Instantly refresh the admin stats and tables!
        // (Make sure this matches the exact name of your data-fetching function)
        fetchDashboard(); 
        
    });

    eventSource.onerror = (error) => {
        console.error("Admin SSE connection lost. Reconnecting...", error);
    };
}

onMounted(() => {
    fetchDashboard(); fetchDepartments(); fetchSystemUsers(); setupAdminLiveUpdates();
})
</script>

<template>
    <div class="executive-layout">
        
        <div class="dynamic-bg">
            <div class="orb orb-violet"></div>
            <div class="orb orb-amethyst"></div>
            <div class="orb orb-slate"></div>
        </div>

        <aside class="side-nav glass-panel">
            <div class="brand-header">
                <div class="logo-mark admin-gradient">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width: 20px; height: 20px; color: white;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
                </div>
                <span class="logo-text">Apex Admin</span>
            </div>

            <nav class="nav-links">
                <div class="nav-section-title">COMMAND CENTER</div>
                <button :class="['nav-btn', { active: activeTab === 'overview' }]" @click="activeTab = 'overview'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
                    System Overview
                </button>
                
                <div class="nav-section-title mt-4">HOSPITAL MANAGEMENT</div>
                <button :class="['nav-btn', { active: activeTab === 'departments' }]" @click="activeTab = 'departments'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                    Departments
                </button>
                <button :class="['nav-btn', { active: activeTab === 'staff' }]" @click="activeTab = 'staff'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    Staff Directory
                </button>
                <button :class="['nav-btn', { active: activeTab === 'patients' }]" @click="activeTab = 'patients'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                    Patient Database
                </button>
            </nav>

            <div class="sidebar-footer">
                <button @click="handleLogout" class="btn-logout-sidebar">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    Secure Logout
                </button>
            </div>
        </aside>

        <main class="workspace">
            
            <header class="top-nav glass-panel-header">
                <div class="date-display">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }) }}
                </div>
                
                <div class="top-actions">
                    <button class="icon-btn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                        <span class="notification-dot"></span>
                    </button>
                    <div class="user-profile">
                        <div class="avatar-placeholder admin-gradient">A</div>
                        <div class="profile-text">
                            <span class="user-name">Super Admin</span>
                            <span class="profile-subtext">System Controls</span>
                        </div>
                    </div>
                </div>
            </header>

            <div class="content-area">

                <div v-if="activeTab === 'overview'" class="fade-in-up">
                    <div class="welcome-banner">
                        <h1 class="sofi-title">System Overview</h1>
                        <p class="banner-dept">Real-time hospital analytics and live activity feed.</p>
                    </div>

                    <div v-if="isLoading" class="loading-state glass-card">
                        <div class="spinner"></div><p>Aggregating hospital data...</p>
                    </div>
                    <div v-else-if="errorMessage" class="error-message glass-card">{{ errorMessage }}</div>
                    <div v-else>
                        
                        <div class="stats-grid">
                            <div class="stat-card glass-card">
                                <div class="stat-icon icon-emerald">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                                </div>
                                <div class="stat-info">
                                    <h3>Total Patients</h3>
                                    <p class="stat-number">{{ stats.total_patients }}</p>
                                </div>
                            </div>
                            <div class="stat-card glass-card">
                                <div class="stat-icon icon-violet">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                                </div>
                                <div class="stat-info">
                                    <h3>Total Doctors</h3>
                                    <p class="stat-number">{{ stats.total_doctors }}</p>
                                </div>
                            </div>
                            <div class="stat-card glass-card">
                                <div class="stat-icon icon-blue">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                                </div>
                                <div class="stat-info">
                                    <h3>Total Appointments</h3>
                                    <p class="stat-number">{{ stats.total_appointments }}</p>
                                </div>
                            </div>
                        </div>

                        <div class="charts-grid" v-if="stats.charts">
                            <div class="chart-card glass-card">
                                <div class="card-header">
                                    <h2>Staff Distribution</h2>
                                    <p class="subtitle">Doctors by hospital department</p>
                                </div>
                                <div class="chart-wrapper"><Doughnut v-if="departmentChartData" :data="departmentChartData" :options="chartOptions" /></div>
                            </div>
                            <div class="chart-card glass-card">
                                <div class="card-header">
                                    <h2>Appointment Health</h2>
                                    <p class="subtitle">Completion vs Cancellation rates</p>
                                </div>
                                <div class="chart-wrapper"><Doughnut v-if="appointmentChartData" :data="appointmentChartData" :options="chartOptions" /></div>
                            </div>
                        </div>

                        <div class="recent-activity glass-card p-0">
                            <div class="card-header border-bottom">
                                <h2>Live Hospital Feed</h2>
                                <p class="subtitle">Most recent appointment bookings and updates</p>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr><th>Appt ID</th><th>Date & Time</th><th>Doctor</th><th>Patient</th><th class="text-right">Status</th></tr>
                                </thead>
                                <tbody>
                                    <tr v-for="appt in stats.recent_activity" :key="appt.id">
                                        <td class="font-mono"><strong>#{{ appt.id }}</strong></td>
                                        <td>{{ new Date(appt.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}</td>
                                        <td><strong>Dr. {{ appt.doctor }}</strong></td>
                                        <td>{{ appt.patient }}</td>
                                        <td class="text-right"><span :class="['status-badge', appt.status.toLowerCase()]">{{ appt.status }}</span></td>
                                    </tr>
                                </tbody>
                            </table>
                            <div v-if="stats.recent_activity.length === 0" class="empty-state">No recent activity detected.</div>
                        </div>
                    </div>
                </div>

                <div v-if="activeTab === 'departments'" class="fade-in-up">
                    <div class="welcome-banner">
                        <h1 class="sofi-title">Manage Departments</h1>
                        <p class="banner-dept">Add new medical departments and view current capacity.</p>
                    </div>
                    
                    <div class="glass-card" style="padding: 2.5rem; margin-bottom: 2rem;">
                        <div class="card-header p-0" style="margin-bottom: 1.5rem;">
                            <h2>Add New Department</h2>
                        </div>
                        
                        <div v-if="deptMessage" class="success-message">{{ deptMessage }}</div>
                        <div v-if="deptError" class="error-message">{{ deptError }}</div>
                        
                        <form @submit.prevent="addDepartment" class="pro-form">
                            <div class="form-group">
                                <label>Department Name</label>
                                <input type="text" v-model="newDepartment.name" class="pro-input" required placeholder="e.g., Neurology">
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea v-model="newDepartment.description" class="pro-input" rows="4" placeholder="Briefly describe the department..."></textarea>
                            </div>
                            <div class="form-actions-bar p-0" style="border:none; margin-top: 1rem;">
                                <button type="submit" class="btn-primary-violet" :disabled="isAddingDept">
                                    {{ isAddingDept ? 'Creating...' : 'Create Department' }}
                                </button>
                            </div>
                        </form>
                    </div>

                    <div class="glass-card p-0">
                        <div class="card-header border-bottom">
                            <h2>Current Departments</h2>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr><th>Department Name</th><th>Total Doctors</th><th class="text-right">Action</th></tr>
                            </thead>
                            <tbody>
                                <tr v-for="dept in departments" :key="dept.id">
                                    <td><strong>{{ dept.name }}</strong></td>
                                    <td><span class="status-badge booked">{{ dept.doctor_count }} Doctors</span></td>
                                    <td class="text-right">
                                        <button @click="deleteDepartment(dept.id)" class="btn-outline-danger" :disabled="dept.doctor_count > 0" :title="dept.doctor_count > 0 ? 'Cannot delete department with active doctors' : ''">
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div v-if="departments.length === 0" class="empty-state">No departments created yet.</div>
                    </div>
                </div>

                <div v-if="activeTab === 'staff'" class="fade-in-up">
                    <div class="welcome-banner">
                        <h1 class="sofi-title">Staff Directory</h1>
                        <p class="banner-dept">Register new doctors and manage system access.</p>
                    </div>

                    <div class="glass-card" style="padding: 2.5rem; margin-bottom: 2rem; position: relative; z-index: 50;">
                        <div class="card-header p-0" style="margin-bottom: 2rem;">
                            <h2>Register New Doctor</h2>
                        </div>
                        
                        <div v-if="registerMessage" class="success-message">{{ registerMessage }}</div>
                        <div v-if="registerError" class="error-message">{{ registerError }}</div>

                        <form @submit.prevent="registerDoctor" class="pro-form">
                            <div class="form-row">
                                <div class="form-group half-width">
                                    <label>Full Name</label>
                                    <input type="text" v-model="newDoctor.name" class="pro-input" required placeholder="e.g., Basant Maharana">
                                </div>
                                <div class="form-group half-width">
                                    <label>Department</label>
                                    
                                    <div class="custom-select-container">
                                        <div v-if="isDeptDropdownOpen" class="dropdown-overlay" @click="isDeptDropdownOpen = false"></div>
                                        
                                        <div class="pro-input select-display" @click="isDeptDropdownOpen = !isDeptDropdownOpen" :class="{ 'is-active': isDeptDropdownOpen }">
                                            <span>{{ getSelectedDeptName }}</span>
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                                        </div>
                                        
                                        <ul v-if="isDeptDropdownOpen" class="custom-options-list fade-in-up">
                                            <li class="custom-option disabled">Select a Department...</li>
                                            <li v-for="dept in departments" :key="dept.id" @click="selectDept(dept.id)" class="custom-option">
                                                {{ dept.name }}
                                            </li>
                                        </ul>
                                    </div>
                                    
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group third-width">
                                    <label>Email Address</label>
                                    <input type="email" v-model="newDoctor.email" class="pro-input" required placeholder="doctor@apex.com">
                                </div>
                                <div class="form-group third-width">
                                    <label>System Username</label>
                                    <input type="text" v-model="newDoctor.username" class="pro-input" required placeholder="dr_basant">
                                </div>
                                <div class="form-group third-width">
                                    <label>Temporary Password</label>
                                    <input type="password" v-model="newDoctor.password" class="pro-input" required placeholder="Min 6 characters">
                                </div>
                            </div>
                            <div class="form-actions-bar p-0" style="border:none; margin-top: 1rem;">
                                <button type="submit" class="btn-primary-violet" :disabled="isRegistering">
                                    {{ isRegistering ? 'Registering...' : 'Register Doctor' }}
                                </button>
                            </div>
                        </form>
                    </div>

                    <div class="glass-card p-0">
                        <div class="card-header border-bottom">
                            <h2>Staff Access Control</h2>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr><th>Doctor Name</th><th>Department</th><th>Email</th><th>System Status</th><th class="text-right">Action</th></tr>
                            </thead>
                            <tbody>
                                <tr v-for="doc in systemUsers.doctors" :key="doc.id">
                                    <td><strong>Dr. {{ doc.name }}</strong></td>
                                    <td>{{ doc.department }}</td>
                                    <td>{{ doc.email }}</td>
                                    <td><span :class="['system-status', doc.status]">{{ doc.status.toUpperCase() }}</span></td>
                                    <td class="text-right">
                                        <button @click="toggleUserStatus(doc.user_id, doc.status)" :class="doc.status === 'active' ? 'btn-outline-warning' : 'btn-outline-success'">
                                            {{ doc.status === 'active' ? 'Suspend' : 'Reactivate' }}
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div v-if="activeTab === 'patients'" class="fade-in-up">
                    <div class="welcome-banner">
                        <h1 class="sofi-title">Patient Database</h1>
                        <p class="banner-dept">Monitor registered patients and manage system access.</p>
                    </div>
                    
                    <div class="glass-card p-0">
                        <div class="card-header border-bottom">
                            <h2>Registered Patients</h2>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr><th>Patient Name</th><th>Contact</th><th>Email Address</th><th>System Status</th><th class="text-right">Action</th></tr>
                            </thead>
                            <tbody>
                                <tr v-for="pat in systemUsers.patients" :key="pat.id">
                                    <td><strong>{{ pat.name }}</strong></td>
                                    <td>{{ pat.contact || 'N/A' }}</td>
                                    <td>{{ pat.email }}</td>
                                    <td><span :class="['system-status', pat.status]">{{ pat.status.toUpperCase() }}</span></td>
                                    <td class="text-right">
                                        <button @click="toggleUserStatus(pat.user_id, pat.status)" :class="pat.status === 'active' ? 'btn-outline-warning' : 'btn-outline-success'">
                                            {{ pat.status === 'active' ? 'Suspend' : 'Reactivate' }}
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div v-if="systemUsers.patients.length === 0" class="empty-state">No patients registered in the system.</div>
                    </div>
                </div>

            </div>
        </main>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@700;800&display=swap');

/* --- BASE & LAYOUT --- */
.executive-layout { font-family: 'Plus Jakarta Sans', sans-serif; display: flex; height: 100vh; background-color: #f8fafc; color: #1e293b; overflow: hidden; position: relative; }

/* THE MAGIC: ANIMATED GRADIENT ORBS (Executive Amethyst Theme) */
.dynamic-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 0; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.35; animation: float 20s infinite alternate cubic-bezier(0.4, 0, 0.2, 1); }
.orb-violet { width: 600px; height: 600px; background: #8b5cf6; top: -10%; left: -10%; }
.orb-amethyst { width: 700px; height: 700px; background: #6d28d9; bottom: -20%; right: -5%; animation-delay: -5s; opacity: 0.25; }
.orb-slate { width: 500px; height: 500px; background: #475569; top: 40%; left: 30%; animation-delay: -10s; opacity: 0.2; }

@keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, 50px) scale(1.1); } }

/* --- GLASSMORPHIC SIDEBAR --- */
.side-nav { width: 260px; background: rgba(255, 255, 255, 0.75); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border-right: 1px solid rgba(255, 255, 255, 0.8); display: flex; flex-direction: column; padding: 1.5rem 1.2rem; z-index: 30; box-shadow: 4px 0 24px rgba(0,0,0,0.02); }
.brand-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 3rem; cursor: default; padding-left: 0.5rem; }
.logo-mark { background: linear-gradient(135deg, #7c3aed, #4c1d95); color: white; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-weight: 800; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25); }
.logo-text { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }

.nav-links { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; }
.nav-section-title { font-size: 0.7rem; font-weight: 800; color: #94a3b8; letter-spacing: 1px; margin-bottom: 0.5rem; padding-left: 1rem; text-transform: uppercase; }
.nav-btn { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 1rem; border-radius: 12px; border: none; background: transparent; color: #64748b; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; text-align: left; }
.nav-icon { width: 20px; height: 20px; opacity: 0.8; }
.nav-btn:hover { color: #7c3aed; background: rgba(124, 58, 237, 0.05); }
.nav-btn.active { background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: #ffffff; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25); }
.nav-btn.active .nav-icon { opacity: 1; }

.sidebar-footer { padding: 1.5rem 0.5rem 0.5rem; border-top: 1px solid rgba(0,0,0,0.05); }
.btn-logout-sidebar { display: flex; align-items: center; gap: 0.8rem; color: #ef4444; background: transparent; border: none; font-size: 0.95rem; font-weight: 600; padding: 0.8rem 1rem; border-radius: 12px; transition: 0.2s; cursor: pointer; width: 100%; text-align: left;}
.btn-logout-sidebar:hover { background: rgba(239, 68, 68, 0.1); color: #dc2626; }

/* --- WORKSPACE & TOP NAV --- */
.workspace { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: transparent; position: relative; z-index: 10; }
.top-nav { height: 80px; background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255, 255, 255, 0.8); display: flex; justify-content: space-between; align-items: center; padding: 0 3rem; }
.date-display { display: flex; align-items: center; gap: 0.8rem; font-weight: 600; color: #475569; font-size: 0.95rem; }
.date-display svg { width: 20px; height: 20px; color: #7c3aed; }

/* DYNAMIC USER PROFILE */
.top-actions { display: flex; align-items: center; gap: 2rem; }
.icon-btn { background: none; border: none; position: relative; cursor: pointer; color: #64748b; padding: 0.5rem; border-radius: 50%; transition: 0.2s; }
.icon-btn:hover { background: rgba(0,0,0,0.05); color: #1e293b; }
.icon-btn svg { width: 22px; height: 22px; }
.notification-dot { position: absolute; top: 4px; right: 4px; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; border: 2px solid white; }

.user-profile { display: flex; align-items: center; gap: 1rem; cursor: pointer; padding-left: 1.5rem; border-left: 1px solid rgba(0,0,0,0.1); transition: 0.2s; }
.user-profile:hover { opacity: 0.8; }
.avatar-placeholder { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1rem; color: white; box-shadow: 0 4px 10px rgba(124, 58, 237, 0.2); border: 2px solid white; }
.admin-gradient { background: linear-gradient(135deg, #7c3aed, #4c1d95); }
.profile-text { display: flex; flex-direction: column; }
.user-name { font-weight: 700; font-size: 0.95rem; color: #1e293b; }
.profile-subtext { font-size: 0.75rem; color: #64748b; font-weight: 600; transition: 0.2s; }

.content-area { padding: 2rem 3rem; overflow-y: auto; flex: 1; }

/* --- HEADERS & GLASS CARDS --- */
.welcome-banner { margin-bottom: 2rem; padding: 1rem 0; }
.sofi-title { font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0 0 0.4rem 0; letter-spacing: -1px; }
.banner-dept { color: #7c3aed; font-weight: 700; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; margin:0; }

.glass-card { background: rgba(255, 255, 255, 0.75); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 20px; box-shadow: 0 15px 35px rgba(15, 23, 42, 0.04), inset 0 1px 0 white; }

/* --- TEMPORARY STYLING FOR EXISTING CONTENT (To be refined in Step 2 & 3) --- */
/* --- PREMIUM STAT CARDS (Tightened) --- */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card { padding: 1.2rem 1.5rem; display: flex; align-items: center; gap: 1.2rem; transition: 0.3s; }
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 20px 40px rgba(0,0,0,0.06), inset 0 1px 0 white; }
.stat-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.stat-icon svg { width: 22px; height: 22px; }
.icon-emerald { background: linear-gradient(135deg, #10b981, #34d399); color: white; }
.icon-violet { background: linear-gradient(135deg, #7c3aed, #8b5cf6); color: white; }
.icon-blue { background: linear-gradient(135deg, #2563eb, #60a5fa); color: white; }
.stat-info h3 { margin: 0 0 0.2rem 0; color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; }
.stat-number { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0; font-family: 'Outfit', sans-serif; line-height: 1; }

/* --- PREMIUM CHARTS (Strict Heights) --- */
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
.chart-card { padding: 0; overflow: hidden; display: flex; flex-direction: column; }
.card-header { padding: 1.2rem 1.5rem; }
.card-header h2 { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 0; }
.card-header .subtitle { color: #64748b; font-size: 0.85rem; margin: 0.2rem 0 0 0; }
.border-bottom { border-bottom: 1px solid rgba(0,0,0,0.05); }
/* The fix: Hardcoded height and removed flex: 1 */
.chart-wrapper { position: relative; height: 240px; width: 100%; display: flex; justify-content: center; padding: 0 1rem 1.5rem; }

/* --- PREMIUM DATA TABLES (Slimmer Padding) --- */
.p-0 { padding: 0 !important; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { padding: 1rem 1.5rem; font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; background: rgba(248, 250, 252, 0.5); border-bottom: 1px solid rgba(0,0,0,0.05); text-align: left; }
.data-table td { padding: 1rem 1.5rem; border-bottom: 1px solid rgba(0,0,0,0.03); color: #334155; font-weight: 500; transition: 0.2s; vertical-align: middle; font-size: 0.9rem; }
.data-table tbody tr:hover td { background: rgba(255, 255, 255, 0.6); }
.data-table strong { color: #0f172a; font-weight: 700; }
.font-mono { font-family: monospace; font-size: 0.9rem; }
.text-right { text-align: right !important; }

/* Badges */
.status-badge { padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block; }
.status-badge.booked { background: #dbeafe; color: #2563eb; }
.status-badge.completed { background: #dcfce7; color: #16a34a; }
.status-badge.cancelled { background: #fee2e2; color: #dc2626; }

/* Basic Table Styles for now */
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 1rem; border-bottom: 1px solid rgba(0,0,0,0.05); text-align: left; }
.data-table th { color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
.status-badge { padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: capitalize; }
.status-badge.booked { background: #dbeafe; color: #2563eb; }
.status-badge.completed { background: #dcfce7; color: #16a34a; }
.status-badge.cancelled { background: #fee2e2; color: #dc2626; }
.system-status { padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }
.system-status.active { background: #dcfce7; color: #16a34a; border: 1px solid #16a34a; }
.system-status.blacklisted { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }

/* --- PREMIUM FORMS --- */
.pro-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-row { display: flex; gap: 1.5rem; }
.half-width { flex: 1; }
.third-width { flex: 1; }
.form-group { display: flex; flex-direction: column; gap: 0.6rem; }
.form-group label { font-size: 0.8rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }

.pro-input { width: 100%; padding: 0.9rem 1.2rem; border: 1px solid #cbd5e1; border-radius: 10px; font-family: inherit; font-size: 0.95rem; color: #1e293b; background: rgba(255,255,255,0.8); transition: 0.2s; box-sizing: border-box; font-weight: 500; }
.pro-input:focus { outline: none; border-color: #7c3aed; background: #ffffff; box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15); }
.pro-input:disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; }

/* --- PREMIUM BUTTONS --- */
.form-actions-bar { display: flex; justify-content: flex-end; align-items: center; gap: 1.5rem; }
.btn-primary-violet { background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: white; border: none; padding: 0.9rem 2rem; border-radius: 10px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25); }
.btn-primary-violet:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(124, 58, 237, 0.35); }
.btn-primary-violet:disabled { opacity: 0.7; cursor: not-allowed; transform: none; box-shadow: none; }

.btn-outline-danger { background: transparent; border: 1px solid #fecaca; color: #ef4444; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: 0.2s; }
.btn-outline-danger:hover:not(:disabled) { background: #fef2f2; border-color: #ef4444; }
.btn-outline-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-outline-warning { background: transparent; border: 1px solid #fed7aa; color: #f97316; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: 0.2s; }
.btn-outline-warning:hover { background: #fff7ed; border-color: #f97316; }

.btn-outline-success { background: transparent; border: 1px solid #bbf7d0; color: #10b981; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: 0.2s; }
.btn-outline-success:hover { background: #f0fdf4; border-color: #10b981; }

/* Alerts & Messages */
.error-message { background: #fef2f2; color: #dc2626; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid #fecaca; font-weight: 600; font-size: 0.95rem; }
.success-message { background: #f0fdf4; color: #16a34a; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid #bbf7d0; font-weight: 600; font-size: 0.95rem; }

/* Utilities */
.loading-state { text-align: center; padding: 5rem; color: #64748b; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #7c3aed; border-radius: 50%; animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite; margin-bottom: 1.5rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-in-up { animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* --- CUSTOM UI DROPDOWN --- */
.custom-select-container { position: relative; width: 100%; }
.dropdown-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 40; cursor: default; }

.select-display { display: flex; justify-content: space-between; align-items: center; cursor: pointer; position: relative; z-index: 41; user-select: none; }
.select-display svg { width: 18px; height: 18px; color: #475569; transition: 0.3s; }
.select-display.is-active { border-color: #7c3aed; box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15); }
.select-display.is-active svg { transform: rotate(180deg); color: #7c3aed; }

.custom-options-list { position: absolute; top: calc(100% + 8px); left: 0; width: 100%; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(16px); border: 1px solid #cbd5e1; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); list-style: none; padding: 0.5rem 0; margin: 0; z-index: 42; max-height: 250px; overflow-y: auto; }
.custom-option { padding: 0.8rem 1.2rem; font-size: 0.95rem; color: #1e293b; cursor: pointer; transition: 0.2s; font-weight: 500; }
.custom-option:hover { background: #f3e8ff; color: #7c3aed; }
.custom-option.disabled { color: #94a3b8; cursor: default; }
.custom-option.disabled:hover { background: transparent; color: #94a3b8; }

</style>