<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// --- IMPORT OUR REUSABLE ENGINE! ---
import ImageCropperModal from '@/components/ImageCropperModal.vue'

const authStore = useAuthStore()
const router = useRouter()

// --- PROFILE STATE ---
const profile = ref({ name: '', contact: '', qualification: '', experience: null, bio: '', profile_picture: null, consultation_fee: 500 })
const isLoading = ref(true)
const updateMessage = ref('')

// --- MEDIA UPLOAD STATE ---
const fileInput = ref(null) 
const isUploading = ref(false)
const uploadError = ref('')
const showCropModal = ref(false)
const imageSource = ref(null)
const imageTimestamp = ref(Date.now()) // The Cache-Buster!

// Dynamic image URL helper - uses cloud URL in production, local in dev
const getImageUrl = (imagePath) => {
    if (!imagePath) return '/default-avatar.png';
    const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
    return `${baseUrl}${imagePath}`;
};

const fetchProfile = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/api/doctor/profile', { 
            headers: { Authorization: `Bearer ${authStore.token}` } 
        })
        profile.value = response.data
    } catch (error) { 
        console.error(error)
    } finally { 
        isLoading.value = false 
    }
}

const updateProfile = async () => {
    updateMessage.value = "Saving..."
    try {
        await axios.put('http://127.0.0.1:5000/api/doctor/profile', profile.value, { 
            headers: { Authorization: `Bearer ${authStore.token}` } 
        })
        
        // Keep global store synced with updated name
        if (authStore.user) authStore.user.username = profile.value.name

        updateMessage.value = "Profile updated successfully."
        setTimeout(() => updateMessage.value = '', 3000)
    } catch (error) {
        updateMessage.value = "Failed to update profile."
    }
}

// ==========================================
// THE CROPPER LOGIC (WITH GLOBAL SYNC)
// ==========================================
const triggerFileInput = () => { fileInput.value.click() }

const onFileSelect = (event) => {
    const file = event.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
        imageSource.value = e.target.result 
        showCropModal.value = true          
    }
    reader.readAsDataURL(file)
    event.target.value = '' 
}

const handleCroppedImage = async (blob) => {
    isUploading.value = true
    uploadError.value = ''

    const formData = new FormData()
    formData.append('file', blob, 'profile_pic.jpg')

    try {
        const response = await axios.post('http://127.0.0.1:5000/api/doctor/profile/picture', formData, {
            headers: { Authorization: `Bearer ${authStore.token}`, 'Content-Type': 'multipart/form-data' }
        })
        
        // 1. Update local component
        profile.value.profile_picture = response.data.picture_url
        imageTimestamp.value = Date.now()
        
        // 2. CRITICAL: Update global Pinia store so Dashboard top-nav instantly updates!
        if (authStore.user) {
            authStore.user.profile_picture = response.data.picture_url
        }
        
        showCropModal.value = false 
        updateMessage.value = "Profile picture updated globally!"
        setTimeout(() => updateMessage.value = '', 3000)
    } catch (error) {
        uploadError.value = error.response?.data?.msg || "Failed to upload picture."
    } finally {
        isUploading.value = false
    }
}

const handleLogout = () => {
    authStore.logout()  
    router.push('/login')   
}

onMounted(() => { fetchProfile() })
</script>

<template>
    <div class="premium-layout">
        
        <div class="dynamic-bg">
            <div class="orb orb-blue"></div>
            <div class="orb orb-indigo"></div>
            <div class="orb orb-sky"></div>
        </div>

        <aside class="side-nav glass-panel">
            <div class="brand-header" @click="router.push('/doctor-dashboard')">
                <img src="@/assets/apex-logo2.png" alt="ApexMedical Logo" class="w-auto object-contain" style="height: 80px;" />
                <span class="logo-text">Apex Provider</span>
            </div>

            <nav class="nav-links">
                <router-link to="/doctor-dashboard" class="btn-back-sidebar">
                    &larr; Back to Dashboard
                </router-link>
            </nav>

            <div class="sidebar-footer">
                <button @click="handleLogout" class="btn-logout-sidebar">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    Secure Logout
                </button>
            </div>
        </aside>

        <main class="workspace">
            <header class="page-header">
                <div class="header-content">
                    <h1 class="sofi-title">Professional Profile</h1>
                    <p>Manage your public directory details and consultation fees.</p>
                </div>
            </header>

            <div class="content-area">
                
                <div v-if="isLoading" class="loading-state glass-card">
                    <div class="spinner"></div><p>Loading profile data...</p>
                </div>
                
                <div v-else class="glass-card main-form-card fade-in-up">
                    
                    <div class="avatar-section">
                        <div class="avatar-wrapper">
                            <img v-if="profile.profile_picture" 
                                 :src="`${getImageUrl(profile.profile_picture)}?t=${imageTimestamp}`" 
                                 alt="Profile" class="profile-img">
                            <div v-else class="avatar-placeholder provider-gradient">
                                {{ profile.name ? profile.name.charAt(0).toUpperCase() : 'Dr.' }}
                            </div>
                        </div>
                        
                        <div class="avatar-actions">
                            <h3>Profile Photo</h3>
                            <p class="sub-text">This will be displayed on your dashboard and to patients booking your slots. PNG or JPG.</p>
                            <input type="file" ref="fileInput" @change="onFileSelect" accept="image/png, image/jpeg, image/webp" style="display: none;">
                            <button type="button" class="btn-outline-slate" @click="triggerFileInput" :disabled="isUploading">
                                {{ isUploading ? 'Uploading...' : 'Change Picture' }}
                            </button>
                            <span v-if="uploadError" class="text-red mt-2" style="display:block; font-size:0.8rem;">{{ uploadError }}</span>
                        </div>
                    </div>

                    <hr class="divider">

                    <form @submit.prevent="updateProfile" class="pro-form">
                        
                        <div class="form-section">
                            <h3 class="section-title">Public Directory Details</h3>
                            
                            <div class="form-row">
                                <div class="form-group half-width">
                                    <label>Display Name</label>
                                    <input type="text" v-model="profile.name" class="pro-input" required />
                                </div>
                                <div class="form-group half-width">
                                    <label>Contact Number</label>
                                    <input type="text" v-model="profile.contact" class="pro-input" />
                                </div>
                            </div>

                            <div class="form-row">
                                <div class="form-group half-width">
                                    <label>Qualifications (Degrees)</label>
                                    <input type="text" v-model="profile.qualification" class="pro-input" placeholder="e.g., MBBS, MD" />
                                </div>
                                <div class="form-group half-width">
                                    <label>Years of Experience</label>
                                    <input type="number" v-model="profile.experience" class="pro-input" placeholder="e.g., 10" />
                                </div>
                            </div>

                            <div class="form-group mt-3">
                                <label>Professional Bio</label>
                                <textarea v-model="profile.bio" class="pro-input" rows="4" placeholder="Briefly describe your specialties and background..."></textarea>
                            </div>
                        </div>

                        <div class="form-section fee-section mt-4">
                            <div class="fee-header">
                                <h3 class="section-title m-0">Consultation Settings</h3>
                                <p class="sub-text">Set the price patients will be charged via Razorpay when booking your slots.</p>
                            </div>
                            
                            <div class="fee-input-wrapper">
                                <span class="currency-symbol">₹</span>
                                <input type="number" v-model="profile.consultation_fee" min="0" step="50" class="pro-input fee-input" required />
                            </div>
                        </div>

                        <div class="form-actions-bar">
                            <span v-if="updateMessage" :class="['alert-msg', updateMessage.includes('success') ? 'text-green' : 'text-red']">
                                {{ updateMessage }}
                            </span>
                            <button type="submit" class="btn-primary-blue">Save Public Profile</button>
                        </div>

                    </form>
                </div>
            </div>
        </main>

        <ImageCropperModal 
            :show="showCropModal"
            :imageSource="imageSource"
            :isUploading="isUploading"
            @close="showCropModal = false"
            @crop="handleCroppedImage"
        />

    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@700;800&display=swap');

/* --- BASE & LAYOUT --- */
.premium-layout { font-family: 'Plus Jakarta Sans', sans-serif; display: flex; height: 100vh; background-color: #f8fafc; color: #1e293b; overflow: hidden; position: relative; }

/* THE MAGIC: ANIMATED GRADIENT ORBS */
.dynamic-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 0; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.4; animation: float 20s infinite alternate cubic-bezier(0.4, 0, 0.2, 1); }
.orb-blue { width: 600px; height: 600px; background: #3b82f6; top: -10%; left: -10%; }
.orb-indigo { width: 700px; height: 700px; background: #6366f1; bottom: -20%; right: -5%; animation-delay: -5s; opacity: 0.3; }
.orb-sky { width: 500px; height: 500px; background: #0ea5e9; top: 40%; left: 30%; animation-delay: -10s; opacity: 0.2; }

@keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, 50px) scale(1.1); } }

/* --- SIDEBAR --- */
.side-nav { width: 260px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border-right: 1px solid rgba(255, 255, 255, 0.8); display: flex; flex-direction: column; padding: 1.5rem 1.2rem; z-index: 30; box-shadow: 4px 0 24px rgba(0,0,0,0.02); }
.brand-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 3rem; cursor: pointer; padding-left: 0.5rem; }
.logo-mark { background: linear-gradient(135deg, #2563eb, #60a5fa); color: white; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-weight: 800; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); }
.logo-text { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }
.nav-links { flex: 1; }
.btn-back-sidebar { display: block; padding: 1rem; text-align: center; background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(0, 0, 0, 0.05); border-radius: 12px; color: #1e293b; font-weight: 700; text-decoration: none; transition: 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
.btn-back-sidebar:hover { background: #ffffff; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.1); color: #2563eb; }
.sidebar-footer { padding: 1.5rem 0.5rem 0.5rem; border-top: 1px solid rgba(0,0,0,0.05); }
.btn-logout-sidebar { display: flex; align-items: center; gap: 0.8rem; color: #ef4444; background: transparent; border: none; font-size: 0.95rem; font-weight: 600; padding: 0.8rem 1rem; border-radius: 12px; transition: 0.2s; cursor: pointer; width: 100%; }
.btn-logout-sidebar:hover { background: rgba(239, 68, 68, 0.1); color: #dc2626; }
.nav-icon { width: 20px; height: 20px; }

/* --- WORKSPACE --- */
.workspace { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: transparent; position: relative; z-index: 10; }
.page-header { padding: 3rem 3rem 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; }
.sofi-title { font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0 0 0.4rem 0; letter-spacing: -1px; }
.page-header p { color: #64748b; margin: 0; font-size: 1rem; font-weight: 500; }
.content-area { padding: 0 3rem 3rem; overflow-y: auto; flex: 1; }

/* --- GLASS CARD --- */
.glass-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 20px; box-shadow: 0 15px 35px rgba(15, 23, 42, 0.04), inset 0 1px 0 white; }
.main-form-card { padding: 3rem; max-width: 900px; margin: 0 auto; }

/* --- AVATAR SECTION --- */
.avatar-section { display: flex; align-items: center; gap: 2.5rem; }
.avatar-wrapper { width: 120px; height: 120px; border-radius: 50%; overflow: hidden; border: 4px solid #ffffff; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.provider-gradient { background: linear-gradient(135deg, #2563eb, #60a5fa); color: white; }
.profile-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 3.5rem; font-weight: 800; color: white; }
.avatar-actions h3 { margin: 0 0 0.3rem 0; font-size: 1.2rem; color: #0f172a; font-weight: 800; }
.sub-text { color: #64748b; font-size: 0.9rem; margin: 0 0 1rem 0; }
.divider { border: 0; height: 1px; background: rgba(0,0,0,0.06); margin: 2.5rem 0; }

/* --- FORM STYLES --- */
.pro-form { display: flex; flex-direction: column; gap: 2rem; }
.section-title { font-size: 1.15rem; font-weight: 800; color: #0f172a; margin: 0 0 1.5rem 0; }
.form-row { display: flex; gap: 1.5rem; margin-bottom: 1.5rem; }
.half-width { flex: 1; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-size: 0.85rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }

.pro-input { width: 100%; padding: 0.9rem 1.2rem; border: 1px solid #cbd5e1; border-radius: 10px; font-family: inherit; font-size: 0.95rem; color: #1e293b; background: rgba(255,255,255,0.8); transition: 0.2s; box-sizing: border-box; font-weight: 500; }
.pro-input:focus { outline: none; border-color: #2563eb; background: #ffffff; box-shadow: 0 0 0 3px rgba(37,99,235,0.15); }

/* --- FEE SECTION --- */
.fee-section { background: rgba(248, 250, 252, 0.5); border: 1px dashed #cbd5e1; padding: 2rem; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem; }
.fee-header { max-width: 400px; }
.m-0 { margin: 0; }
.fee-input-wrapper { display: flex; align-items: center; position: relative; width: 200px; }
.currency-symbol { position: absolute; left: 1rem; font-size: 1.2rem; font-weight: 800; color: #2563eb; z-index: 1; }
.fee-input { padding-left: 2.5rem; font-size: 1.2rem; font-weight: 800; color: #0f172a; }

/* --- BUTTONS --- */
.form-actions-bar { display: flex; justify-content: flex-end; align-items: center; gap: 1.5rem; border-top: 1px solid rgba(0,0,0,0.06); padding-top: 2rem; margin-top: 1rem; }
.btn-primary-blue { background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; border: none; padding: 0.9rem 2rem; border-radius: 10px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(37,99,235,0.25); }
.btn-primary-blue:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37,99,235,0.35); }
.btn-outline-slate { background: white; border: 1px solid #cbd5e1; color: #475569; padding: 0.7rem 1.2rem; border-radius: 10px; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: 0.2s; display: inline-flex; justify-content: center; align-items: center; }
.btn-outline-slate:hover { border-color: #0f172a; color: #0f172a; background: #f8fafc; }

.alert-msg { font-weight: 700; font-size: 0.95rem; }
.text-green { color: #10b981; }
.text-red { color: #ef4444; }
.mt-3 { margin-top: 1.5rem; }
.mt-4 { margin-top: 2rem; }
.w-100 { width: 100%; }

.loading-state { text-align: center; padding: 5rem; color: #64748b; margin: 0 auto; max-width: 900px; display: flex; flex-direction: column; align-items: center; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite; margin-bottom: 1.5rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-in-up { animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); filter: blur(4px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }
</style>