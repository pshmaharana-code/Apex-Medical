<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios';

const authStore = useAuthStore()
const router = useRouter()

// --- STATE ---
const dashboardData = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const activeTab = ref('appointments') 

// State for the Schedule Builder
const isSavingSchedule = ref(false)
const scheduleMessage = ref('')
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const weeklySchedule = ref(daysOfWeek.map((day, index) => ({
    day_of_week: index,
    day_name: day,
    is_working: false,
    morning_start_time: '',
    morning_end_time: '',
    evening_start_time: '',
    evening_end_time: ''
})))

// CONSULTATION MODAL STATE
const showConsultModal = ref(false)
const currentAppointmentId = ref(null)
const consultForm = ref({ diagnosis: '', prescription: '', notes: ''})
const isSubmitting = ref(false)

const getLocalToday = () => {
    const d = new Date()
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}
const todayFormatted = ref(getLocalToday())

// --- METHODS ---
const fetchDashboard = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/doctor/dashboard', {
            headers: { Authorization: `Bearer ${authStore.token}` }
        })
        dashboardData.value = response.data

        if (response.data.availability_schedule) {
            response.data.availability_schedule.forEach(savedSlot => {
                const dayObj = weeklySchedule.value.find(d => d.day_of_week === savedSlot.day_of_week)
                if (dayObj) {
                    dayObj.morning_start_time = savedSlot.morning_start_time || ''
                    dayObj.morning_end_time = savedSlot.morning_end_time || ''
                    dayObj.evening_start_time = savedSlot.evening_start_time || ''
                    dayObj.evening_end_time = savedSlot.evening_end_time || ''
                    
                    if (dayObj.morning_start_time || dayObj.evening_start_time) {
                        dayObj.is_working = true
                    }
                }
            })
        }
    } catch (error) {
        console.error("Failed to load dashboard:", error)
        errorMessage.value = "Could not load dashboard data."
    } finally {
        isLoading.value = false
    }
}

const saveSchedule = async () => {
    isSavingSchedule.value = true
    scheduleMessage.value = ''
    
    const payload = weeklySchedule.value.map(day => ({
        day_of_week: day.day_of_week,
        morning_start_time: day.is_working ? day.morning_start_time : '',
        morning_end_time: day.is_working ? day.morning_end_time : '',
        evening_start_time: day.is_working ? day.evening_start_time : '',
        evening_end_time: day.is_working ? day.evening_end_time : ''
    }))

    try {
        await axios.post('http://127.0.0.1:5000/api/doctor/schedule', payload, {
            headers: { Authorization: `Bearer ${authStore.token}` }
        })
        scheduleMessage.value = "Schedule saved successfully!"
        setTimeout(() => scheduleMessage.value = '', 3000)
    } catch (error) {
        scheduleMessage.value = "Failed to save schedule. Please try again."
    } finally {
        isSavingSchedule.value = false
    }
}

// --- LEAVE MANAGEMENT ---
const leaves = ref([])
const newLeaveDate =  ref('')
const isSubmitingLeave = ref(false)

const fetchLeaves = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/doctor/leaves', {
            headers: { Authorization: `Bearer ${authStore.token}`}
        })
        leaves.value = response.data
    } catch (error) {
        console.error("Failed to fetch leaves", error)
    }
}

const submitLeave = async () => {
    if(!newLeaveDate.value) return;
    isSubmitingLeave.value = true;

    try {
        await axios.post('http://127.0.0.1:5000/api/doctor/leaves', {date: newLeaveDate.value}, {
            headers: { Authorization: `Bearer ${authStore.token}`}
        })
        newLeaveDate.value = ''
        fetchLeaves()
    } catch (error) {
        alert(error.response?.data?.msg || "Failed to schedule time off.")
    } finally {
        isSubmitingLeave.value = false;
    }
}

const handleLogout = () => {
    authStore.logout()  
    router.push('/login')   
}

const startConsultation = (appointmentId) => {
    currentAppointmentId.value = appointmentId
    consultForm.value = { diagnosis: '', prescription: '', notes: ''}
    showConsultModal.value = true
}

const closeConsultModal = () => {
    showConsultModal.value = false
    currentAppointmentId.value = null
}

const submitConsultation = async () => {
    isSubmitting.value = true
    try {
        await axios.post(`http://127.0.0.1:5000/api/doctor/appointment/${currentAppointmentId.value}/consult`, consultForm.value, {
            headers: {Authorization: `Bearer ${authStore.token}`}
        })
        closeConsultModal()
        fetchDashboard() 
    } catch(error) {
        alert("Failed to save consultation. Please check your connection.")
    } finally {
        isSubmitting.value = false
    }
}

const showHistoryModal = ref(false)
const patientHistoryData = ref(null)
const isHistoryLoading = ref(false)

const viewPatientHistory = async (patientId) => {
    showHistoryModal.value = true
    isHistoryLoading.value = true
    patientHistoryData.value = null

    try {
        const response = await axios.get(`http://127.0.0.1:5000/api/doctor/patient/${patientId}/history`, {
            headers: { Authorization: `Bearer ${authStore.token}` }
        })
        patientHistoryData.value = response.data
    } catch (error) {
        alert("Failed to load patient history or permission denied.")
        showHistoryModal.value = false
    } finally {
        isHistoryLoading.value = false
    }
}
const closeHistoryModal = () => { showHistoryModal.value = false }


const fetchProfilePic = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/doctor/profile', {
            headers: { Authorization: `Bearer ${authStore.token}` }
        })
        if (authStore.user) {
            authStore.user.profile_picture = response.data.profile_picture
        }
    } catch (error) {
        console.error("Failed to load profile picture:", error)
    }
}


// --- LIVE RADIO RECEIVER (SSE) ---
const setupLiveUpdates = () => {
    // 1. Get this specific doctor's ID from the JWT token in authStore
    const userId = authStore.user?.id;
    
    if (!userId) return;

    // 2. Tune the radio to this doctor's specific channel
    const eventSource = new EventSource(`http://127.0.0.1:5000/stream?channel=user_${userId}`);

    // 3. Listen for the 'new_appointment' signal
    eventSource.addEventListener('new_appointment', (event) => {
        const data = JSON.parse(event.data);
        console.log("LIVE UPDATE RECEIVED:", data.message);
        
        // 4. Instantly refresh the dashboard data without reloading the page!
        fetchDashboard(); 
    });

    // Handle connection errors gracefully
    eventSource.onerror = (error) => {
        console.error("SSE connection lost. Reconnecting...", error);
    };
}

onMounted(() => {
    fetchDashboard()
    fetchLeaves()
    fetchProfilePic()
    setupLiveUpdates()
})
</script>

<template>
    <div class="premium-layout">
        
        <div class="dynamic-bg">
            <div class="orb orb-blue"></div>
            <div class="orb orb-indigo"></div>
            <div class="orb orb-sky"></div>
        </div>

        <aside class="side-nav glass-panel">
            <div class="brand-header">
                <div class="logo-mark provider-gradient">Rx</div>
                <span class="logo-text">Apex Provider</span>
            </div>

            <nav class="nav-links">
                <div class="nav-section-title">CLINICAL</div>
                <button :class="['nav-btn', { active: activeTab === 'appointments' }]" @click="activeTab = 'appointments'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    Today's Patients
                </button>
                
                <div class="nav-section-title mt-4">MANAGEMENT</div>
                <button :class="['nav-btn', { active: activeTab === 'schedule' }]" @click="activeTab = 'schedule'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    Master Schedule
                </button>
                <button :class="['nav-btn', { active: activeTab === 'leaves' }]" @click="activeTab = 'leaves'">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                    Time Off & Leaves
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
                    <div class="user-profile" @click="$router.push('/doctor-profile')">
                        <img v-if="authStore.user?.profile_picture" 
                             :src="`http://127.0.0.1:5000${authStore.user.profile_picture}`" 
                             alt="Profile" class="avatar-placeholder img-cover" />
                        <div v-else class="avatar-placeholder provider-gradient">
                            {{ dashboardData?.doctor_name ? dashboardData.doctor_name.charAt(0).toUpperCase() : 'D' }}
                        </div>
                        <div class="profile-text">
                            <span class="user-name">Dr. {{ dashboardData?.doctor_name || 'Loading' }}</span>
                            <span class="profile-subtext">Manage Profile</span>
                        </div>
                    </div>
                </div>
            </header>

            <div v-if="isLoading" class="content-area loading-state">
                <div class="spinner"></div><p>Syncing secure medical records...</p>
            </div>
            
            <div v-else-if="errorMessage" class="content-area error-message">
                {{ errorMessage }}
            </div>

            <div v-else class="content-area">

                <div class="welcome-banner fade-in-up">
                    <div class="banner-content">
                        <h1 class="sofi-title">Welcome back, Dr. {{ dashboardData.doctor_name }}</h1>
                        <p class="banner-dept">{{ dashboardData.department || 'General Practice' }} Department</p>
                    </div>
                </div>

                <div v-if="activeTab === 'appointments'" class="fade-in-up delay-1">
                    
                    <div class="data-card glass-card">
                        <div class="card-header">
                            <h2>Today's Consultation Queue</h2>
                        </div>

                        <table class="clinical-table" v-if="dashboardData.upcoming_appointments.length > 0">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Patient</th>
                                    <th>Status</th>
                                    <th class="text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="appt in dashboardData.upcoming_appointments" :key="appt.id" :class="{'row-active': appt.date === todayFormatted}">
                                    <td>
                                        <div class="datetime">
                                            <strong>{{ appt.time }}</strong>
                                            <span>{{ appt.date }}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="patient-cell">
                                            <div class="patient-avatar">{{ appt.patient_name.charAt(0) }}</div>
                                            <strong>{{ appt.patient_name }}</strong>
                                        </div>
                                    </td>
                                    <td>
                                        <span v-if="appt.date === todayFormatted" class="status-badge badge-blue">Ready</span>
                                        <span v-else class="status-badge badge-gray">Upcoming</span>
                                    </td>
                                    <td class="text-right action-cell">
                                        <button @click="viewPatientHistory(appt.patient_id)" class="btn-icon" title="View History">
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                                        </button>
                                        <button v-if="appt.date === todayFormatted" @click="startConsultation(appt.id)" class="btn-primary-blue">Start Consult</button>
                                        <button v-else class="btn-disabled" disabled>Scheduled</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div v-else class="empty-state">
                            <svg class="empty-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
                            <h3>Queue is Clear</h3>
                            <p>You have no pending consultations for today.</p>
                        </div>
                    </div>
                </div>

                <div v-if="activeTab === 'schedule'" class="fade-in-up delay-1">
                    <div class="data-card glass-card p-0">
                        <div class="card-header border-bottom">
                            <h2>Weekly Master Roster</h2>
                            <p class="subtitle">Set your availability. The patient booking engine syncs with this data.</p>
                        </div>

                        <form @submit.prevent="saveSchedule" class="schedule-form">
                            <div v-for="day in weeklySchedule" :key="day.day_of_week" class="day-row">
                                
                                <div class="day-toggle">
                                    <label class="switch">
                                        <input type="checkbox" v-model="day.is_working">
                                        <span class="slider round"></span>
                                    </label>
                                    <span class="day-name" :class="{ 'text-disabled': !day.is_working }">{{ day.day_name }}</span>
                                </div>

                                <div class="time-inputs" v-if="day.is_working">
                                    <div class="shift-block">
                                        <label>Morning Shift</label>
                                        <div class="time-group">
                                            <input type="time" v-model="day.morning_start_time" class="pro-input">
                                            <span class="to-text">-</span>
                                            <input type="time" v-model="day.morning_end_time" class="pro-input">
                                        </div>
                                    </div>
                                    <div class="shift-block">
                                        <label>Evening Shift</label>
                                        <div class="time-group">
                                            <input type="time" v-model="day.evening_start_time" class="pro-input">
                                            <span class="to-text">-</span>
                                            <input type="time" v-model="day.evening_end_time" class="pro-input">
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="off-badge">Unavailable</div>
                            </div>

                            <div class="form-actions-bar">
                                <span v-if="scheduleMessage" :class="['alert-msg', scheduleMessage.includes('success') ? 'text-green' : 'text-red']">
                                    {{ scheduleMessage }}
                                </span>
                                <button type="submit" class="btn-primary-blue" :disabled="isSavingSchedule">
                                    {{ isSavingSchedule ? 'Syncing...' : 'Save Master Schedule' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div v-if="activeTab === 'leaves'" class="fade-in-up delay-1">
                    <div class="leaves-grid">
                        <div class="data-card glass-card">
                            <form @submit.prevent="submitLeave" class="leave-form">
                                <h3 class="mb-4">Schedule Time Off</h3>
                                <div class="form-group">
                                    <label>Select Date</label>
                                    <input type="date" v-model="newLeaveDate" :min="todayFormatted" class="pro-input" required>
                                </div>
                                <button type="submit" class="btn-primary-blue w-100 mt-4" :disabled="isSubmitingLeave">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                                    {{ isSubmitingLeave ? 'Blocking...' : 'Block Date from Booking' }}
                                </button>
                            </form>
                        </div>

                        <div class="data-card glass-card">
                            <h3 class="mb-4">Upcoming Blocked Dates</h3>
                            <ul v-if="leaves.length > 0" class="leave-list">
                                <li v-for="leave in leaves" :key="leave.id" class="leave-item">
                                    <span class="leave-date">{{ leave.date }}</span>
                                    <span class="status-badge badge-orange">Unavailable</span>
                                </li>
                            </ul>
                            <div v-else class="empty-state-small">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                                <p>No upcoming time off scheduled.</p>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </main>

        <div v-if="showConsultModal" class="modal-overlay">
            <div class="modal-card fade-in-up">
                <div class="modal-header">
                    <h3>Patient Consultation</h3>
                    <button @click="closeConsultModal" class="close-btn">&times;</button>
                </div>
                <form @submit.prevent="submitConsultation" class="pro-form">
                    <div class="form-group">
                        <label>Diagnosis <span class="text-red">*</span></label>
                        <input type="text" v-model="consultForm.diagnosis" class="pro-input" required placeholder="e.g., Viral Fever">
                    </div>
                    <div class="form-group">
                        <label>Prescription <span class="text-red">*</span></label>
                        <textarea v-model="consultForm.prescription" class="pro-input" required placeholder="e.g., Paracetamol 500mg, 1x a day" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Additional Notes</label>
                        <textarea v-model="consultForm.notes" class="pro-input" placeholder="e.g., Drink plenty of fluids and rest." rows="2"></textarea>
                    </div>
                    <div class="modal-actions">
                        <button type="button" @click="closeConsultModal" class="btn-outline-slate">Cancel</button>
                        <button type="submit" class="btn-primary-blue" :disabled="isSubmitting">
                            {{ isSubmitting ? 'Saving...' : 'Finalize & Save Record' }}  
                        </button>
                    </div> 
                </form>
            </div>
        </div>

        <div v-if="showHistoryModal" class="modal-overlay">
            <div class="modal-card history-modal fade-in-up">
                <div class="modal-header">
                    <h3>Patient Medical Records</h3>
                    <button @click="closeHistoryModal" class="close-btn">&times;</button>
                </div>

                <div v-if="isHistoryLoading" class="loading-state"><div class="spinner"></div></div>

                <div v-else-if="patientHistoryData">
                    <div class="patient-profile-bar">
                        <div class="profile-stat"><span>Name</span><strong>{{ patientHistoryData.patient_name }}</strong></div>
                        <div class="profile-stat"><span>Age</span><strong>{{ patientHistoryData.patient_age }}</strong></div>
                        <div class="profile-stat"><span>Blood Group</span><strong>{{ patientHistoryData.patient_blood_group || 'Unknown' }}</strong></div>
                    </div>

                    <div v-if="patientHistoryData.history.length > 0" class="history-list">
                        <div v-for="(record, index) in patientHistoryData.history" :key="index" class="history-card">
                            <div class="record-header">
                                <span class="record-date">{{ record.date }}</span>
                                <span class="record-doc">Dr. {{ record.consulting_doctor }}</span>
                            </div>
                            <div class="record-body">
                                <p><strong>Diagnosis:</strong> {{ record.diagnosis }}</p>
                                <p><strong>Rx:</strong> {{ record.prescription }}</p>
                                <p v-if="record.notes"><strong>Notes:</strong> {{ record.notes }}</p>                           
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-state-small mt-4">
                        <p>No past medical history found in the database.</p>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@700;800&display=swap');

/* --- BASE & LAYOUT --- */
.premium-layout { font-family: 'Plus Jakarta Sans', sans-serif; display: flex; height: 100vh; background-color: #f8fafc; color: #1e293b; overflow: hidden; position: relative; }

/* THE MAGIC: ANIMATED GRADIENT ORBS (Provider Blue Theme) */
.dynamic-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 0; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.4; animation: float 20s infinite alternate cubic-bezier(0.4, 0, 0.2, 1); }
.orb-blue { width: 600px; height: 600px; background: #3b82f6; top: -10%; left: -10%; }
.orb-indigo { width: 700px; height: 700px; background: #6366f1; bottom: -20%; right: -5%; animation-delay: -5s; opacity: 0.3; }
.orb-sky { width: 500px; height: 500px; background: #0ea5e9; top: 40%; left: 30%; animation-delay: -10s; opacity: 0.2; }

@keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, 50px) scale(1.1); } }

/* --- GLASSMORPHIC SIDEBAR --- */
.side-nav { width: 260px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border-right: 1px solid rgba(255, 255, 255, 0.8); display: flex; flex-direction: column; padding: 1.5rem 1.2rem; z-index: 30; box-shadow: 4px 0 24px rgba(0,0,0,0.02); }
.brand-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 3rem; cursor: pointer; padding-left: 0.5rem; }
.logo-mark { background: linear-gradient(135deg, #2563eb, #60a5fa); color: white; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-weight: 800; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); }
.logo-text { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }

.nav-links { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; }
.nav-section-title { font-size: 0.7rem; font-weight: 800; color: #94a3b8; letter-spacing: 1px; margin-bottom: 0.5rem; padding-left: 1rem; text-transform: uppercase; }
.nav-btn { display: flex; align-items: center; gap: 1rem; padding: 0.9rem 1rem; border-radius: 12px; border: none; background: transparent; color: #64748b; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; text-align: left; }
.nav-icon { width: 20px; height: 20px; opacity: 0.8; }
.nav-btn:hover { color: #2563eb; background: rgba(37, 99, 235, 0.05); }
.nav-btn.active { background: linear-gradient(135deg, #2563eb, #3b82f6); color: #ffffff; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25); }
.nav-btn.active .nav-icon { opacity: 1; }

.sidebar-footer { padding: 1.5rem 0.5rem 0.5rem; border-top: 1px solid rgba(0,0,0,0.05); }
/* Replace .btn-profile-sidebar and .btn-logout with this: */
.btn-logout-sidebar { display: flex; align-items: center; gap: 0.8rem; color: #ef4444; background: transparent; border: none; font-size: 0.95rem; font-weight: 600; padding: 0.8rem 1rem; border-radius: 12px; transition: 0.2s; cursor: pointer; width: 100%; }
.btn-logout-sidebar:hover { background: rgba(239, 68, 68, 0.1); color: #dc2626; }

/* --- WORKSPACE & TOP NAV --- */
.workspace { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: transparent; position: relative; z-index: 10; }
.top-nav { height: 80px; background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255, 255, 255, 0.8); display: flex; justify-content: space-between; align-items: center; padding: 0 3rem; }
.date-display { display: flex; align-items: center; gap: 0.8rem; font-weight: 600; color: #475569; font-size: 0.95rem; }
.date-display svg { width: 20px; height: 20px; color: #2563eb; }

/* DYNAMIC USER PROFILE */
.top-actions { display: flex; align-items: center; gap: 2rem; }
.icon-btn { background: none; border: none; position: relative; cursor: pointer; color: #64748b; padding: 0.5rem; border-radius: 50%; transition: 0.2s; }
.icon-btn:hover { background: rgba(0,0,0,0.05); color: #1e293b; }
.icon-btn svg { width: 22px; height: 22px; }
.notification-dot { position: absolute; top: 4px; right: 4px; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; border: 2px solid white; }

.user-profile { display: flex; align-items: center; gap: 1rem; cursor: pointer; padding-left: 1.5rem; border-left: 1px solid rgba(0,0,0,0.1); transition: 0.2s; }
.user-profile:hover { opacity: 0.8; }
.avatar-placeholder { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1rem; color: white; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2); border: 2px solid white; }
.provider-gradient { background: linear-gradient(135deg, #2563eb, #60a5fa); }
.img-cover { object-fit: cover; }
.profile-text { display: flex; flex-direction: column; }
.user-name { font-weight: 700; font-size: 0.95rem; color: #1e293b; }
/* Replace .logout-text with this: */
.profile-subtext { font-size: 0.75rem; color: #64748b; font-weight: 600; transition: 0.2s; }
.user-profile:hover .profile-subtext { color: #2563eb; }

.content-area { padding: 2rem 3rem; overflow-y: auto; flex: 1; }

/* --- HEADERS & CARDS --- */
.welcome-banner { margin-bottom: 2rem; padding: 1rem 0; }
.sofi-title { font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0 0 0.4rem 0; letter-spacing: -1px; }
.banner-dept { color: #2563eb; font-weight: 700; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }

.card-header { padding: 1.5rem 2rem; border-bottom: 1px solid rgba(0,0,0,0.05); }
.card-header h2 { font-size: 1.3rem; font-weight: 800; color: #0f172a; margin: 0; }
.card-header .subtitle { color: #64748b; font-size: 0.9rem; margin: 0.4rem 0 0 0; }

.glass-card { background: rgba(255, 255, 255, 0.75); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 20px; box-shadow: 0 15px 35px rgba(15, 23, 42, 0.04), inset 0 1px 0 white; margin-bottom: 2rem; overflow: hidden; }
.p-0 { padding: 0; }
.mt-3 { margin-top: 1.5rem; }
.mt-4 { margin-top: 2rem; }
.mb-4 { margin-bottom: 1.5rem; }
.w-100 { width: 100%; }

/* --- TABLES --- */
.clinical-table { width: 100%; border-collapse: collapse; }
.clinical-table th { text-align: left; padding: 1.2rem 2rem; font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; background: rgba(248, 250, 252, 0.5); border-bottom: 1px solid rgba(0,0,0,0.05); }
.clinical-table td { padding: 1.2rem 2rem; border-bottom: 1px solid rgba(0,0,0,0.03); vertical-align: middle; color: #334155; }
.row-active { background: rgba(255, 255, 255, 0.9); box-shadow: inset 4px 0 0 #2563eb; }

.datetime strong { display: block; color: #0f172a; font-weight: 800; font-size: 1.05rem; }
.datetime span { font-size: 0.8rem; color: #64748b; font-weight: 600; }
.patient-cell { display: flex; align-items: center; gap: 1rem; }
.patient-avatar { width: 36px; height: 36px; background: #e2e8f0; color: #475569; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; }
.patient-cell strong { font-weight: 700; color: #0f172a; font-size: 1.05rem; }

.status-badge { padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.badge-orange { background: #fee2e2; color: #b91c1c; }
.badge-blue { background: #dbeafe; color: #2563eb; }
.badge-gray { background: #f1f5f9; color: #64748b; }

.text-right { text-align: right !important; }
.action-cell { display: flex; gap: 0.8rem; justify-content: flex-end; align-items: center; }

/* --- BUTTONS & INPUTS --- */
.btn-primary-blue { background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 10px; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 12px rgba(37,99,235,0.25); display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.btn-primary-blue:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(37,99,235,0.35); }
.btn-primary-blue:disabled { opacity: 0.6; cursor: not-allowed; box-shadow: none; transform: none; }

.btn-outline-slate { background: white; border: 1px solid #cbd5e1; color: #475569; padding: 0.8rem 1.5rem; border-radius: 10px; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: 0.2s; }
.btn-outline-slate:hover { border-color: #0f172a; color: #0f172a; background: #f8fafc; }

.btn-icon { background: #f1f5f9; border: none; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #475569; cursor: pointer; transition: 0.2s; }
.btn-icon:hover { background: #e2e8f0; color: #0f172a; }
.btn-icon svg { width: 18px; height: 18px; }

.btn-disabled { background: #f1f5f9; color: #94a3b8; border: 1px dashed #cbd5e1; padding: 0.8rem 1.5rem; border-radius: 10px; font-weight: 700; font-size: 0.95rem; cursor: not-allowed; }

.pro-input { width: 100%; padding: 0.9rem 1.2rem; border: 1px solid #cbd5e1; border-radius: 10px; font-family: inherit; font-size: 0.95rem; color: #1e293b; background: rgba(255,255,255,0.8); transition: 0.2s; box-sizing: border-box; font-weight: 500; }
.pro-input:focus { outline: none; border-color: #2563eb; background: #ffffff; box-shadow: 0 0 0 3px rgba(37,99,235,0.15); }

/* --- SCHEDULE BUILDER --- */
.day-row { display: flex; align-items: center; padding: 1.5rem 2rem; border-bottom: 1px solid rgba(0,0,0,0.03); gap: 3rem; transition: 0.2s; }
.day-row:hover { background: rgba(255,255,255,0.5); }
.day-toggle { width: 180px; display: flex; align-items: center; gap: 12px; }
.day-name { font-weight: 800; font-size: 1.05rem; color: #1e293b; transition: 0.2s; }
.text-disabled { color: #94a3b8; text-decoration: line-through; }
.off-badge { background: #f1f5f9; color: #94a3b8; padding: 0.5rem 1.2rem; border-radius: 10px; font-weight: 800; font-size: 0.85rem; margin-left: auto; border: 1px dashed #cbd5e1; }

.time-inputs { display: flex; gap: 3rem; flex: 1; flex-wrap: wrap; }
.shift-block { display: flex; flex-direction: column; gap: 0.6rem; }
.shift-block label { font-size: 0.75rem; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.time-group { display: flex; align-items: center; gap: 12px; }
.to-text { color: #94a3b8; font-size: 0.9rem; font-weight: 700; }
.form-actions-bar { padding: 1.5rem 2rem; display: flex; justify-content: flex-end; align-items: center; gap: 1.5rem; background: rgba(248, 250, 252, 0.5); border-top: 1px solid rgba(0,0,0,0.05); }

/* Toggle Switch CSS */
.switch { position: relative; display: inline-block; width: 48px; height: 26px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .3s; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px; background-color: white; transition: .3s; }
input:checked + .slider { background: linear-gradient(135deg, #2563eb, #3b82f6); }
input:checked + .slider:before { transform: translateX(22px); }
.slider.round { border-radius: 34px; }
.slider.round:before { border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }

/* --- LEAVES --- */
.leaves-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.leave-form h3, .glass-card h3 { font-size: 1.2rem; font-weight: 800; color: #0f172a; margin: 0; padding: 2rem 2rem 0; }
.leave-form .form-group { padding: 0 2rem 2rem; }
.leave-list { list-style: none; padding: 0 2rem 2rem; margin: 0; display: flex; flex-direction: column; gap: 1rem; }
.leave-item { border: 1px solid rgba(0,0,0,0.05); padding: 1.2rem 1.5rem; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.8); box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
.leave-date { font-weight: 800; color: #1e293b; font-size: 1.05rem; }

/* --- MODALS --- */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-card { background: #ffffff; padding: 3rem; border-radius: 24px; width: 100%; max-width: 600px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
.history-modal { max-width: 800px; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.modal-header h3 { margin: 0; color: #0f172a; font-size: 1.5rem; font-weight: 800; }
.close-btn { background: #f1f5f9; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.5rem; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
.close-btn:hover { background: #fee2e2; color: #ef4444; }

.pro-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-weight: 800; color: #334155; font-size: 0.9rem; }
.text-red { color: #ef4444; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }

/* Patient History Inside Modal */
.patient-profile-bar { display: flex; gap: 3rem; background: #f8fafc; padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid #e2e8f0; }
.profile-stat { display: flex; flex-direction: column; gap: 0.3rem; }
.profile-stat span { font-size: 0.75rem; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.profile-stat strong { font-size: 1.2rem; color: #0f172a; }

.history-list { display: flex; flex-direction: column; gap: 1.5rem; overflow-y: auto; padding-right: 0.5rem; }
.history-card { border: 1px solid #e2e8f0; padding: 2rem; border-radius: 16px; background: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }
.record-header { display: flex; justify-content: space-between; border-bottom: 1px dashed #cbd5e1; padding-bottom: 1rem; margin-bottom: 1rem; }
.record-date { font-weight: 800; color: #2563eb; font-size: 1.1rem; }
.record-doc { color: #64748b; font-size: 0.95rem; font-weight: 600; }
.record-body p { margin: 0 0 0.8rem 0; color: #334155; font-size: 1rem; line-height: 1.6; }
.record-body strong { color: #0f172a; font-weight: 800; }

.empty-state, .empty-state-small { text-align: center; color: #64748b; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-state { padding: 5rem 2rem; }
.empty-state h3 { color: #0f172a; font-size: 1.4rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.empty-state-small { padding: 3rem; background: rgba(248, 250, 252, 0.5); border-radius: 16px; border: 1px dashed rgba(0,0,0,0.1); margin: 0 2rem 2rem; }
.empty-state-small p { margin: 0; font-weight: 600; margin-top: 1rem; }
.empty-svg { width: 80px; height: 80px; color: #cbd5e1; margin-bottom: 1.5rem; }
.empty-state-small svg { width: 48px; height: 48px; color: #cbd5e1; }

.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite; margin: 0 auto 1.5rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-in-up { animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }
.delay-1 { animation-delay: 0.1s; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); filter: blur(4px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }
</style>