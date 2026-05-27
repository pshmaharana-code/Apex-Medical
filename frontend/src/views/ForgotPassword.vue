<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// UI State
const currentStep = ref(1) // 1: Username, 2: OTP, 3: New Password
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Form Data
const username = ref('')
const otp = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// --- API CALLS ---
const requestResetCode = async () => {
    if (!username.value) return
    isLoading.value = true; errorMessage.value = ''; successMessage.value = ''
    
    try {
        const response = await axios.post('http://127.0.0.1:5000/api/auth/forgot-password', {
            username: username.value
        })
        successMessage.value = response.data.msg
        setTimeout(() => {
            successMessage.value = ''
            currentStep.value = 2 // Move to Step 2!
        }, 1500)
    } catch (error) {
        errorMessage.value = error.response?.data?.msg || "Failed to request code."
    } finally { isLoading.value = false }
}

const verifyCode = async () => {
    if (!otp.value) return
    isLoading.value = true; errorMessage.value = ''; successMessage.value = ''
    
    try {
        const response = await axios.post('http://127.0.0.1:5000/api/auth/verify-otp', {
            username: username.value,
            otp: otp.value
        })
        successMessage.value = response.data.msg
        setTimeout(() => {
            successMessage.value = ''
            currentStep.value = 3 // Move to Step 3!
        }, 1000)
    } catch (error) {
        errorMessage.value = error.response?.data?.msg || "Invalid code."
    } finally { isLoading.value = false }
}

const submitNewPassword = async () => {
    if (newPassword.value !== confirmPassword.value) {
        errorMessage.value = "Passwords do not match!"
        return
    }
    
    isLoading.value = true; errorMessage.value = ''; successMessage.value = ''
    
    try {
        const response = await axios.post('http://127.0.0.1:5000/api/auth/reset-password', {
            username: username.value,
            otp: otp.value,
            password: newPassword.value 
        })
        successMessage.value = response.data.msg
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
            router.push('/login')
        }, 2000)
    } catch (error) {
        errorMessage.value = error.response?.data?.msg || "Failed to reset password."
    } finally { isLoading.value = false }
}
</script>

<template>
    <div class="auth-page">
        <div class="auth-wrapper">
            <div class="brand-header" @click="$router.push('/')">
                <img src="@/assets/apex-logo.png" alt="ApexMedical Logo" class="brand-logo" />
                <span class="logo-text">ApexMedical</span>
            </div>

            <div class="auth-card">
                <div class="card-header">
                    <h2>Password Recovery</h2>
                    <p v-if="currentStep === 1">Enter your username to receive a 6-digit recovery code.</p>
                    <p v-if="currentStep === 2">We've generated a secure code. Please enter it below.</p>
                    <p v-if="currentStep === 3">Code verified! Create your new password.</p>
                </div>

                <div v-if="errorMessage" class="error-alert">{{ errorMessage }}</div>
                <div v-if="successMessage" class="success-alert">{{ successMessage }}</div>

                <form v-if="currentStep === 1" @submit.prevent="requestResetCode" class="auth-form">
                    <div class="input-group">
                        <label>Username</label>
                        <input type="text" v-model="username" required placeholder="Enter your username" />
                    </div>
                    <button type="submit" class="btn-primary" :disabled="isLoading">
                        {{ isLoading ? 'Sending...' : 'Send Recovery Code' }}
                    </button>
                </form>

                <form v-if="currentStep === 2" @submit.prevent="verifyCode" class="auth-form">
                    <div class="input-group">
                        <label>6-Digit Recovery Code</label>
                        <input type="text" v-model="otp" required placeholder="e.g., 123456" maxlength="6" class="text-center letter-spacing" />
                    </div>
                    <button type="submit" class="btn-primary" :disabled="isLoading">
                        {{ isLoading ? 'Verifying...' : 'Verify Code' }}
                    </button>
                    <button type="button" @click="currentStep = 1" class="btn-link">Cancel / Back</button>
                </form>

                <form v-if="currentStep === 3" @submit.prevent="submitNewPassword" class="auth-form">
                    <div class="input-group">
                        <label>New Password</label>
                        <input type="password" v-model="newPassword" required placeholder="Enter new password" />
                    </div>
                    <div class="input-group">
                        <label>Confirm Password</label>
                        <input type="password" v-model="confirmPassword" required placeholder="Confirm new password" />
                    </div>
                    <button type="submit" class="btn-primary" :disabled="isLoading">
                        {{ isLoading ? 'Saving...' : 'Reset Password' }}
                    </button>
                </form>

                <div class="login-prompt" v-if="currentStep === 1">
                    Remember your password? <router-link to="/login">Log in here</router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&display=swap');

/* --- BASE SETUP & CINEMATIC BACKGROUND --- */
.auth-page {
    font-family: 'Inter', -apple-system, sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: 2rem 0; 
    
    /* Cinematic Background */
    background-image: url('@/assets/auth-bg.png');
    background-size: cover;
    background-position: center;
}

/* --- WRAPPER & BRAND --- */
.auth-wrapper {
    position: relative;
    z-index: 10;
    width: 100%;
    max-width: 440px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.brand-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 2rem;
    cursor: pointer;
    transition: transform 0.2s ease;
}

.brand-header:hover { transform: scale(1.02); }

.brand-logo {
    height: 40px;
    width: 40px;
    object-fit: contain;
    background: #ffffff;
    border-radius: 50%;
    padding: 5px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    border: 1px solid rgba(15, 118, 110, 0.1);
}

.logo-text { font-size: 1.6rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }

/* --- GLASSMORPHIC CARD --- */
.auth-card {
    width: 100%;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0.4) 100%);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0,0,0,0.05);
}

.card-header { text-align: center; margin-bottom: 2rem; }
.card-header h2 { 
    font-family: 'Outfit', sans-serif;
    color: #0f172a; 
    font-size: 2.1rem; 
    font-weight: 800; 
    margin-bottom: 0.5rem; 
    letter-spacing: -1px; 
}
.card-header p { color: #475569; font-size: 0.95rem; line-height: 1.5; }

/* --- FORM INPUTS --- */
.auth-form { display: flex; flex-direction: column; gap: 1.5rem; }

.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.input-group label { font-size: 0.85rem; font-weight: 600; color: #334155; }

.input-group input {
    padding: 0.9rem 1.2rem;
    border-radius: 12px;
    border: 1px solid #cbd5e1;
    background: rgba(255, 255, 255, 0.9);
    font-size: 0.95rem;
    color: #0f172a;
    transition: all 0.3s ease;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.input-group input:focus {
    outline: none;
    border-color: #0f766e;
    box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.1);
    background: #ffffff;
}

.input-group input::placeholder { color: #94a3b8; font-weight: 400; }

/* Special styling for the 6-digit OTP code */
.text-center { text-align: center; }
.letter-spacing { letter-spacing: 8px; font-weight: 700; font-size: 1.2rem !important; }

/* --- ALERTS --- */
.error-alert {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #dc2626;
    padding: 0.8rem;
    border-radius: 10px;
    font-size: 0.9rem;
    text-align: center;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.success-alert {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: #059669;
    padding: 0.8rem;
    border-radius: 10px;
    font-size: 0.9rem;
    text-align: center;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

/* --- BUTTONS & LINKS --- */
.btn-primary {
    font-family: 'Outfit', sans-serif;
    background: #0f766e;
    color: white;
    border: none;
    padding: 1rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 14px rgba(15, 118, 110, 0.25);
    margin-top: 0.5rem;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(15, 118, 110, 0.4);
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.btn-link {
    background: none;
    border: none;
    color: #64748b;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: -0.5rem;
    transition: color 0.2s;
}

.btn-link:hover { color: #0f172a; }

.login-prompt {
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.95rem;
    color: #64748b;
}

.login-prompt a {
    color: #0f766e;
    font-weight: 700;
    text-decoration: none;
    transition: color 0.2s;
}

.login-prompt a:hover { color: #042f2c; }
</style>