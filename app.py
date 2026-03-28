import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document

# 1. إعدادات المنصة العالمية
st.set_page_config(page_title="Asharq AI Analytics Pro", layout="wide", page_icon="💎")

# تصميم CSS فاخر (Dark & Modern UI)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .metric-card { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; text-align: center; transition: 0.3s; }
    .metric-card:hover { border-color: #3b82f6; transform: translateY(-5px); }
    .ai-insight { background: rgba(59, 130, 246, 0.1); border-right: 5px solid #3b82f6; padding: 15px; border-radius: 5px; margin: 10px 0; }
    h1, h2, h3 { color: #f1f5f9; font-weight: 800; }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric [data-testid="stMetricValue"] { color: #3b82f6 !important; font-size: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. محرك معالجة البيانات الفائق
@st.cache_data
def ultra_data_engine(uploaded_files):
    storage = {'p': [], 'r': [], 'g': [], 'c': [], 'h': []}
    for file in uploaded_files:
        try:
            doc = Document(file)
            fname = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Date_Ref'] = fname
                    cols = df.columns.tolist()
                    if 'شكل التقديم' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        storage['p'].append(df)
                    elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                        df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                        storage['r'].append(df)
                    elif 'الضيف' in cols: storage['g'].append(df)
                    elif 'التصنيف' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        storage['c'].append(df)
        except: continue
    return storage

# 3. الواجهة الرئيسية (Hero Section)
st.markdown("<h1 style='text-align: center; font-size: 3.5rem;'>💎 Asharq Analytics <span style='color:#3b82f6;'>Ultra</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>الجيل القادم من تحليلات غرف الأخبار المدعومة بالبيانات</p>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📂 اسحب تقاريرك هنا (docx):", type="docx", accept_multiple_files=True)

if files:
    raw = ultra_data_engine(files)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()
    df_g = pd.concat(raw['g']) if raw['g'] else pd.DataFrame()
    df_c = pd.concat(raw['c']) if raw['c'] else pd.DataFrame()

    # --- القسم الأول: لوحة التحكم الذكية (Smart Cards) ---
    st.markdown("### 🧠 استنتاجات الذكاء التحليلي")
    c1, c2, c3 = st.columns(3)
    
    if not df_p.empty:
        total_mats = int(df_p['العدد'].sum())
        avg_mats = total_mats / len(files)
        c1.metric("إجمالي المواد", f"{total_mats:,}", f"بمتوسط {avg_mats:.1f} لكل تقرير")
        
        # AI Insight 1: اكتشاف القالب المهيمن
        top_format = df_p.groupby('شكل التقديم')['العدد'].sum().idxmax()
        st.markdown(f"<div class='ai-insight'>💡 <b>ملاحظة ذكية:</b> المحتوى المهيمن هو '<b>{top_format}</b>'. هذا يشير إلى اعتماد التغطية على هذا القالب بنسبة كبيرة.</div>", unsafe_allow_html=True)

    if not df_r.empty:
        total_reps = len(df_r['المراسل/الصحفي'].unique())
        c2.metric("شبكة المراسلين", f"{total_reps}", "تغطية ميدانية نشطة")
        
    if not df_g.empty:
        total_guests = len(df_g)
        c3.metric("إجمالي الضيوف", f"{total_guests}", "تنوع في الآراء")

    # --- القسم الثاني: الرادار التفاعلي ومقارنة الفئات ---
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 🕸️ رادار توازن المحتوى")
        if not df_p.empty:
            radar_data = df_p.groupby('شكل التقديم')['العدد'].sum().reset_index()
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=radar_data['العدد'], theta=radar_data['شكل التقديم'], fill='toself',
                line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.3)'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, gridcolor="#334155")), 
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.markdown("### 📊 توزيع القوالب عبر الزمن")
        if not df_p.empty:
            fig_area = px.area(df_p.groupby(['Date_Ref', 'شكل التقديم'])['العدد'].sum().reset_index(), 
                               x='Date_Ref', y='العدد', color='شكل التقديم', line_group='شكل التقديم')
            fig_area.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_area, use_container_width=True)

    # --- القسم الثالث: خريطة الحرارة (Heatmap) لأداء المراسلين ---
    st.markdown("---")
    st.markdown("### 🔥 خريطة كثافة نشاط المراسلين")
    if not df_r.empty:
        pivot_r = df_r.pivot_table(index='المراسل/الصحفي', columns='Date_Ref', values='عدد المداخلات', aggfunc='sum').fillna(0)
        fig_heat = px.imshow(pivot_r, labels=dict(x="التقرير", y="المراسل", color="المداخلات"),
                             color_continuous_scale='Blues', aspect="auto")
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- القسم الرابع: الجدول الذكي التفاعلي ---
    st.markdown("---")
    st.markdown("### 🕵️‍♂️ مستكشف الضيوف العميق")
    if not df_g.empty:
        st.dataframe(df_g, use_container_width=True)

else:
    st.info("💎 مرحباً بك في النسخة الاحترافية. يرجى رفع التقارير من القائمة الجانبية لتنشيط محرك الذكاء التحليلي.")
