import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document

st.set_page_config(page_title="Asharq Insights Pro", layout="wide")

# تصميم ستايل يشبه Meta Business Suite
st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1c1e21; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

def parse_docx(file):
    doc = Document(file)
    data = {'kpis': {}, 'presentation': None, 'category': None, 'reporters': None, 'hourly': []}
    
    for table in doc.tables:
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
            
            if 'المؤشر' in df.columns:
                data['kpis'] = dict(zip(df['المؤشر'], df['القيمة']))
            elif 'شكل التقديم' in df.columns:
                df['العدد'] = pd.to_numeric(df['العدد'], errors='coerce')
                data['presentation'] = df
            elif 'التصنيف' in df.columns:
                df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace('≈ ', '').str.replace('%', ''), errors='coerce')
                data['category'] = df
            elif 'المراسل/الصحفي' in df.columns:
                df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce')
                data['reporters'] = df
    
    # استخراج الكثافة الساعة بساعة (افتراضي من نصوص التحليل)
    # يمكن تطوير هذه الجزئية لاحقاً لسحبها من جداول الساعات بدقة
    return data

st.title("🔵 Asharq Business Insights")
st.subheader("لوحة تحكم أداء البث الإخباري")

uploaded_files = st.file_uploader("ارفع تقارير الرصد", type="docx", accept_multiple_files=True)

if uploaded_files:
    all_data = [parse_docx(f) for f in uploaded_files]
    
    # 1. قسم الملخص (Top Stats)
    st.markdown("### 📈 ملخص الأداء العام")
    m1, m2, m3, m4 = st.columns(4)
    total_mats = sum([int(d['kpis'].get('إجمالي المواد المبثوثة', '0').split()[0]) for d in all_data if d['kpis']])
    total_reporters = sum([int(d['kpis'].get('عدد المراسلين', '0')) for d in all_data if d['kpis']])
    
    m1.metric("إجمالي المواد", f"{total_mats}")
    m2.metric("شبكة المراسلين", f"{total_reporters}")
    m3.metric("تغطية متواصلة", "24h")
    m4.metric("حالة البث", "مستقر")

    st.markdown("---")

    # 2. تحليل المحتوى (Content Breakdown)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### 🎯 توزيع قوالب العرض (Format)")
        all_p = pd.concat([d['presentation'] for d in all_data if d['presentation'] is not None])
        fig_p = px.bar(all_p.groupby('شكل التقديم').sum().reset_index(), 
                       x='العدد', y='شكل التقدim', orientation='h', 
                       color_discrete_sequence=['#1877f2'], text_auto=True)
        st.plotly_chart(fig_p, use_container_width=True)

    with c2:
        st.markdown("#### 🌍 التغطية الموضوعية (Topics)")
        all_c = pd.concat([d['category'] for d in all_data if d['category'] is not None])
        fig_c = px.pie(all_c.groupby('التصنيف').sum().reset_index(), 
                       values='العدد', names='التصنيف', hole=0.6,
                       color_discrete_sequence=['#1877f2', '#e4e6eb'])
        st.plotly_chart(fig_c, use_container_width=True)

    # 3. تحليل المراسلين (Top Performers)
    st.markdown("#### 🎙️ أداء شبكة المراسلين (Top Reporters)")
    all_r = pd.concat([d['reporters'] for d in all_data if d['reporters'] is not None])
    top_r = all_r.groupby('المراسل/الصحفي')['عدد المداخلات'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_r = px.treemap(top_r, path=['المراسل/الصحفي'], values='عدد المداخلات', color='عدد المداخلات',
                       color_continuous_scale='Blues')
    st.plotly_chart(fig_r, use_container_width=True)

    st.success(f"تم تحليل {len(uploaded_files)} تقارير بنجاح.")
