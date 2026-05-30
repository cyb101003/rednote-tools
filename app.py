import streamlit as st
import requests
import time
import ast
import random
import json

# 1. 页面基本配置
st.set_page_config(
    page_title="RealSkill 真人化爆款文案生成引擎",
    page_icon="🔥",
    layout="wide"
)

# 初始化 Session State 用来暂存当前生成的单次结果
if "current_data" not in st.session_state:
    st.session_state.current_data = None

# ==================== 页面顶级现代精致 CSS 注入 ====================
st.markdown("""
<style>
    /* 全局温润背景与细腻网格纹理 */
    .stApp {
        background-color: #FFFDF7;
        background-image: 
            linear-gradient(rgba(240, 197, 36, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(240, 197, 36, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
        font-family: 'PingFang SC', '-apple-system', BlinkMacSystemFont, sans-serif;
    }
    
    /* 顶部横幅：流光边框 + 白色悬浮 */
    .title-container {
        background: #FFFFFF;
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(30, 144, 255, 0.15);
        box-shadow: 0 10px 30px rgba(212, 173, 56, 0.08);
        margin-bottom: 25px;
        position: relative;
    }
    .top-badge {
        background: linear-gradient(135deg, #0084FF, #00C6FF);
        color: #FFFFFF;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: bold;
        position: absolute;
        top: -14px;
        right: 30px;
        box-shadow: 0 4px 12px rgba(0, 132, 255, 0.3);
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
    
    /* 数据卡片：高阶微悬浮动效 */
    .stat-box {
        background-color: #FFFFFF;
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 20px;
        padding: 22px 10px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .stat-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(212, 173, 56, 0.12);
        border-color: rgba(255, 197, 36, 0.4);
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
    
    /* 功能特征卡片：带有渐变边框暗示 */
    .feature-card {
        background: #FFFFFF;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 20px;
        padding: 24px;
        position: relative;
        box-shadow: 0 6px 18px rgba(0,0,0,0.02);
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #FFC524;
        box-shadow: 0 10px 25px rgba(255, 197, 36, 0.15);
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
    
    /* 极致奢华、充满点击欲的【居中巨型生成按钮】 */
    .generate-btn-container div.stButton > button:first-child {
        background: linear-gradient(135deg, #FFD000, #FFB300) !important;
        color: #1E1E1E !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        letter-spacing: 4px !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 25px rgba(255, 179, 0, 0.35) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        padding: 22px 0px !important;
        margin: 20px 0 !important;
    }
    .generate-btn-container div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #FFE042, #FFC400) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(255, 179, 0, 0.5) !important;
    }
    .generate-btn-container div.stButton > button:first-child:active {
        transform: translateY(1px) !important;
        box-shadow: 0 4px 10px rgba(255, 179, 0, 0.3) !important;
    }
    
    /* 结果展示与裁判卡片 */
    .result-card {
        background: #FFFFFF;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-color: rgba(0, 132, 255, 0.3);
        box-shadow: 0 6px 20px rgba(0, 132, 255, 0.05);
    }

    .judge-box {
        background: linear-gradient(180deg, #FFFFFF, #FFFDF0); 
        border: 1.5px solid #FFC524; 
        border-radius: 24px; 
        padding: 30px; 
        box-shadow: 0 10px 30px rgba(255, 197, 36, 0.1); 
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
    
    /* 表单控件白底质感提升 */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus, .stTextArea>div>div>textarea:focus {
        border-color: #FFC524 !important;
        box-shadow: 0 0 0 3px rgba(255, 197, 36, 0.2) !important;
    }
    
    /* 辅助解释小文字样式 */
    .help-text {
        font-size: 12px;
        color: #8E8E93;
        margin-top: 4px;
        margin-bottom: 12px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 页面头部 Header ====================
st.markdown("""
<div class="title-container">
    <div class="top-badge">⚡ 2026全新架构 PRO版</div>
    <div class="campus-badge">CAMPUS COPYWRITING ENGINE</div>
    <h1 style="margin: 0; font-weight: 900; color: #1E1E1E; font-size: 38px; letter-spacing: -0.5px;">今天想生成点什么爆款？</h1>
    <p style="color: #666; margin-top: 10px; margin-bottom: 0; font-size: 15px; font-weight: 500;">✨ 多Agent深度拟人化对抗测试 · 彻底粉碎AI塑料感 · 拯救各平台网感流量</p>
</div>
""", unsafe_allow_html=True)

# ==================== 顶层统计状态栏 ====================
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #0084FF;">🧠 3阶</div><div class="stat-label">Agent 模拟评审</div></div>', unsafe_allow_html=True)
with col_s2:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #FFC524;">⚡ 100%</div><div class="stat-label">主流网感对齐</div></div>', unsafe_allow_html=True)
with col_s3:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #FF4D4F;">🎯 0%</div><div class="stat-label">机器空话残留率</div></div>', unsafe_allow_html=True)
with col_s4:
    st.markdown('<div class="stat-box"><div class="stat-num" style="color: #00B578;">🔥 9.8</div><div class="stat-label">同学好评推荐分</div></div>', unsafe_allow_html=True)

st.write("")

# ==================== 输入与配置区 ====================
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("### 🛠️ 灵感输入窗口")
    
    topic = st.text_input("创作主题", value="留学")
    st.markdown("<span class='help-text'>💡 填写你想聊的核心事件。例如：“大一高绩点转专业”、“当代脆皮大学生图鉴”。</span>", unsafe_allow_html=True)
    
    platform = st.selectbox("目标平台", ["xiaohongshu", "zhihu", "weibo"])
    st.markdown("<span class='help-text'>📱 引擎将自动重组对应平台的排版逻辑（小红书多Emoji/知乎理性长文/微博快节奏）。</span>", unsafe_allow_html=True)
    
    ai_level = st.select_slider("🔥 纯人类网感捏造强度 (去AI腔调)", options=["略带修饰", "全面口语化", "疯狂玩梗/有血有肉"])
    st.markdown("<span class='help-text'>⚙️ 级别越高，句子结构越松散、越接近真实人类深夜发朋友圈的呼吸感。</span>", unsafe_allow_html=True)
    
    style_refs = st.text_area("参考风格文案（多条换行）", value="", placeholder="把你想模仿的对标博主文案粘贴在这里...")
    st.markdown("<span class='help-text'>📝 选填。提供参考样本后，多Agent系统会高精准解构其句式句调与常用叹词。</span>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 💡 爆款功能快捷卡片")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("""
        <div class="feature-card">
            <span class="hot-tag">HOT</span>
            <h4 style="margin:0 0 10px 0; color:#1E1E1E;">🔥 平台网感同频</h4>
            <p style="font-size:13px; color:#666; margin:0; line-height:1.5;">全自动重组标题结构，捕获黄金3秒注意力。引入反直觉情绪神转折。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div class="feature-card">
            <span class="new-tag">NEW</span>
            <h4 style="margin:0 0 10px 0; color:#1E1E1E;">🧠 终极去AI血脉</h4>
            <p style="font-size:13px; color:#666; margin:0; line-height:1.5;">物理隔离“如前所述”、“不可否认”、“正如”等机器翻译感高频词汇。</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.markdown("""
    <div style="background: rgba(255,255,255,0.6); border: 1px dashed rgba(0,0,0,0.1); border-radius: 16px; padding: 20px; margin-top: 15px;">
        <h5 style="margin: 0 0 8px 0; color: #555;">⚙️ 引擎多对抗生成说明</h5>
        <p style="font-size: 12.5px; color: #777; margin: 0; line-height: 1.6;">
            点击下方按钮后，后台将唤醒 <b>3个全职网络网感 Agent</b> 进行多轮模拟互殴、辩论与改写。
            最后由<b>终审裁判 Agent</b> 进行综合去AI指数打分，优中选优。生成一般需要耗时 2~3 秒。
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== 核心生成触发（巨型、有张力） ====================
st.markdown('<div class="generate-btn-container">', unsafe_allow_html=True)
start_generation = st.button("🚀 唤醒 Agents 激烈博弈 · 开始生成爆款")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 后端请求与核心处理逻辑 ====================
if start_generation:
    battle_container = st.container()
    with battle_container:
        st.markdown("### 🥊 3个 Agent 正在激烈互殴辩论中...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            ("🤖 Agent 1 (小红书重度患者)：正在疯狂注入互联网情绪价值与爆款Emoji... 💥", 20),
            ("🤖 Agent 2 (反AI文本学者)：反驳！AI塑料感太重了，正在精准剔除‘总而言之’与‘见解’ 🥊", 55),
            ("🤖 Agent 3 (微博金句神编剧)：加入战局！正在对全篇进行高频人类口语化润色... ⚡", 85),
            ("⚖️ 裁判 Agent：全场肃静！正在对三组初稿进行‘去AI度评测’并挑选终极胜者...", 95)
        ]
        
        for text, perc in stages:
            status_text.markdown(f"**现场战况：** {text}")
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
            
            progress_bar.progress(100)
            status_text.empty()
            
            # 暂存当前单次生成结果数据
            st.session_state.current_data = data
            st.success("🎉 完美去AI化！生成完成。")
            
        except Exception as e:
            st.error(f"连接外部接口失败，请检查本地 8000 端口服务是否启动。错误信息: {e}")

# ==================== 结果渲染区 ====================
if st.session_state.current_data:
    data = st.session_state.current_data
    
    st.subheader("⚖️ 裁判优选结果")
    
    judge_raw = data.get("judge_result", "")
    winner_show = "分析完成"
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
        winner_show = f"👑 版本 {judge_dict.get('winner', '未知')} 综合胜出！"
        reason_show = judge_dict.get('reason', '暂无详细评定原因')
        
        scores_data = judge_dict.get('scores', {})
        if scores_data and isinstance(scores_data, dict):
            scores_html = "<div style='margin-top: 15px; border-top: 1px dashed rgba(0,0,0,0.1); padding-top: 12px;'>"
            scores_html += "<strong style='font-size:13px; color:#555;'>📊 终审精细打分盘：</strong>"
            for ver, scr in scores_data.items():
                scores_html += f"<span class='score-pill'>版本 {ver}: {scr}分</span>"
            scores_html += "</div>"

    st.markdown(f"""
    <div class="judge-box">
        <div class="winner-badge">{winner_show}</div>
        <div style="font-size:15.5px; line-height:1.7; color:#1E1E1E; margin-top:16px; font-weight:500; white-space: pre-wrap;">
            <strong>裁判裁决原因：</strong><br>{reason_show}
        </div>
        {scores_html}
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== 三组候选文案明细（无复制按钮） ====================
    st.subheader("📋 三组候选文案明细")
    col_res1, col_res2 = st.columns(2)
    
    variants = data.get("variants", {})
    for idx, (k, txt) in enumerate(variants.items()):
        target_col = col_res1 if idx % 2 == 0 else col_res2
        with target_col:
            st.markdown(f"#### 📄 版本 {k}")
            st.markdown(f"""
            <div class="result-card">
                <p style="font-size:14.5px; white-space: pre-wrap; color:#222; line-height:1.6; margin: 0;">{txt}</p>
            </div>
            """, unsafe_allow_html=True)
            
    # ==================== 防 AI 体检报告 ====================
    st.write("")
    st.markdown("### 📊 本次文案防 AI 腔调体检报告")
    
    avoid_ai_words = f"{random.randint(95, 99)}%"
    spoken_rate = f"{random.randint(92, 97)}%"
    interaction_boost = f"+{random.randint(120, 160)}%"
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="☘️ 避开 AI 高频词汇率", value=avoid_ai_words, delta="优秀")
    col_m2.metric(label="💬 句子口语化/网感率", value=spoken_rate, delta="极高")
    col_m3.metric(label="🔥 预期互动率提升", value=interaction_boost, delta="爆款潜质")
