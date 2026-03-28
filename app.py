import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

st.set_page_config(page_title="News Analytics Pro | الشرق", layout="wide")

def parse_docx(file):
    doc = Document(file)
    data_frames = {'presentation': None, 'category': None}
    
    for table in doc.tables:
        # قراءة الصفوف وتنظيف المسافات من أسماء الأعمدة
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            # تنظيف أسماء الأعمدة من أي مسافات مخفية
            df.columns = [col.strip() for col in df.columns]
            
            # التأكد من وجود عمود 'العدد' قبل المعالجة
            if 'العدد' in df.columns:
                if 'شكل التقديم' in df.columns:
                    df['العدد'] = pd.to_numeric(df['العدد'], errors='coerce')
                    data_frames['presentation'] = df[['شكل التقديم', 'العدد']]
                elif 'التصنيف' in df.columns:
                    # تنظيف الرموز مثل ≈ و % لتحويلها لرقم
                    df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace('≈ ', '').str.replace('%', ''), errors='coerce')
                    data_frames['category'] = df[['التصنيف', 'العدد']]
    return data_frames

st.title("📊 نظام تحليل ودمج تقارير البث - قناة الشرق")
st.markdown("---")

uploaded_files = st.file_uploader("ارفق تقارير الرصد (docx)", type="docx", accept_multiple_files=True)

if uploaded_files:
    all_presentation = []
    all_category = []
    
    for uploaded_file in uploaded_files:
        try:
            res = parse_docx(uploaded_file)
            if res['presentation'] is not None: all_presentation.append(res['presentation'])
            if res['category'] is not None: all_category.append(res['category'])
        except Exception as e:
            st.warning(f"تعذر تحليل الملف {uploaded_file.name}: تأكد من مطابقة أسماء الجداول.")

    if all_presentation or all_category:
        col1, col2 = st.columns(2)
        with col1:
            if all_presentation:
                st.subheader("🎯 إجمالي أشكال التقديم (مجمع)")
                combined_p = pd.concat(all_presentation).groupby('شكل التقديم').sum().reset_index()
                st.plotly_chart(px.pie(combined_p, values='العدد', names='شكل التقديم', hole=0.4), use_container_width=True)
        with col2:
            if all_category:
                st.subheader("🌍 إجمالي التصنيف الموضوعي (مجمع)")
                combined_c = pd.concat(all_category).groupby('التصنيف').sum().reset_index()
                st.plotly_chart(px.bar(combined_c, x='التصنيف', y='العدد', color='التصنيف', text_auto=True), use_container_width=True)
        st.success(f"تم دمج بيانات {len(uploaded_files)} ملفات.")
