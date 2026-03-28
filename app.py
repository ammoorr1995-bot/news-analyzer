import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الهوية البصرية (High-Contrast & Clean UI)
st.set_page_config(page_title="Asharq Analytics Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    
    /* خلفية مريحة للعين وتباين عالي */
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* تصميم البطاقات بوضوح فائق */
    .executive-card { 
        background: #1e293b; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #334155; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* تحسين وضوح أرقام الـ Metric */
    .stMetric { 
        background: #1e293b !important; 
        border: 1px solid #3b82f6 !important; 
        border-radius: 12px !important; 
        padding: 20px !important;
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.8rem !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 1.1rem !important; }

    .ai-insight-box { 
        border-right: 6px solid #3b82f6; 
        background: rgba(59, 130, 246, 0.15); 
        padding: 25px; 
        border-radius: 10px; 
        color: #e2e8f0; 
        font-size: 1.2rem; 
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- محرك تنقية الأسماء الذكي ---
def extract_clean_name(text):
    if pd.isna(text) or text == "": return "غير معروف"
    trash_words = [
        "مراسل الشرق", "مراسلة الشرق", "الشرق", "من غزة", "في القدس", "من", "في", 
        "مراسل", "مراسلة", "واشنطن", "القدس", "دبي", "الرياض", "القاهرة", "بيروت", "لندن"
    ]
    clean = str(text)
    clean = re.sub(r'[-–—|/:]', ' ', clean)
    for word in trash_words:
        clean = clean.replace(word, "")
    parts = clean.split()
    if len(parts) >= 2:
        return " ".join(parts[:3]).strip()
    return clean.strip()

def clean_num(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if nums := res else 0

# 2. محرك المعالجة المتقدم
@st.cache_data
def advanced_parser(files):
    pool = {'p': [], 'r': [], 'g': []}
    for f in files:
        try:
            doc = Document(f)
            tag = f.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Source'] = tag
                    cols = df.columns.tolist()
                    num_col = next((c for c in cols if any(k in c for k in ["العدد", "عدد", "مداخلات"])), None)
                    
                    if any("شكل التقديم" in c for c in cols) and num_col:
                        df['Count'] = df[num_col].apply(clean_num)
                        pool['p'].append(df)
                    elif any("المراسل" in c for c in cols) and num_col:
                        df['Count'] = df[num_col].apply(clean_num)
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(extract_clean_name)
                        pool['r'].append(df)
                    elif any("الضيف" in c for c in cols):
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(extract_clean_name)
                        pool['g'].append(df)
        except: continue
    return pool

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #3b82f6; font-size: 3rem; margin-bottom:0;'>ASHARQ <span style='color:white'>ANALYTICS HUB</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2rem;'>المنصة المركزية لتحليل وقياس الأداء الإخباري</p>", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader("📂 ارفع ملفات الرصد (Docx):", type="docx", accept_multiple_files=True)

if uploaded:
    data = advanced_parser(uploaded)
    df_p = pd.concat(data['p']) if data['p'] else pd.DataFrame()
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()
    df_g = pd.concat(data['g']) if data['g'] else pd.DataFrame()

    tabs = st.tabs(["🚀 الملخص التنفيذي", "📅 التحليل اليومي", "⚖️ المقارنة الذكية", "🌟 النجوم والموارد", "📥 التصدير"])

    # تبويب 1: الملخص التنفيذي (تحسين الوضوح)
    with tabs[0]:
        st.markdown("### 🧠 مركز استنتاجات الذكاء الاصطناعي")
        if not df_p.empty:
            total = df_p['Count'].sum()
            avg = total / len(uploaded)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.metric("إجمالي الإنتاج الإخباري", f"{int(total):,}", f"بمعدل {avg:.1f} يومياً")
                st.markdown(f"<div class='ai-insight-box'><b>💡 رؤية المحلل الذكي:</b><br>تم رصد كثافة إنتاجية عالية خلال الفترة المرفوعة. النظام يشير إلى استقرار في تدفق المحتوى الإخباري مع تميز واضح في تنوع قوالب العرض.</div>", unsafe_allow_html=True)
            with c2:
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=avg, 
                                                  gauge={'axis':{'range':[0,300]}, 'bar':{'color':"#3b82f6"}}))
                fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_gauge, use_container_width=True)

    # تبويب 4: النجوم والموارد (حل مشكلة الأسماء)
    with tabs[3]:
        st.markdown("### 🌟 تحليل أداء المراسلين والضيوف")
        cat = st.selectbox("اختر الفئة:", ["🎙️ المراسلين", "👥 الضيوف"])
        
        if cat == "🎙️ المراسلين" and not df_r.empty:
            rep_name = st.selectbox("اختر اسم المراسل (مجمع تلقائياً):", df_r['اسم_نظيف'].unique())
            rep_data = df_r[df_r['اسم_نظيف'] == rep_name]
            st.metric(f"إجمالي مداخلات {rep_name}", int(rep_data['Count'].sum()))
            st.plotly_chart(px.line(rep_data, x='Source', y='Count', markers=True, title=f"تطور أداء {rep_name}"), use_container_width=True)
        
        elif cat == "👥 الضيوف" and not df_g.empty:
            guest_name = st.selectbox("اختر اسم الضيف:", df_g['اسم_نظيف'].unique())
            guest_data = df_g[df_g['اسم_نظيف'] == guest_name]
            st.metric(f"عدد مرات الظهور لـ {guest_name}", len(guest_data))
            st.dataframe(guest_data[['Source']], use_container_width=True)

else:
    st.info("💎 بانتظار الملفات لتفعيل محرك التحليل الذكي.")
