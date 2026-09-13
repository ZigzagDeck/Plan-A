"""Custom CSS design system for SlopeGuard Streamlit Dashboard.
Provides dark-mode glassmorphism, glowing risk indicators, anti-dimming overrides,
and prominent circular buffering indicators for real-time model inference.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* =========================================================================
   DISABLE STREAMLIT'S AUTOMATIC SCREEN DIMMING / GRAYING OUT DURING RUN
   ========================================================================= */
/* Prevent page and elements from fading to grey/dim when computing */
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
div[data-testid="stElementContainer"],
section.main,
.stApp,
.element-container {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}

.stApp[data-test-script-state="running"] div[data-testid="stAppViewBlockContainer"],
.stApp[data-test-script-state="running"] div[data-testid="stElementContainer"],
.stApp[data-test-script-state="running"] section.main,
.stApp[data-test-script-state="running"] div[data-testid="stAppViewContainer"] {
    opacity: 1 !important;
    filter: none !important;
}

/* Glassmorphic card styling */
.glass-card {
    background: rgba(18, 24, 38, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(0, 212, 255, 0.3);
    box-shadow: 0 8px 36px 0 rgba(0, 212, 255, 0.12);
}

/* Gradient Header */
.main-header {
    background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #0072FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8rem;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}

.sub-header {
    color: #94A3B8;
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 24px;
}

/* Status Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-critical {
    background: rgba(239, 68, 68, 0.2);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.5);
    box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

.badge-high {
    background: rgba(249, 115, 22, 0.2);
    color: #FB923C;
    border: 1px solid rgba(249, 115, 22, 0.5);
    box-shadow: 0 0 12px rgba(249, 115, 22, 0.3);
}

.badge-medium {
    background: rgba(234, 179, 8, 0.2);
    color: #FACC15;
    border: 1px solid rgba(234, 179, 8, 0.5);
}

.badge-low {
    background: rgba(34, 197, 94, 0.2);
    color: #4ADE80;
    border: 1px solid rgba(34, 197, 94, 0.5);
}

.badge-online {
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-offline {
    background: rgba(239, 68, 68, 0.2);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

/* Metric Display Container */
.metric-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 4px;
}

.metric-label {
    font-size: 0.85rem;
    color: #94A3B8;
    font-weight: 500;
    text-transform: uppercase;
}

/* Live Pulse Indicator */
.pulse-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #10B981;
    margin-right: 6px;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse 1.8s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

/* =========================================================================
   CIRCLING BUFFER / CIRCULAR SPINNER LOADING COMPONENT
   ========================================================================= */
.circular-buffer-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 36px 24px;
    margin: 20px 0;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 18px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 0 30px rgba(56, 189, 248, 0.08);
}

.circular-buffer-spinner {
    width: 68px;
    height: 68px;
    border: 5px solid rgba(56, 189, 248, 0.18);
    border-radius: 50%;
    border-top: 5px solid #38BDF8;
    border-right: 5px solid #818CF8;
    animation: circular-buffer-spin 0.85s cubic-bezier(0.5, 0.1, 0.5, 0.9) infinite;
    box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);
    margin-bottom: 16px;
}

@keyframes circular-buffer-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.circular-buffer-title {
    color: #F8FAFC;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    margin-bottom: 6px;
}

.circular-buffer-subtitle {
    color: #94A3B8;
    font-size: 0.9rem;
    font-weight: 400;
}

/* Make native Streamlit spinner also render as a circular buffer */
[data-testid="stSpinner"], .stSpinner {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 18px 24px !important;
    background: rgba(15, 23, 42, 0.85) !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 12px !important;
    margin: 16px 0 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
}

[data-testid="stSpinner"] > div:first-child {
    width: 32px !important;
    height: 32px !important;
    border: 4px solid rgba(56, 189, 248, 0.2) !important;
    border-top-color: #38BDF8 !important;
    border-right-color: #818CF8 !important;
    border-radius: 50% !important;
    animation: circular-buffer-spin 0.85s linear infinite !important;
}
</style>
"""


def apply_custom_styles() -> str:
    return CUSTOM_CSS

