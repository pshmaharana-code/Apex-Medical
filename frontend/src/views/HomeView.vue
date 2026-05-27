<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import gsap from 'gsap'

const router = useRouter()
const authStore = useAuthStore()

const handleActionClick = () => {
    if (authStore.isAuthenticated) {
        if (authStore.user?.role === 'doctor') {
            router.push('/doctor-dashboard')
        } else {
            router.push('/patient-dashboard')
        }
    } else {
        router.push('/login')
    }
}

const handleBookClick = () => {
    if (authStore.isAuthenticated) {
        router.push('/book-appointment')
    } else {
        alert("Please login as a patient to book an appointment.")
        router.push('/login')
    }
}

onMounted(() => {
    // 1. Navbar drops in
    gsap.fromTo('.navbar', 
        { y: -50, opacity: 0 }, 
        { y: 0, opacity: 1, duration: 1, ease: 'power3.out' }
    )

    // 2. Hero Text Stagger
    gsap.fromTo(['.badge', '.hero-title', '.hero-subtitle', '.hero-actions'], 
        { y: 40, opacity: 0 }, 
        { y: 0, opacity: 1, duration: 1, stagger: 0.2, ease: 'power3.out', delay: 0.2 }
    )

    // 3. Floating Glass Cards Reveal
    gsap.fromTo('.glass-card',
        { y: 60, opacity: 0, scale: 0.9 },
        { y: 0, opacity: 1, scale: 1, duration: 1.2, stagger: 0.2, ease: 'back.out(1.2)', delay: 0.6 }
    )

    // 4. Continuous Floating Animation for the cards
    gsap.to('.card-top', { y: -15, duration: 3, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 2 })
    gsap.to('.card-main', { y: -20, duration: 4, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 2.5 })
    gsap.to('.card-bottom', { y: -10, duration: 3.5, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 2.2 })

    // 5. Stronger Dynamic Aura Background
    gsap.to('.aura-blob-1', { x: 150, y: 150, duration: 15, repeat: -1, yoyo: true, ease: 'sine.inOut' })
    gsap.to('.aura-blob-2', { x: -150, y: -100, duration: 20, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 2 })
})
</script>

<template>
    <div class="landing-page">
        <div class="vibe-background">
            <div class="bg-section bg-1"></div>
            <div class="bg-section bg-2"></div>
            <div class="bg-section bg-3"></div>
        </div>
        <div class="aura-container">
            <div class="aura-blob aura-blob-1"></div>
            <div class="aura-blob aura-blob-2"></div>
        </div>

        <div class="announcement-wrapper">
            <div class="announcement-bar">
                <span class="pulse-dot"></span>
                <p><strong>Ranked #1</strong> Regional Hospital for Cardiology & Neurology</p>
            </div>
        </div>

        <nav class="navbar">
            <div class="nav-brand">
                <img src="@/assets/apex-logo2.png" alt="ApexMedical Logo" class="w-auto object-contain" style="height: 65px;" />
                <span class="logo-text">ApexMedical</span>
            </div>
            
            <div class="nav-links">
                <a href="#services">Specialties</a>
                <a href="#doctors">Our Doctors</a>
                <a href="#contact">Contact</a>
            </div>

            <button @click="handleActionClick" class="btn-nav">
                {{ authStore.isAuthenticated ? 'Go to Dashboard' : 'Login' }}
            </button>
        </nav>

        <header class="hero-section">
            <div class="hero-content">
                <div class="badge">Premium Healthcare</div>
                <h1 class="hero-title">Exceptional Care,<br> Without the Wait.</h1>
                <p class="hero-subtitle">
                    Experience a new standard of medical excellence. Book appointments instantly, manage your records securely, and connect with top-tier specialists.
                </p>
                
                <div class="hero-actions">
                    <button @click="handleBookClick" class="btn-primary">
                        Book an Appointment
                    </button>
                    <button @click="handleActionClick" class="btn-secondary">
                        Access Portal
                    </button>
                </div>
            </div>

            <div class="hero-visual">
                <div class="floating-ui-container">
                    
                    <div class="glass-card card-top">
                        <img src="@/assets/dr-marcus.png" alt="Dr. Sarah Jenkins" class="card-avatar" style="object-fit: cover;" />
                        <div class="lines">
                            <div class="card-info">
                                <h4>Dr. Marcus Chen</h4>
                                <p>Head of Neurology</p>
                            </div>
                            <div class="line long"></div>
                        </div>
                    </div>

                    <div class="glass-card card-main">
                        <img src="@/assets/dr-sarah.png" alt="Dr. Sarah Jenkins" class="card-avatar" style="object-fit: cover;" />
                        <div class="card-info">
                            <h4>Dr. Sarah Jenkins</h4>
                            <p>Senior Cardiologist</p>
                        </div>
                        <div class="status-badge">Available Today</div>
                    </div>

                    <div class="glass-card card-bottom">
                        <span class="time-slot">10:30 AM</span>
                        <span class="time-slot active">11:00 AM</span>
                        <span class="time-slot">01:15 PM</span>
                    </div>

                </div>
            </div>
        </header>

        <section id="services" class="specialties-section">
            <div class="section-header">
                <span class="badge">Our Expertise</span>
                <h2 class="section-title">Centers of Excellence</h2>
                <p class="section-subtitle">World-class medical departments equipped with state-of-the-art technology and leading specialists.</p>
            </div>

            <div class="specialties-grid">
                <div class="specialty-card">
                    <div class="icon-wrapper cardiology">
                        <img src="@/assets/icon-cardio.png" alt="Cardiology" class="dept-icon" />
                    </div>
                    <h3>Cardiology</h3>
                    <p>Comprehensive heart care, from advanced diagnostics to complex cardiac surgeries.</p>
                    <a href="#doctors" class="learn-more">View Specialists &rarr;</a>
                </div>

                <div class="specialty-card">
                    <div class="icon-wrapper neurology">
                        <img src="@/assets/icon-neuro.png" alt="Neurology" class="dept-icon" />
                    </div>
                    <h3>Neurology</h3>
                    <p>Cutting-edge treatments for brain, spine, and complex nervous system disorders.</p>
                    <a href="#doctors" class="learn-more">View Specialists &rarr;</a>
                </div>

                <div class="specialty-card">
                    <div class="icon-wrapper orthopedics">
                        <img src="@/assets/icon-ortho.png" alt="Orthopedics" class="dept-icon" />
                    </div>
                    <h3>Orthopedics</h3>
                    <p>Specialized treatments for bones, joint replacements, and sports medicine.</p>
                    <a href="#doctors" class="learn-more">View Specialists &rarr;</a>
                </div>

                <div class="specialty-card">
                    <div class="icon-wrapper pediatrics">
                        <img src="@/assets/icon-peds.png" alt="Pediatrics" class="dept-icon" />
                    </div>
                    <h3>Pediatrics</h3>
                    <p>Compassionate, expert medical care for infants, children, and adolescents.</p>
                    <a href="#doctors" class="learn-more">View Specialists &rarr;</a>
                </div>
            </div>
        </section>

        <section id="doctors" class="doctors-section">
            <div class="section-header">
                <span class="badge">World-Class Team</span>
                <h2 class="section-title">Meet Our Experts</h2>
                <p class="section-subtitle">Consult with highly experienced professionals dedicated to providing exceptional patient care.</p>
            </div>

            <div class="doctors-grid">
                <div class="doctor-card">
                    <img src="@/assets/dr-sarah.png" alt="Dr. Sarah Jenkins" class="doc-avatar" style="object-fit: cover;" />
                    <div class="doc-info">
                        <h3>Dr. Sarah Jenkins</h3>
                        <p class="doc-dept">Senior Cardiologist</p>
                        <div class="doc-stats">
                            <span class="stat-badge">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="star-icon">
                                    <path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" />
                                </svg>
                                    4.9
                            </span>
                            <span class="stat-badge">12 Yrs Exp</span>
                        </div>
                    </div>
                </div>

                <div class="doctor-card">
                    <img src="@/assets/dr-marcus.png" alt="Dr. Marcus Chen" class="doc-avatar" style="object-fit: cover;" />
                    <div class="doc-info">
                        <h3>Dr. Marcus Chen</h3>
                        <p class="doc-dept">Head of Neurology</p>
                        <div class="doc-stats">
                            <span class="stat-badge">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="star-icon">
                                    <path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" />
                                </svg>
                                5.0
                            </span>
                            <span class="stat-badge">15 Yrs Exp</span>
                        </div>
                    </div>
                </div>

                <div class="doctor-card">
                    <img src="@/assets/dr-emily.png" alt="Dr. Emily Thorne" class="doc-avatar" style="object-fit: cover;" />
                    <div class="doc-info">
                        <h3>Dr. Emily Thorne</h3>
                        <p class="doc-dept">Pediatric Specialist</p>
                        <div class="doc-stats">
                            <span class="stat-badge">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="star-icon">
                                    <path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" />
                                </svg>
                                4.8
                            </span>
                            <span class="stat-badge">8 Yrs Exp</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>


        <footer id="contact" class="site-footer">
            <div class="footer-cta">
                <h2>Ready to prioritize your health?</h2>
                <p>Join thousands of patients who trust ApexMedical for their care.</p>
                <button @click="handleActionClick" class="btn-footer-cta">Access Patient Portal</button>
            </div>

            <div class="footer-content">
                <div class="footer-brand">
                    <div class="nav-brand">
                        <img src="@/assets/apex-logo2.png" alt="ApexMedical Logo" class="w-auto object-contain" style="height: 65px;" />
                        <span class="logo-text-light">ApexMedical</span>
                    </div>
                    <p class="brand-desc">Redefining modern healthcare with world-class specialists and cutting-edge technology.</p>
                </div>

                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <a href="#services">Centers of Excellence</a>
                    <a href="#doctors">Our Specialists</a>
                    <a href="#" @click.prevent="handleBookClick">Book Appointment</a>
                    <a href="#" @click.prevent="handleActionClick">Login</a>
                </div>

                <div class="footer-contact">
                    <h4>Contact Us</h4>
                    <p>123 Health Avenue, Medical District</p>
                    <p>+1 (800) 555-APEX</p>
                    <p>care@apexmedical.com</p>
                </div>
            </div>

            <div class="footer-bottom">
                <p>&copy; 2026 ApexMedical. All rights reserved.</p>
                <div class="legal-links">
                    <a href="#">Privacy Policy</a>
                    <a href="#">Terms of Service</a>
                </div>
            </div>
        </footer>
    </div>
</template>

<style scoped>
/* --- BASE SETUP --- */
.landing-page {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
    color: #0f172a;
    position: relative;
    overflow-x: hidden;
    /* Back to the soft base layer so the images can blend into it */
    background: linear-gradient(135deg, #f0f9ff 0%, #e6f2f2 100%); 
}
/* --- THE CONTINUOUS VIBE BACKGROUND --- */
/* --- THE CONTINUOUS VIBE BACKGROUND --- */
/* --- THE CONTINUOUS VIBE BACKGROUND (FIXED) --- */
.vibe-background {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0; /* Locks firmly to the full scrollable page height */
    z-index: 1;
    opacity: 0.35; /* Dialed down slightly so the text stays crisp */
    pointer-events: none;
}

.bg-section {
    position: absolute; /* Mathematically anchors each image */
    width: 100%;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* Top Image: Covers 0% to 40% of the page */
.bg-1 {
    top: 0;
    height: 40%;
    background-image: url('@/assets/bg-1.png');
    -webkit-mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
    mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
}

/* Middle Image: Covers 30% to 70% of the page (Overlaps the top and bottom!) */
.bg-2 {
    top: 30%;
    height: 40%;
    background-image: url('@/assets/bg-2.png');
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%);
    mask-image: linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%);
}

/* Bottom Image: Covers 60% to 100% of the page */
/* Bottom Image: Covers 60% to 95% of the page (Stops right before the footer!) */
.bg-3 {
    top: 60%;
    height: 35%;
    background-image: url('@/assets/bg-3.png');
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 30%, black 100%);
    mask-image: linear-gradient(to bottom, transparent 0%, black 30%, black 100%);
}

/* Let's also tone down the aura blobs since the image does the heavy lifting now */
.aura-blob {
    position: absolute;
    width: 800px;
    height: 800px;
    border-radius: 50%;
    filter: blur(120px); /* Softer blur */
    opacity: 0.3; /* Turned opacity way down */
    mix-blend-mode: overlay;
}
/* --- 2. MORE VIBRANT AURA --- */
.aura-container {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: 0; pointer-events: none;
}

.aura-blob {
    position: absolute;
    width: 800px; /* Made them larger to fill the white space */
    height: 800px;
    border-radius: 50%;
    filter: blur(90px); /* Tighter blur for more intense color */
    opacity: 0.65;
    mix-blend-mode: multiply;
}

/* Deepened the colors so they pop through the glass */
.aura-blob-1 { background: #7dd3fc; top: -10%; left: -5%; } 
.aura-blob-2 { background: #34d399; bottom: 0%; right: -5%; }

/* --- NEW ANNOUNCEMENT PILL --- */
.announcement-wrapper {
    display: flex;
    justify-content: center;
    padding-top: 1.5rem;
    position: relative;
    z-index: 101;
}

.announcement-bar {
    background: linear-gradient(90deg, #0f172a, #1e293b);
    color: #f8fafc;
    padding: 0.5rem 1.5rem;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 12px;
    border-radius: 30px; /* Transforms it into a sleek pill */
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15); /* Soft drop shadow */
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #10b981; 
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* --- UPGRADED FLOATING NAVBAR --- */
/* --- UPGRADED FLOATING NAVBAR --- */
/* --- THE HYBRID GLASS NAVBAR --- */
/* --- THE HYBRID GLASS NAVBAR --- */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    margin: 1.5rem 5% 0; 
    position: sticky;
    top: 1.5rem; 
    z-index: 100;
    
    background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.4)), url('@/assets/nav-bg.png');
    
    /* THE FIX: Forces the full image into the box (Width Height) */
    background-size: 100% 100%; 
    background-position: center;
    background-repeat: no-repeat;
    
    backdrop-filter: blur(24px) saturate(150%);
    -webkit-backdrop-filter: blur(24px) saturate(150%);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 24px; 
    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.15), 0 5px 15px rgba(0, 0, 0, 0.05); 
}

.nav-brand { display: flex; align-items: center; gap: 0.6rem; }
.logo-text { font-size: 1.3rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }
.nav-links a { text-decoration: none; color: #64748b; font-weight: 600; font-size: 0.95rem; margin: 0 1.5rem; transition: color 0.3s; }
.nav-links a:hover { color: #0f766e; }

.btn-nav { 
    background: white; 
    border: 1px solid #e2e8f0; 
    padding: 0.6rem 1.5rem; 
    border-radius: 30px; 
    font-weight: 600; 
    color: #0f172a; 
    cursor: pointer; 
    transition: all 0.3s ease; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
.btn-nav:hover { border-color: #0f766e; color: #0f766e; box-shadow: 0 4px 15px rgba(15, 118, 110, 0.1); }

/* --- HERO SECTION TWEAK --- */
/* Just make sure your hero section has a little less top padding now so it doesn't feel too distant */
.hero-section {
    position: relative;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6rem 5% 4rem; /* Adjusted top padding from 8rem to 6rem */
    max-width: 1400px;
    margin: 0 auto;
}

.hero-content {
    flex: 1;
    max-width: 600px;
}

.badge { display: inline-block; background: rgba(255,255,255,0.8); border: 1px solid #e2e8f0; color: #0f766e; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 1.5rem; }
.hero-title { font-size: 4rem; font-weight: 800; line-height: 1.1; color: #0f172a; margin-bottom: 1.5rem; letter-spacing: -1.5px; }
.hero-subtitle { font-size: 1.2rem; line-height: 1.6; color: #475569; margin-bottom: 2.5rem; }

/* --- BUTTONS --- */
.hero-actions { display: flex; gap: 1rem; }
.btn-primary { background: #0f766e; color: white; border: none; padding: 1rem 2rem; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease; box-shadow: 0 4px 14px rgba(15, 118, 110, 0.25); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(15, 118, 110, 0.4); }
.btn-secondary { background: rgba(255,255,255,0.5); backdrop-filter: blur(4px); color: #0f172a; border: 2px solid #cbd5e1; padding: 1rem 2rem; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; }
.btn-secondary:hover { background: white; border-color: #94a3b8; }

/* --- NEW FLOATING UI (SKEUOMORPHIC) --- */
.hero-visual {
    flex: 1;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    position: relative;
    height: 500px;
}

.floating-ui-container {
    position: relative;
    width: 450px;
    height: 100%;
}

.glass-card {
    position: absolute;
    /* True Translucent Glass Gradient */
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.1) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 20px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.05);
    padding: 1.5rem;
}

/* Small top card */
.card-top {
    top: 10%;
    left: 10%;
    width: 220px;
    display: flex;
    align-items: center;
    gap: 1rem;
    z-index: 2;
}

.icon-circle { width: 40px; height: 40px; border-radius: 50%; }
.icon-circle.teal { background: #ccfbf1; border: 2px solid #14b8a6; }
.lines { display: flex; flex-direction: column; gap: 8px; flex: 1; }
.line { height: 8px; border-radius: 4px; background: #e2e8f0; }
.line.short { width: 60%; }
.line.long { width: 100%; }

/* Main center card */
.card-main {
    top: 30%;
    right: 5%;
    width: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    z-index: 3;
    /* I REMOVED the solid white background override that was ruining this card! */
}

.card-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin-bottom: 1rem;
    border: 4px solid white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    
    /* THE CSS CROP MAGIC */
    object-fit: cover;
    object-position: center top; /* Keeps the focus on the face/head */
}

.card-info h4 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.2rem; }
.card-info p { margin: 0 0 1rem 0; color: #64748b; font-size: 0.9rem; }
.status-badge { background: #dcfce7; color: #166534; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }

/* Bottom time slots card */
.card-bottom {
    bottom: 15%;
    left: 0;
    width: 300px;
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    z-index: 4;
}

.time-slot {
    /* Changed from solid white to sheer glass */
    background: rgba(255, 255, 255, 0.3);
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #0f172a;
    border: 1px solid rgba(255, 255, 255, 0.5);
}

.time-slot.active {
    background: #0f766e;
    color: white;
    border-color: #0f766e;
    box-shadow: 0 4px 10px rgba(15, 118, 110, 0.3);
}


/* --- CENTERS OF EXCELLENCE SECTION --- */
.specialties-section {
    padding: 8rem 5%;
    position: relative;
    z-index: 10;
}

.section-header {
    text-align: center;
    max-width: 650px;
    margin: 0 auto 4rem;
}

.section-title {
    font-size: 3rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 1.2rem;
    letter-spacing: -1px;
}

.section-subtitle {
    font-size: 1.15rem;
    color: #334155; /* Darkened from #64748b for much better contrast */
    line-height: 1.6;
    font-weight: 500;
}

/* --- THE GRID --- */
.specialties-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

/* --- GLASSMORPHIC SPECIALTY CARDS --- */
.specialty-card {
    /* Increased the white opacity from 0.6 to 0.75 so the text is always legible */
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0.4) 100%);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04); /* Slightly deeper shadow */
}

.specialty-card:hover {
    transform: translateY(-12px);
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 20px 40px rgba(15, 118, 110, 0.08);
    border-color: #ffffff;
}

/* --- CARD INNER STYLING (The Premium Monograms) --- */
.icon-wrapper {
    width: 80px;      /* Increased from 56px */
    height: 80px;     /* Increased from 56px */
    border-radius: 20px; /* Slightly rounder to match the larger size */
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08); /* Softened and expanded the shadow */
    border: 1px solid rgba(255, 255, 255, 0.6);
}

.dept-icon {
    width: 65px;      /* Increased from 44px */
    height: 65px;     /* Increased from 44px */
    object-fit: contain; 
    /* Boosted the drop shadow so the larger 3D objects pop off the screen */
    filter: drop-shadow(0 8px 12px rgba(0,0,0,0.15)); 
    transition: transform 0.3s ease; /* Adds a nice hover effect baseline */
}

.specialty-card:hover .dept-icon {
    transform: scale(1.1) rotate(-5deg);
}

/* Sleeker, less saturated gradients for the icon boxes */
.cardiology { background: linear-gradient(135deg, #0f766e, #042f2e); }
.neurology { background: linear-gradient(135deg, #0f766e, #042f2e); }
.orthopedics { background: linear-gradient(135deg, #0f766e, #042f2e); }
.pediatrics { background: linear-gradient(135deg, #0f766e, #042f2e); }


/* --- FEATURED DOCTORS SECTION --- */
.doctors-section {
    padding: 6rem 5% 8rem;
    max-width: 1400px;
    margin: 0 auto;
    position: relative;
    z-index: 10;
}

.doctors-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2.5rem;
    margin-top: 2rem;
}

/* --- DOCTOR CARDS --- */
.doctor-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.4) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 24px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
}

.doctor-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(15, 118, 110, 0.08);
}

/* --- AVATARS --- */
.doc-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    margin-bottom: 1.5rem;
    border: 4px solid white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    
    /* THE CSS CROP MAGIC */
    object-fit: cover;
    object-position: center top; 
}



/* --- INFO & STATS --- */
.doc-info h3 {
    font-size: 1.3rem;
    color: #0f172a;
    margin: 0 0 0.3rem 0;
    font-weight: 700;
}

.doc-dept {
    color: #0f766e;
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0 0 1.2rem 0;
}

.doc-stats {
    display: flex;
    gap: 0.8rem;
    justify-content: center;
    margin-bottom: 2rem;
}

.stat-badge {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.8);
    color: #475569;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    
    /* NEW: Flexbox to perfectly align the star and text */
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

/* NEW: Styling the SVG star */
.star-icon {
    width: 16px;
    height: 16px;
    color: #f59e0b; /* A professional, warm amber/gold color */
}

/* --- PREMIUM FOOTER --- */
.site-footer {
    background-color: #0f172a; 
    color: #f8fafc;
    padding: 3.5rem 5% 1.5rem; /* Trimmed top padding from 6rem to 3.5rem */
    position: relative;
    z-index: 20; 
}

/* --- FOOTER CTA --- */
.footer-cta {
    text-align: center;
    padding-bottom: 2rem; /* Drastically reduced from 5rem */
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 2rem;  /* Drastically reduced from 4rem */
}

.footer-cta h2 {
    font-size: 2.2rem; /* Scaled down from 2.8rem for a sleeker look */
    font-weight: 800;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.footer-cta p {
    color: #94a3b8;
    font-size: 1.05rem; /* Scaled down from 1.2rem */
    margin-bottom: 1.2rem; /* Reduced from 2.5rem */
}

.btn-footer-cta {
    margin-top: 0.5rem; 
    background: #10b981; 
    color: #0f172a;
    border: none;
    padding: 0.75rem 2rem; /* Sleeker, less bulky button padding */
    border-radius: 30px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
}

.btn-footer-cta:hover {
    transform: translateY(-2px);
    background: #34d399;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

/* --- FOOTER CONTENT GRID --- */
.footer-content {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1.2fr; 
    gap: 2rem; /* Reduced column spacing */
    max-width: 1200px; 
    margin: 0 auto;
    padding-bottom: 2rem; /* Trimmed vertical gap before copyright line */
}

.brand-desc {
    color: #cbd5e1; 
    line-height: 1.5;
    margin-top: 1rem; /* Brought description closer to logo text */
    max-width: 320px;
    font-size: 0.9rem; /* Made description slightly more compact */
}

@media (max-width: 768px) { .brand-desc { margin: 1.5rem auto 0; } }

.footer-links h4, .footer-contact h4 {
    color: white;
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    font-weight: 600;
}

.footer-links {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

.footer-links a {
    color: #cbd5e1; /* Lightened from #94a3b8 */
    text-decoration: none;
    transition: color 0.3s ease;
    font-weight: 500;
}

.footer-links a:hover {
    color: #10b981;
}

.footer-contact p {
    color: #cbd5e1; /* Lightened from #94a3b8 */
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

@media (max-width: 768px) { .footer-contact p { justify-content: center; } }

/* --- FOOTER BOTTOM --- */
.footer-bottom {
    max-width: 1400px;
    margin: 0 auto;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #94a3b8; /* Lightened from #64748b */
    font-size: 0.95rem;
}

@media (max-width: 768px) {
    .footer-bottom {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
}

.legal-links {
    display: flex;
    gap: 2rem;
}

.legal-links a {
    color: #94a3b8; /* Lightened from #64748b */
    text-decoration: none;
    transition: color 0.3s;
}

.legal-links a:hover {
    color: white;
}
</style>