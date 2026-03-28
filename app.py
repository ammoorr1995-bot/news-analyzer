import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(page_title="Asharq News Analytics", layout="wide", page_icon="🌐")

# تصميم CSS احترافي للبطاقات والمقارنات
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .hero-banner { background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); color: white; padding: 30px 20px; border-radius: 10px; text-align: center; margin-bottom: 25px; }
    .hero-banner h1 { color: #ffffff !important; font-size: 2.5em; margin-bottom: 5px; font-weight: 700; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-right: 4px solid #1976d2; text-align: center; }
    h3 { color: #0d47a1; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. دالة استخراج البيانات الشاملة
@st.cache_data
def process_files(uploaded_files):
    all_data = {'presentation': [], 'category': [], 'reporters': [], 'guests': [], 'officials': [], 'hourly': []}
    
    for file in uploaded_files:
        try:
            doc = Document(file)
            report_name = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    cols = df.columns.tolist()
                    df['التقرير'] = report_name
                    
                    if 'شكل التقديم' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['presentation'].append(df[['التقرير', 'شكل التقديم', 'العدد']])
                    elif 'التصنيف' in cols and 'العدد' in cols and 'شكل التقديم' not in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['category'].append(df[['التقرير', 'التصنيف', 'العدد']])
                    elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                        df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                        all_data['reporters'].append(df[['التقرير', 'المراسل/الصحفي', 'عدد المداخلات']])
                    elif 'الضيف' in cols and 'الصفة' in cols:
                        all_data['guests'].append(df)
                    elif 'المسؤول' in cols and 'الصفة' in cols:
                        all_data['officials'].append(df)
                    elif 'الساعة' in cols and 'العدد' in cols: # معالجة جداول الساعات إن وجدت
                        df['العدد'] = pd.to_numeric(df['العدد'], errors='coerce').fillna(0)
                        if 'التصنيف' in cols:
                            all_data['hourly'].append(df[['التقرير', 'الساعة', 'التصنيف', 'العدد']])
                        else:
                            all_data['hourly'].append(df[['التقرير', 'الساعة', 'العدد']])
        except Exception:
            continue
    return all_data

# 3. القائمة الجانبية وصندوق الرفع الآمن
st.sidebar.markdown("## 🌐 قناة الشرق | تحليلات")
st.sidebar.markdown("---")
uploaded_files = st.sidebar.file_uploader("📥 ارفع تقارير الوورد هنا:", type="docx", accept_multiple_files=True)
st.sidebar.info("🔒 تعالج البيانات محلياً وبشكل آمن.")

# معالجة البيانات
df_p, df_c, df_r, df_g, df_o, df_h = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
if uploaded_files:
    data = process_files(uploaded_files)
    if data['presentation']: df_p = pd.concat(data['presentation'])
    if data['category']: df_c = pd.concat(data['category'])
    if data['reporters']: df_r = pd.concat(data['reporters'])
    if data['guests']: df_g = pd.concat(data['guests'])
    if data['officials']: df_o = pd.concat(data['officials'])
    if data['hourly']: df_h = pd.concat(data['hourly'])

    report_names = [f.name.replace('.docx', '') for f in uploaded_files]
else:
    report_names = []

# ==========================================
# الهيكل الرئيسي والتنقل
# ==========================================
st.markdown('<div class="hero-banner"><h1>منصة التحليلات الإخبارية</h1><p>لوحة تحكم تفاعلية متقدمة لتحويل تقارير الرصد إلى قرارات</p></div>', unsafe_allow_html=True)

if not uploaded_files:
    st.warning("👈 يرجى رفع ملفات الوورد من القائمة الجانبية للبدء (ارفع ملف اليوم والأمس لتفعيل المقارنات).")
else:
    tab1, tab2, tab3 = st.tabs(["📊 التقرير اليومي المفصل", "⚖️ مقارنة مع اليوم السابق", "🗄️ استكشاف البيانات"])

    # ----------------------------------------------------------------------
    # التبويب الأول: التقرير اليومي المفصل (اليوم الحالي)
    # ----------------------------------------------------------------------
    with tab1:
        st.markdown("### 📅 اختر التقرير لعرض تحليله المفصل:")
        selected_report = st.selectbox("", report_names, key="daily_rep")
        
        # فلترة البيانات لليوم المختار
        d_p = df_p[df_p['التقرير'] == selected_report] if not df_p.empty else pd.DataFrame()
        d_c = df_c[df_c['التقرير'] == selected_report] if not df_c.empty else pd.DataFrame()
        d_r = df_r[df_r['التقرير'] == selected_report] if not df
