import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document
import re

# 1. إعدادات الهوية والوضوح
st.set_page_config(page_title="Asharq Analytics Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background: #1e293b !important; border: 1px solid #3b82f6 !important; border-radius: 12px; padding: 20px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.8rem !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك التطهير اللغوي النهائي (V28) ---
def advanced_clean_name(text):
    if pd.isna(text) or text == "": return "غير معروف"
    
    # تحويل لنص وتنظيف الرموز وعلامات التنصيص والنقاط
    name = str(text).strip()
    name = re.sub(r'["\'.\.،,]', '', name) # حذف النقاط وعلامات التنصيص
    name = re.sub(r'[-–—|/:_]', ' ', name)
    
    # 1. كلمات يجب حذفها بالكامل لأنها ليست أسماء
    black_list = [
        "موفد", "وفد", "هجمات", "متكرره", "واشنطن", "تؤكد", "الشرق", 
        "عاجل", "خاص", "مراسل", "مراسلة", "من", "في", "قناة"
    ]
    
    # 2. بتر الزوائد الوظيفية والجغرافية
    patterns = [r"مراسل.*", r"مراسلة.*", r"مدير.*", r"خبير.*", r"من\s.*", r"في\s.*"]
    for p in patterns:
        name = re.sub(p, "", name)
    
    # 3. توحيد الحروف الحرج
    name = re.sub(r"[أإآ]", "ا", name)
    name = re.sub(r"ة", "ه", name)
    name = re.sub(r"ى", "ي", name)
    
    # 4. دمج المسافات بأسماء "عبد"
    name = re.sub(r"عبد\s+", "عبد", name)
    
    # 5. تنظيف المسافات الزائدة
    parts = name.split()
    
    # حذف الكلمات السوداء من داخل الأجزاء
    parts = [p for p in parts if p not in black_list]
    
    # إذا لم يتبق شيء أو كانت كلمة واحدة غير منطقية
    if not parts or len(parts) < 2:
        # محاولة أخيرة: إذا كانت كلمة واحدة معروفة كاسم نتركها، وإلا نهملها
        return " ".join(parts).strip() if parts else "بيانات غير صالحة"
    
    # نأخذ أول كلمتين (الاسم الثنائي) لضمان أعلى دقة تجميع
    return " ".join(parts[:2]).strip()

def clean_num(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if res else 0

@st.cache_data
def ultra_parser(files):
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
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(advanced_clean_name)
                        pool['r'].append(df)
                    elif any("الضيف" in c for c in cols):
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(advanced_clean_name)
                        pool['g'].append(df)
        except: continue
    return pool

# --- الواجهة ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>ASHARQ <span style='color:white'>ANALYTICS HUB</span></h1>", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader("📂 ارفع ملفاتك (Docx):", type="docx", accept_multiple_files=True)

if uploaded:
    data = ultra_parser(uploaded)
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()
    df_g = pd.concat(data['g']) if data['g'] else pd.DataFrame()

    tabs = st.tabs(["📊 الملخص", "🌟 النجوم والموارد", "📥 التصدير"])

    with tabs[1]:
        st.markdown("### 🌟 تحليل الكوادر (نسخة التنقية النهائية)")
        cat = st.selectbox("الفئة:", ["🎙️ المراسلين", "👥 الضيوف"])
        target = df_r if cat == "🎙️ المراسلين" else df_g
        
        if not target.empty:
            # فلترة الأسماء غير الصالحة (مثل "موفد") من القائمة
            invalid_entries = ["بيانات غير صالحة", "غير معروف", "موفد", "وفد"]
            clean_list = sorted([n for n in target['اسم_نظيف'].unique() if n not in invalid_entries])
            
            selected_name = st.selectbox("اختر الاسم:", clean_list)
            p_data = target[target['اسم_نظيف'] == selected_name]
            
            st.metric(f"إجمالي نشاط {selected_name}", int(p_data['Count'].sum() if 'Count' in p_data.columns else len(p_data)))
            st.dataframe(p_data[['Source']], use_container_width=True)

else:
    st.info("💎 ارفع الملفات لتشغيل المحرك المحدث.")
