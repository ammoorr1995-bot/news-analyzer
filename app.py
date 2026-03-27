import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

# إعدادات الصفحة لتظهر بشكل عريض واحترافي
st.set_page_config(page_title="News Analytics Pro | الشرق", layout="wide")

def parse_docx(file):
    """دالة لاستخراج الجداول والبيانات من ملف التقرير"""
    doc = Document(file)
    data_frames = {}
    
    for table in doc.tables:
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if len(rows) > 1:
            # تنظيف البيانات وحذف الصفوف المكررة إن وجدت
            df = pd.DataFrame(rows[1:], columns=rows[0])
            # التعرف على الجداول بناءً على أسماء الأعمدة في تقريرك
            if 'شكل التقديم' in df.columns: 
                data_frames['presentation'] = df
            elif 'التصنيف' in df.columns: 
                data_frames['category'] = df
            elif 'المؤشر' in df.columns:
                data_frames['kpis'] = df
    return data_frames

# واجهة الموقع
st.title("📊 نظام تحليل رصد البث الإخباري - قناة الشرق")
st.markdown("---")

# رفع الملف
uploaded_file = st.file_uploader("ارفق تقرير الرصد الشامل (docx)", type="docx")

if uploaded_file:
    with st.spinner('جاري معالجة التقرير...'):
        results = parse_docx(uploaded_file)
        
        # 1. عرض المؤشرات الرئيسية (KPIs) في الأعلى
        if 'kpis' in results:
            st.subheader("📌 المؤشرات الرئيسية")
            kpi_df = results['kpis']
            cols = st.columns(len(kpi_df))
            for idx, row in kpi_df.iterrows():
                cols[idx].metric(row['المؤشر'], row['القيمة'])
            st.markdown("---")

        # 2. عرض الرسوم البيانية في أعمدة
        col1, col2 = st.columns(2)

        if 'presentation' in results:
            with col1:
                st.subheader("🎯 توزيع أشكال التقديم")
                df_p = results['presentation']
                df_p['العدد'] = pd.to_numeric(df_p['العدد'], errors='coerce')
                fig_pie = px.pie(df_p, values='العدد', names='شكل التقديم', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig_pie, use_container_width=True)

        if 'category' in results:
            with col2:
                st.subheader("🌍 التصنيف الموضوعي")
                df_c = results['category']
                # تنظيف الأرقام من رموز مثل (≈) و (%)
                df_c['العدد'] = pd.to_numeric(df_c['العدد'].astype(str).str.replace('≈ ', '').str.replace('%', ''), errors='coerce')
                fig_bar = px.bar(df_c, x='التصنيف', y='العدد', color='التصنيف', 
                                 text_auto=True, title="عدد المواد حسب التخصص")
                st.plotly_chart(fig_bar, use_container_width=True)

st.sidebar.markdown("""
### حول النظام
هذا المشغل مخصص لتحليل تقارير **متابعة البث**. 
يعتمد على استخراج البيانات من الجداول المضمنة في ملفات Word وتحويلها إلى رؤى بصرية.
""")