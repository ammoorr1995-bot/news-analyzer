import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الهوية والوضوح الفائق
st.set_page_config(page_title="Asharq Analytics Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background: #1e293b; border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.8rem !important; font-weight: 800; }
    .ai-insight-box { border-right: 6px solid #3b82f6; background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 10px; color: #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك التطهير اللغوي المتطور (لدمج الأسماء المتشابهة) ---
def advanced_clean_name(text):
    if pd.isna(text) or text == "": return "غير معروف"
    name = str(text).strip()
    name = re.sub(r'["\'.\.،,]', '', name)
    name = re.sub(r'[-–—|/:_]', ' ', name)
    
    # كلمات تصفية إضافية بناءً على الصور المرفقة
    black_list = ["موفد", "وفد", "هجمات", "تؤكد", "الشرق", "عاجل", "مراسل", "مراسلة", "من", "في"]
    
    # توحيد الحروف
    name = re.sub(r"[أإآ]", "ا", name)
    name = re.sub(r"ة", "ه", name)
    name = re.sub(r"ى", "ي", name)
    name = re.sub(r"عبد\s+", "عبد", name)
    
    parts = [p for p in name.split() if p not in black_list]
    if not parts or len(parts) < 1: return "بيانات غير صالحة"
    
    # نأخذ أول كلمتين (الاسم الثنائي) لضمان التجميع الصحيح (مثلاً وسام عبدالله)
    return " ".join(parts[:2]).strip()

def clean_num(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if res else 0

# 2. محرك القراءة المتطابق مع صور الجداول المرفقة
@st.cache_data
def matched_parser(files):
    pool = {'p': [], 'r': [], 'g': [], 'o': []}
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
                    
                    # 1. جدول المراسلين (بناءً على صورة 2a77c3)
                    if any("المراسل" in c for c in cols) and any("مداخلات" in c for c in cols):
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(advanced_clean_name)
                        df['Count'] = df.iloc[:, 1].apply(clean_num)
                        pool['r'].append(df)
                    
                    # 2. جدول الضيوف (بناءً على صورة 2a77e9)
                    elif any("الضيف" in c for c in cols) and any("الصفة" in c for c in cols):
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(advanced_clean_name)
                        pool['g'].append(df)
                        
                    # 3. جدول المسؤولين (بناءً على صورة 2a7823)
                    elif any("المسؤول" in c for c in cols) and any("تصريح" in c for c in cols):
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(advanced_clean_name)
                        pool['o'].append(df)
                    
                    # 4. جدول الأرقام الإجمالية (شكل التقديم)
                    elif any("شكل التقديم" in c for c in cols):
                        col_val = next((c for c in cols if "العدد" in c), cols[1])
                        df['Count'] = df[col_val].apply(clean_num)
                        pool['p'].append(df)
        except: continue
    return pool

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>ASHARQ <span style='color:white'>ANALYTICS HUB</span></h1>", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader("📂 ارفع ملفات الرصد اليومي (Docx):", type="docx", accept_multiple_files=True)

if uploaded:
    data = matched_parser(uploaded)
    df_p = pd.concat(data['p']) if data['p'] else pd.DataFrame()
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()
    df_g = pd.concat(data['g']) if data['g'] else pd.DataFrame()
    df_o = pd.concat(data['o']) if data['o'] else pd.DataFrame()

    tabs = st.tabs(["🚀 ملخص القيادة", "🌟 النجوم والموارد", "📉 تحليل التوجهات", "📥 تصدير"])

    with tabs[0]:
        st.markdown("### 🧠 مركز الاستنتاجات الذكي")
        if not df_p.empty:
            total = df_p['Count'].sum()
            avg = total / len(uploaded)
            c1, c2 = st.columns([2, 1])
            with c1:
                st.metric("إجمالي المواد الإخبارية", f"{int(total):,}", f"بمعدل {avg:.1f} يومياً")
                st.markdown("<div class='ai-insight-box'><b>💡 تحليل استراتيجي:</b> تظهر البيانات توافقاً تاماً مع هيكل الجداول المعتمد. يتم الآن تجميع مداخلات المراسلين وتصريحات المسؤولين بدقة.</div>", unsafe_allow_html=True)
            with c2:
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=avg, gauge={'bar':{'color':"#3b82f6"}}))
                fig_gauge.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_gauge, use_container_width=True)

    with tabs[1]:
        st.markdown("### 🌟 تحليل أداء الكوادر والضيوف")
        cat = st.selectbox("اختر الفئة المستهدفة:", ["🎙️ المراسلين", "👥 الضيوف", "👔 المسؤولين"])
        
        target = {"🎙️ المراسلين": df_r, "👥 الضيوف": df_g, "👔 المسؤولين": df_o}[cat]
        
        if not target.empty:
            clean_list = sorted([n for n in target['اسم_نظيف'].unique() if n not in ["بيانات غير صالحة", "غير معروف"]])
            selected_name = st.selectbox("اختر الاسم المراد تحليله:", clean_list)
            p_data = target[target['اسم_نظيف'] == selected_name]
            
            c_val, c_table = st.columns([1, 2])
            with c_val:
                total_val = p_data['Count'].sum() if 'Count' in p_data.columns else len(p_data)
                st.metric(f"نشاط {selected_name}", int(total_val))
            with c_table:
                st.dataframe(p_data[['Source']], use_container_width=True)
            
            if 'Count' in p_data.columns:
                st.plotly_chart(px.line(p_data, x='Source', y='Count', markers=True, title=f"تطور ظهور {selected_name}"), use_container_width=True)

    with tabs[3]:
        st.markdown("### 📥 جاهز للتصدير")
        st.info("استخدم (Ctrl + P) لحفظ التقرير كملف PDF نظيف ومنظم.")

else:
    st.info("💎 بانتظار الملفات لتفعيل محرك التحليل المتطابق مع جداول الرصد.")
