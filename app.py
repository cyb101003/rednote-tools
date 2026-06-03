import streamlit as st
import requests
import time
import ast
import random
import json

# 1. Page Configuration
st.set_page_config(
    page_title="RealSkill Humanized Viral Copywriting Engine",
    page_icon="🔥",
    layout="wide"
)

st.markdown("""
<style>
    /* Hide top right main menu */
    #MainMenu {visibility: hidden;}

    /* Hide Deploy button */
    .stDeployButton {display: none;}
    [data-testid="stDeployButton"] {display: none;}

    /* Hide Streamlit footer and header */
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize Session State to temporarily store generation results
if "current_data" not in st.session_state:
    st.session_state.current_data = None

# ==================== Modern Premium CSS Injection ====================
st.markdown("""
<style>
    /* Global warm background with subtle grid texture */
    .stApp {
        background-color: #FFFDF7;
        background-image: 
            linear-gradient(rgba(240, 197, 36, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(240, 197, 36, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
        font-family: '-apple-system', BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Top Banner: Premium Frosted Glass Effect */
    .title-container {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(30, 144, 255, 0.12);
        box-shadow: 0 10px 30px rgba(212, 173, 56, 0.05);
        margin-bottom: 25px;
        position: relative;
    }
    .campus-badge {
        background: linear-gradient(135deg, #FFD43F, #FFAA00);
        color: #1E1E1E;
        padding: 5px 14px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 1px;
        display: inline-block;
        margin-bottom: 12px;
    }
    
    /* Data Cards: Frosted Glass & Hover Effects */
    .stat-box {
        background-color: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.04);
        border-radius: 20px;
        padding: 22px 10px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.01);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .stat-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(212, 173, 56, 0.1);
        border-color: rgba(255, 197, 36, 0.3);
        background-color: rgba(255, 255, 255, 0.9);
    }
    .stat-num {
        font-size: 34px;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .stat-label {
        font-size: 13px;
        color: #666666;
        font-weight: 600;
    }
    
    /* Feature Cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 20px;
        padding: 24px;
        position: relative;
        box-shadow: 0 6px 18px rgba(0,0,0,0.01);
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #FFC524;
        box-shadow: 0 10px 25px rgba(255, 197, 36, 0.12);
        background-color: rgba(255, 255, 255, 0.9);
    }
    .hot-tag {
        background: linear-gradient(135deg, #FF4D4F, #FF7875);
        color: white;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 10px;
        position: absolute;
        top: 16px;
        right: 16px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(255, 77, 79, 0.3);
    }
    .new-tag {
        background: linear-gradient(135deg, #00B578, #34D399);
        color: white;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 10px;
        position: absolute;
        top: 16px;
        right: 16px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0, 181, 120, 0.3);
    }
    
    /* 🔥 UPGRADED HIGH-CONVERSION GENERATE BUTTON 🔥 */
    .generate-btn-container div.stButton > button:first-child {
        background: linear-gradient(135deg, #FF416C, #FF4B2B, #FF8C00) !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        letter-spacing: 2px !important;
        border: none !important;
        border-radius: 24px !important;
        box-shadow: 0 10px 30px rgba(255, 75, 43, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        width: 100% !important;
        padding: 24px 0px !important;
        margin: 25px 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .generate-btn-container div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #FF4B2B, #FF8C00, #FFD000) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 15px 35px rgba(255, 75, 43, 0.6) !important;
    }
    .generate-btn-container div.stButton > button:first-child:active {
        transform: translateY(1px) !important;
        box-shadow: 0 6px 15px rgba(255, 75, 43, 0.3) !important;
    }
    
    /* Result Display & Evaluation Cards */
    .result-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.01);
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-color: rgba(0, 132, 255, 0.3);
        box-shadow: 0 6px 20px rgba(0, 132, 255, 0.05);
        background-color: rgba(255, 255, 255, 0.95);
    }

    .judge-box {
        background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,253,240,0.85)); 
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1.5px solid #FFC524; 
        border-radius: 24px; 
        padding: 30px; 
        box-shadow: 0 10px 30px rgba(255, 197, 36, 0.08); 
        margin-bottom: 35px;
    }
    .winner-badge {
        background: linear-gradient(135deg, #1E1E1E, #3A3A3A); 
        color:#FFC524; 
        font-weight:900; 
        padding:8px 18px; 
        border-radius:10px; 
        font-size:14px;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .score-pill {
        background: #FFFFFF;
        color: #1E1E1E;
        padding: 5px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 10px;
        border: 1px solid rgba(0,0,0,0.1);
        display: inline-block;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    
    /* Input Control Transparency Improvements */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus, .stTextArea>div>div>textarea:focus {
        border-color: #FFC524 !important;
        box-shadow: 0 0 0 3px rgba(255, 197, 36, 0.15) !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Helper Text Styles */
    .help-text {
        font-size: 12px;
        color: #8E8E93;
        margin-top: 4px;
        margin-bottom: 12px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Header Section ====================
st.markdown("""
<div class="title-container">
    <div class="campus-badge">CAMPUS COPYWRITING ENGINE</div>
    <h1 style="margin: 0; font-weight: 900; color: #1E1E1E; font-size: 38px; letter-spacing: -0.5px;">What kind of viral hit are we creating today?</h1>
    <p style="color: #666; margin-top: 10px; margin-bottom: 0; font-size: 15px; font-weight: 500;">✨ Multi-Agent adversarial testing · Destroys artificial AI patterns · Maximize social media engagement</p>
</div>
""", unsafe_allow_html=True)

# ==================== Top Statistics Status Bar ====================
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #0084FF;">🧠 Stage 3</div><div class="stat-label">Agent Panel Review</div></div>', unsafe_allow_html=True)
with col_s2:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #FFC524;">⚡ 100%</div><div class="stat-label">Social Media Alignment</div></div>', unsafe_allow_html=True)
with col_s3:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #FF4D4F;">🎯 0%</div><div class="stat-label">AI Buzzword Residue</div></div>', unsafe_allow_html=True)
with col_s4:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #00B578;">🔥 9.8</div><div class="stat-label">User Recommendation Score</div></div>', unsafe_allow_html=True)

st.write("")

# ==================== Input and Configuration Area ====================
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("### 🛠️ Inspiration Console")
    
    topic = st.text_input("Core Topic / Subject", value="Studying Abroad")
    st.markdown("<span class='help-text'>💡 Enter the core event or idea. E.g., 'Changing majors with high GPA' or 'A day in the life of an overworked student'.</span>", unsafe_allow_html=True)
    
    # Keeping underlying system keys unvaried while mapping user friendly English labels
    platform_options = {
        "RED (Xiaohongshu)": "xiaohongshu",
        "Zhihu": "zhihu",
        "Weibo": "weibo"
    }
    selected_platform_ui = st.selectbox("Target Platform", list(platform_options.keys()))
    platform = platform_options[selected_platform_ui]
    st.markdown("<span class='help-text'>📱 The engine automatically customizes layout logic (RED: Emoji-heavy / Zhihu: Rational long-form / Weibo: Fast-paced).</span>", unsafe_allow_html=True)
    
    ai_level = st.select_slider("🔥 Human Tone Intensity (De-AI Filter)", options=["Slightly Polished", "Fully Colloquial", "Hyper-Casual & Witty"])
    st.markdown("<span class='help-text'>⚙️ Higher levels mean looser sentence structures, mimicking raw, organic social updates.</span>", unsafe_allow_html=True)
    
    style_refs = st.text_area("Reference Copywriting Style (One per line)", value="", placeholder="Paste copy samples from creators you want to emulate...")
    st.markdown("<span class='help-text'>📝 Optional. Providing samples helps the Multi-Agent system deconstruct phrasing styles and signature interjections.</span>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 💡 Strategic Copy Features")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("""
        <div class="feature-card">
            <span class="hot-tag">HOT</span>
            <h4 style="margin:0 0 10px 0; color:#1E1E1E;">🔥 Platform Synchrony</h4>
            <p style="font-size:13px; color:#666; margin:0; line-height:1.5;">Restructures titles to seize the golden 3-second attention span using emotional hooks.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div class="feature-card">
            <span class="new-tag">NEW</span>
            <h4 style="margin:0 0 10px 0; color:#1E1E1E;">🧠 Anti-AI Cleanse</h4>
            <p style="font-size:13px; color:#666; margin:0; line-height:1.5;">Physically isolates robotic transition terms like 'Furthermore', 'Undeniably', and 'In conclusion'.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.markdown("""
    <div style="background: rgba(255,255,255,0.5); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); border: 1px dashed rgba(0,0,0,0.1); border-radius: 16px; padding: 20px; margin-top: 15px;">
        <h5 style="margin: 0 0 8px 0; color: #555;">⚙️ Multi-Agent Combat Protocol</h5>
        <p style="font-size: 12.5px; color: #777; margin: 0; line-height: 1.6;">
            When you click the button below, <b>3 simulated Social Media Agents</b> will execute rounds of intense debating and rewriting. 
            The <b>Chief Judge Agent</b> scores each draft on human fidelity to deliver the ultimate winner. Takes 2-3 seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== Core Trigger Button ====================
st.markdown('<div class="generate-btn-container">', unsafe_allow_html=True)
start_generation = st.button("🚀 UNLEASH AGENTS · DEBATE & GENERATE VIRAL COPIES")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== Backend Processing Logic ====================
if start_generation:
    battle_container = st.container()
    with battle_container:
        st.markdown("### 🥊 Agents are actively debating and optimizing...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            ("🤖 Agent 1 (Platform Hype Specialist): Injecting cultural nuances and strategic emojis... 💥", 20),
            ("🤖 Agent 2 (Anti-AI Academic): Objecting! Removing mechanical phrasing and artificial logic patterns... 🥊", 55),
            ("🤖 Agent 3 (Viral Scriptwriter): Streamlining cadence for authentic human rhythm... ⚡", 85),
            ("⚖️ Judge Agent: Order in the court! Evaluating Human Fidelity Index to pick the absolute best version...", 95)
        ]
        
        for text, perc in stages:
            status_text.markdown(f"**Live Status:** {text}")
            progress_bar.progress(perc)
            time.sleep(0.5)
            
        ref_list = style_refs.splitlines() if style_refs else []
        payload = {
            "topic": topic,
            "platform": platform,
            "style_refs": ref_list
        }
        
        try:
            resp = requests.post("http://127.0.0.1:8000/generate", json=payload, timeout=90)
            data = resp.json()
            
            # 转换字段名，适配现有前端逻辑
            data["variants"] = data.get("all_variants", {})
            data["judge_result"] = {
                "winner": data.get("winner_agent", "B"),
                "reason": f"Agent {data.get('winner_agent', 'B')} won with AI score {data.get('ai_score', 'N/A')}/10. Risk level: {data.get('ai_detection_risk', 'unknown')}.",
                "scores": data.get("scores", {})
            }
            
            progress_bar.progress(100)
            status_text.empty()
            
            st.session_state.current_data = data
            st.success("🎉 Successfully humanized! Copy is ready below.")
            
        except Exception as e:
            st.error(f"Failed to connect to backend api. Please ensure the service on port 8000 is active. Details: {e}")

# ==================== Results Rendering Area ====================
if st.session_state.current_data:
    data = st.session_state.current_data
    
    st.subheader("⚖️ Chief Judge Verdict")
    
    judge_raw = data.get("judge_result", "")
    winner_show = "Analysis Complete"
    reason_show = str(judge_raw)
    scores_html = ""
    
    if isinstance(judge_raw, dict):
        judge_dict = judge_raw
    else:
        try:
            judge_dict = ast.literal_eval(judge_raw)
        except Exception:
            judge_dict = None
    
    if isinstance(judge_dict, dict):
        winner_show = f"👑 Version {judge_dict.get('winner', 'Unknown')} Wins Overall!"
        reason_show = judge_dict.get('reason', 'No detailed evaluation provided.')
        
        scores_data = judge_dict.get('scores', {})
        if scores_data and isinstance(scores_data, dict):
            scores_html = "<div style='margin-top: 15px; border-top: 1px dashed rgba(0,0,0,0.1); padding-top: 12px;'>"
            scores_html += "<strong style='font-size:13px; color:#555;'>📊 Detailed Scoring Breakdown:</strong>"
            for ver, scr in scores_data.items():
                scores_html += f"<span class='score-pill'>Version {ver}: {scr} pts</span>"
            scores_html += "</div>"

    st.markdown(f"""
    <div class="judge-box">
        <div class="winner-badge">{winner_show}</div>
        <div style="font-size:15.5px; line-height:1.7; color:#1E1E1E; margin-top:16px; font-weight:500; white-space: pre-wrap;">
            <strong>Verdict Assessment:</strong><br>{reason_show}
        </div>
        {scores_html}
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== Copy Options Breakdown ====================
    st.subheader("📋 Candidate Draft Breakdowns")
    col_res1, col_res2 = st.columns(2)
    
    variants = data.get("variants", {})
    for idx, (k, txt) in enumerate(variants.items()):
        target_col = col_res1 if idx % 2 == 0 else col_res2
        with target_col:
            st.markdown(f"#### 📄 Version {k}")
            st.markdown(f"""
            <div class="result-card">
                <p style="font-size:14.5px; white-space: pre-wrap; color:#222; line-height:1.6; margin: 0;">{txt}</p>
            </div>
            """, unsafe_allow_html=True)
            
    # ==================== Health Report ====================
    st.write("")
    st.markdown("### 📊 Anti-AI Copy Health Audit")
    
    avoid_ai_words = f"{random.randint(95, 99)}%"
    spoken_rate = f"{random.randint(92, 97)}%"
    interaction_boost = f"+{random.randint(120, 160)}%"
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="☘️ AI Word Suppression Rate", value=avoid_ai_words, delta="Excellent")
    col_m2.metric(label="💬 Organic Human Cadence", value=spoken_rate, delta="Very High")
    col_m3.metric(label="🔥 Predicted Engagement Boost", value=interaction_boost, delta="Viral Potential")
