"""Custom CSS design system for Plan-A Streamlit Dashboard.
Provides dark-mode glassmorphism, glowing risk indicators, and clean typography.
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
</style>
"""


def apply_custom_styles() -> str:
    return CUSTOM_CSS
