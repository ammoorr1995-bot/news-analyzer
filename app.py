import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

# إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Asharq Insights Pro", layout="wide", page_icon="📈")

# ستايل مخصص لمحاكاة Meta Business Suite
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e4e6eb; }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

def parse_docx(file):
    doc = Document(file)
    data = {'presentation': None, 'category': None, 'reporters': None}
    
    for table in doc.tables:
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
            
            # حل مشكلة KeyError: التأكد من وجود الأعمدة قبل المعالجة
            cols = df.columns.tolist()
            
            if 'شكل التقديم' in cols and 'العدد' in cols:
                df['العدد'] = pd.to_numeric(df['العدد'], errors='coerce').fillna(0)
                data['presentation'] = df[['شكل التقديم', 'العدد']]
            
            elif 'التصنيف' in cols and 'العدد' in cols:
                df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace('≈ ', '').str.replace('%', ''), errors='coerce').fillna(0)
                data['category'] = df[['التصنيف', 'العدد']]
                
            elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                data['reporters'] = df[['المراسل/الصحفي', 'عدد المداخلات']]
    return data

st.title("🔵 Asharq Business Insights")
st.markdown("### تحليلات أداء البث والجمهور")

uploaded_files = st.file_uploader("ارفق تقارير الرصد (docx)", type="docx", accept_multiple_files=True)

if uploaded_files:
    all_p, all_c, all_r = [], [], []
    
    for f in uploaded_files:
        try:
            res = parse_docx(f)
            if res['presentation'] is not None: all_p.append(res['presentation'])
            if res['category'] is not None: all_c.append(res['category'])
            if res['reporters'] is not None: all_r.append(res['reporters'])
        except Exception:
            continue

    # عرض بطاقات الأداء (Meta Metrics)
    st.markdown("---")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    if all_p:
        combined_p = pd.concat(all_p).groupby('شكل التقديم').sum().reset_index()
        total_content = int(combined_p['العدد'].sum())
        kpi1.metric("إجمالي المواد الإخبارية", f"{total_content:,}")
        
        # الرسم البياني (Donut Chart)
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown("#### 📊 توزيع القوالب")
            fig_pie = px.pie(combined_p, values='العدد', names='شكل التقديم', hole=0.6, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

    if all_c:
        combined_c = pd.concat(all_c).groupby('التصنيف').sum().reset_index()
        kpi2.metric("التغطية الموضوعية", f"{len(combined_c)} فئات")
        with col_right:
            st.markdown("#### 🌍 تحليل المواضيع")
            fig_bar = px.bar(combined_c, x='التصنيف', y='العدد', text_auto=True,
                             color_discrete_sequence=['#1877f2'])
            st.plotly_chart(fig_bar, use_container_width=True)

    if all_r:
        combined_r = pd.concat(all_r).groupby('المراسل/الصحفي').sum().reset_index()
        kpi3.metric("شبكة المراسلين النشطة", f"{len(combined_r)}")
        st.markdown("#### 🎙️ أعلى المراسلين نشاطاً (Top Contributors)")
        top_reporters = combined_r.sort_values(by='عدد المداخلات', ascending=False).head(10)
        fig_rep = px.treemap(top_reporters, path=['المراسل/الصحفي'], values='عدد المداخلات',
                             color='عدد المداخلات', color_continuous_scale='Blues')
        st.plotly_chart(fig_rep, use_container_width=True)

    st.success(f"تم تحليل ودمج {len(uploaded_files)} تقارير بنجاح.")
