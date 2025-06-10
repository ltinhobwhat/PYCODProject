# app/menu.py - Revamped as Navigation Hub
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

menu_bp = Blueprint('menu', __name__)

@menu_bp.route("/")
@login_required
def menu():
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CyberSec Academy - Command Center</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', 'Orbitron', sans-serif;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%);
                color: #ffffff;
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }}

            /* Animated background grid */
            body::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    linear-gradient(90deg, transparent 95%, rgba(0, 255, 136, 0.1) 5%), 
                    linear-gradient(transparent 95%, rgba(0, 255, 136, 0.1) 5%);
                background-size: 50px 50px;
                animation: gridMove 20s linear infinite;
                z-index: -2;
            }}

            @keyframes gridMove {{
                0% {{ transform: translate(0, 0); }}
                100% {{ transform: translate(50px, 50px); }}
            }}

            /* Floating orbs */
            .orb {{
                position: fixed;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(0, 255, 136, 0.3), transparent);
                animation: float 15s infinite ease-in-out;
                z-index: -1;
            }}

            .orb1 {{
                width: 200px;
                height: 200px;
                top: 10%;
                left: 10%;
                animation-delay: 0s;
            }}

            .orb2 {{
                width: 150px;
                height: 150px;
                top: 70%;
                right: 15%;
                animation-delay: 5s;
            }}

            .orb3 {{
                width: 100px;
                height: 100px;
                top: 40%;
                left: 80%;
                animation-delay: 10s;
            }}

            @keyframes float {{
                0%, 100% {{ transform: translateY(0px) scale(1); }}
                33% {{ transform: translateY(-20px) scale(1.1); }}
                66% {{ transform: translateY(20px) scale(0.9); }}
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                position: relative;
                z-index: 1;
            }}

            /* Header Section */
            .header {{
                text-align: center;
                margin-bottom: 3rem;
                position: relative;
            }}

            .header::before {{
                content: "";
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, rgba(0, 255, 136, 0.1), transparent);
                border-radius: 50%;
                z-index: -1;
            }}

            .logo {{
                font-size: 3.5rem;
                font-weight: bold;
                color: #00ff88;
                text-shadow: 0 0 30px rgba(0, 255, 136, 0.8);
                margin-bottom: 1rem;
                animation: titleGlow 3s ease-in-out infinite alternate;
                letter-spacing: 3px;
            }}

            @keyframes titleGlow {{
                from {{ text-shadow: 0 0 30px rgba(0, 255, 136, 0.8); }}
                to {{ text-shadow: 0 0 50px rgba(0, 255, 136, 1), 0 0 80px rgba(0, 255, 136, 0.5); }}
            }}

            .welcome-text {{
                font-size: 1.3rem;
                color: #00ff88;
                margin-bottom: 0.5rem;
                font-weight: 600;
            }}

            .subtitle {{
                font-size: 1.1rem;
                opacity: 0.9;
                color: #ffffff;
                max-width: 600px;
                margin: 0 auto 2rem;
                line-height: 1.6;
            }}

            /* User Stats Panel */
            .stats-panel {{
                background: rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(20px);
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 3rem;
                position: relative;
                overflow: hidden;
            }}

            .stats-panel::before {{
                content: "";
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.1), transparent);
                animation: shimmer 3s infinite;
            }}

            @keyframes shimmer {{
                0% {{ left: -100%; }}
                100% {{ left: 100%; }}
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 2rem;
                text-align: center;
            }}

            .stat-item {{
                position: relative;
            }}

            .stat-value {{
                font-size: 2.5rem;
                font-weight: bold;
                color: #00ff88;
                display: block;
                text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
            }}

            .stat-label {{
                font-size: 1rem;
                opacity: 0.8;
                margin-top: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            /* Navigation Cards */
            .nav-section {{
                margin-top: 3rem;
            }}

            .section-title {{
                font-size: 2rem;
                text-align: center;
                margin-bottom: 2rem;
                color: #00ff88;
                text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
                text-transform: uppercase;
                letter-spacing: 2px;
            }}

            .nav-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            }}

            .nav-card {{
                background: rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(15px);
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 20px;
                padding: 2.5rem;
                text-align: center;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                position: relative;
                overflow: hidden;
                text-decoration: none;
                color: inherit;
                cursor: pointer;
            }}

            .nav-card::before {{
                content: "";
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: radial-gradient(circle, rgba(0, 255, 136, 0.1), transparent);
                transition: all 0.4s ease;
                transform: translate(-50%, -50%);
                border-radius: 50%;
            }}

            .nav-card:hover {{
                transform: translateY(-15px) scale(1.02);
                border-color: #00ff88;
                box-shadow: 
                    0 25px 50px rgba(0, 255, 136, 0.3),
                    0 0 50px rgba(0, 255, 136, 0.2);
            }}

            .nav-card:hover::before {{
                width: 300px;
                height: 300px;
            }}

            .nav-icon {{
                font-size: 4rem;
                color: #00ff88;
                margin-bottom: 1.5rem;
                text-shadow: 0 0 20px rgba(0, 255, 136, 0.6);
                position: relative;
                z-index: 1;
                transition: all 0.3s ease;
            }}

            .nav-card:hover .nav-icon {{
                transform: scale(1.1) rotateY(15deg);
                text-shadow: 0 0 30px rgba(0, 255, 136, 1);
            }}

            .nav-title {{
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 1rem;
                color: #00ff88;
                position: relative;
                z-index: 1;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .nav-description {{
                font-size: 1.1rem;
                opacity: 0.9;
                line-height: 1.6;
                position: relative;
                z-index: 1;
            }}

            .nav-badge {{
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: linear-gradient(135deg, #00ff88, #00cc6a);
                color: #000;
                padding: 0.3rem 0.8rem;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            /* Logout Section */
            .logout-section {{
                text-align: center;
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 1px solid rgba(0, 255, 136, 0.3);
            }}

            .logout-btn {{
                background: rgba(255, 69, 69, 0.2);
                border: 2px solid rgba(255, 69, 69, 0.5);
                color: #ff4545;
                padding: 1rem 2rem;
                border-radius: 10px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
                display: inline-flex;
                align-items: center;
                gap: 0.8rem;
            }}

            .logout-btn:hover {{
                background: rgba(255, 69, 69, 0.3);
                border-color: #ff4545;
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(255, 69, 69, 0.3);
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                .container {{
                    padding: 1rem;
                }}

                .logo {{
                    font-size: 2.5rem;
                }}

                .nav-grid {{
                    grid-template-columns: 1fr;
                    gap: 1.5rem;
                }}

                .stats-grid {{
                    grid-template-columns: repeat(2, 1fr);
                    gap: 1rem;
                }}

                .nav-card {{
                    padding: 2rem;
                }}

                .nav-icon {{
                    font-size: 3rem;
                }}

                .nav-title {{
                    font-size: 1.5rem;
                }}
            }}

            /* Security scanner effect */
            .scanner-line {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, #00ff88, transparent);
                animation: scan 8s linear infinite;
                z-index: 10;
                opacity: 0.6;
            }}

            @keyframes scan {{
                0% {{ top: 0; }}
                100% {{ top: 100vh; }}
            }}
        </style>
    </head>
    <body>
        <!-- Floating orbs -->
        <div class="orb orb1"></div>
        <div class="orb orb2"></div>
        <div class="orb orb3"></div>
        
        <!-- Scanner effect -->
        <div class="scanner-line"></div>

        <div class="container">
            <!-- Header Section -->
            <div class="header">
                <h1 class="logo">
                    <i class="fas fa-shield-alt"></i> CYBERSEC ACADEMY
                </h1>
                <div class="welcome-text">Welcome back, Agent {current_user.username}</div>
                <p class="subtitle">
                    Your mission: Master cybersecurity through immersive challenges and rise through the ranks. 
                    The digital battlefield awaits your expertise.
                </p>
            </div>

            <!-- User Stats Panel -->
            <div class="stats-panel">
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-value">{current_user.total_score}</span>
                        <div class="stat-label">Total Score</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{current_user.games_completed}/6</span>
                        <div class="stat-label">Missions Complete</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">#{current_user.get_rank()}</span>
                        <div class="stat-label">Global Rank</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">Rising Hacker</span>
                        <div class="stat-label">Current Rank</div>
                    </div>
                </div>
            </div>

            <!-- Navigation Section -->
            <div class="nav-section">
                <h2 class="section-title">Command Center</h2>
                <div class="nav-grid">
                    <!-- Challenge Map -->
                    <a href="/map" class="nav-card">
                        <div class="nav-badge">Primary</div>
                        <div class="nav-icon">
                            <i class="fas fa-map-marked-alt"></i>
                        </div>
                        <div class="nav-title">Challenge Map</div>
                        <div class="nav-description">
                            Navigate through the cyber city and access all security challenges. 
                            Each district offers unique learning experiences and rewards.
                        </div>
                    </a>

                    <!-- Leaderboard -->
                    <a href="/leaderboard" class="nav-card">
                        <div class="nav-badge">Compete</div>
                        <div class="nav-icon">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div class="nav-title">Leaderboard</div>
                        <div class="nav-description">
                            See how you rank against other cybersecurity agents worldwide. 
                            Climb the ranks and prove your expertise.
                        </div>
                    </a>

                    <!-- Dashboard -->
                    <a href="/leaderboard/dashboard" class="nav-card">
                        <div class="nav-badge">Analytics</div>
                        <div class="nav-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="nav-title">Analytics Dashboard</div>
                        <div class="nav-description">
                            Track your detailed progress, performance metrics, and achievements. 
                            Monitor your growth as a security professional.
                        </div>
                    </a>
                </div>
            </div>

            <!-- Logout Section -->
            <div class="logout-section">
                <a href="/auth/logout" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i>
                    Secure Logout
                </a>
            </div>
        </div>

        <script>
            // Add dynamic particle effects
            function createParticle() {{
                const particle = document.createElement('div');
                particle.style.position = 'fixed';
                particle.style.width = '2px';
                particle.style.height = '2px';
                particle.style.background = '#00ff88';
                particle.style.left = Math.random() * 100 + 'vw';
                particle.style.top = '100vh';
                particle.style.pointerEvents = 'none';
                particle.style.opacity = Math.random();
                particle.style.zIndex = '-1';
                
                document.body.appendChild(particle);
                
                const animation = particle.animate([
                    {{ transform: 'translateY(0px)', opacity: 0 }},
                    {{ transform: 'translateY(-20px)', opacity: 1 }},
                    {{ transform: 'translateY(-100vh)', opacity: 0 }}
                ], {{
                    duration: 6000,
                    easing: 'linear'
                }});
                
                animation.onfinish = () => particle.remove();
            }}

            // Create particles periodically
            setInterval(createParticle, 300);

            // Add mouse movement effects
            document.addEventListener('mousemove', (e) => {{
                const cards = document.querySelectorAll('.nav-card');
                cards.forEach(card => {{
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {{
                        const rotateX = (y - rect.height / 2) / 10;
                        const rotateY = (x - rect.width / 2) / -10;
                        card.style.transform = `translateY(-15px) scale(1.02) rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg)`;
                    }}
                }});
            }});

            // Add click sound effect simulation
            document.querySelectorAll('.nav-card').forEach(card => {{
                card.addEventListener('click', (e) => {{
                    // Add a brief flash effect
                    const flash = document.createElement('div');
                    flash.style.position = 'absolute';
                    flash.style.top = '0';
                    flash.style.left = '0';
                    flash.style.width = '100%';
                    flash.style.height = '100%';
                    flash.style.background = 'rgba(0, 255, 136, 0.3)';
                    flash.style.pointerEvents = 'none';
                    flash.style.borderRadius = '20px';
                    card.appendChild(flash);
                    
                    setTimeout(() => flash.remove(), 200);
                }});
            }});

            // Add typing effect to welcome text
            const welcomeText = document.querySelector('.welcome-text');
            if (welcomeText) {{
                const originalText = welcomeText.textContent;
                welcomeText.textContent = '';
                let i = 0;
                
                const typeWriter = () => {{
                    if (i < originalText.length) {{
                        welcomeText.textContent += originalText.charAt(i);
                        i++;
                        setTimeout(typeWriter, 100);
                    }}
                }};
                
                setTimeout(typeWriter, 1000);
            }}
        </script>
    </body>
    </html>
    '''

@menu_bp.route('/end_game')
def end_game():
    return "Game ended!"
