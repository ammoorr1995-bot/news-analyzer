import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الهوية البصرية (High Contrast)
st.set_page_config(page_title="Asharq Analytics Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background: #1e293b !important; border: 1px solid #3b82f6 !important; border-radius: 12px !important; padding: 20px !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.8rem !important; font-weight: 800 !important; }
    .ai-insight-box { border-right: 6px solid #3b82f6; background: rgba(59, 130, 246, 0.15); padding: 20px; border-radius: 10px; color: #f1f5f9; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك التطهير اللغوي (Advanced Normalization) ---
def normalize_name(text):
    if pd.isna(text) or text == "": return "غير معروف"
    
    name = str(text).strip()
    
    # 1. إزالة الألقاب والجهات (بتر صارم)
    # نحذف كل ما بعد الكلمات المفتاحية الوظيفية
    patterns = [r"مراسل.*", r"مدير.*", r"خبير.*", r"محلل.*", r"من\s.*", r"في\s.*", r"الشرق.*"]
    for p in patterns:
        name = re.sub(p, "", name)
    
    # 2. تنظيف الرموز
    name = re.sub(r'[-–—|/:،,]', ' ', name)
    
    # 3. توحيد الحروف العربية (إدارة التباين اللغوي)
    name = re.sub(r"[أإآ]", "ا", name)
    name = re.sub(r"ة", "ه", name)
    name = re.sub(r"ى", "ي", name)
    
    # 4. معالجة المسافات الحرجة (مثل عبدالله و عبد الله)
    # نحذف المسافات بين "عبد" والاسم الذي يليها
    name = re.sub(r"عبد\s+", "عبد", name)
    
    # 5. تنظيف المسافات المزدوجة
    name = " ".join(name.split())
    
    # 6. اقتطاع الاسم (أول كلمتين غالباً هما الاسم الأساسي)
    parts = name.split()
    if len(parts) >= 2:
        return " ".join(parts[:2]).strip()
    
    return name if name else "غير معروف"

def clean_num(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if res else 0

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
                        # تطبيق التطهير اللغوي
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(normalize_name)
                        pool['r'].append(df)
                    elif any("الضيف" in c for c in cols):
                        df['اسم_نظيف'] = df.iloc[:, 0].apply(normalize_name)
                        pool['g'].append(df)
        except: continue
    return pool

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>ASHARQ <span style='color:white'>ANALYTICS HUB</span></h1>", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader("📂 ارفع ملفات الرصد (Docx):", type="docx", accept_multiple_files=True)

if uploaded:
    data = advanced_parser(uploaded)
    df_p = pd.concat(data['p']) if data['p'] else pd.DataFrame()
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()
    df_g = pd.concat(data['g']) if data['g'] else pd.DataFrame()

    tabs = st.tabs(["🚀 الملخص التنفيذي", "📅 التحليل اليومي", "🌟 النجوم والموارد", "📥 تصدير"])

    with tabs[2]:
        st.markdown("### 🌟 تحليل الكوادر (تجميع ذكي متطور)")
        cat = st.selectbox("اختر الفئة:", ["🎙️ المراسلين", "👥 الضيوف"])
        
        target_df = df_r if cat == "🎙️ المراسلين" else df_g
        
        if not target_df.empty:
            # ترتيب الأسماء أبجدياً لتسهيل البحث
            clean_list = sorted(target_df['اسم_نظيف'].unique())
            selected_name = st.selectbox("اختر الاسم (تم الدمج لغوياً):", clean_list)
            
            personal_data = target_df[target_df['اسم_نظيف'] == selected_name]
            
            c1, c2 = st.columns([1, 2])
            with c1:
                total_val = personal_data['Count'].sum() if 'Count' in personal_data.columns else len(personal_data)
                st.metric(f"إجمالي نشاط {selected_name}", int(total_val))
            with c2:
                st.write("**سجل التواجد في التقارير:**")
                st.dataframe(personal_data[['Source']], use_container_width=True)

    with tabs[0]:
        if not df_p.empty:
            total = df_p['Count'].sum()
            st.metric("إجمالي المواد المرصودة", f"{int(total):,}")
            st.plotly_chart(px.bar(df_p.groupby('شكل التقديم')['Count'].sum().reset_index(), x='Count', y='شكل التقديم', orientation='h', template="plotly_dark"), use_container_width=True)

else:
    st.info("💎 ارفع ملفاتك لتفعيل محرك التطهير اللغوي والتحليل الاستراتيجي.")
