import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

# 1. إعدادات الصفحة
st.set_page_config(page_title="Asharq News Analytics", layout="wide", page_icon="🌐")

# 2. تصميم CSS احترافي (مظهر Enterprise)
st.markdown("""
    <style>
    /* خلفية الموقع */
    .stApp { background-color: #f4f7f6; }
    
    /* القائمة الجانبية */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    
    /* البانر الترحيبي في الصفحة الرئيسية */
    .hero-banner {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        color: white;
        padding: 40px 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    .hero-banner h1 { color: #ffffff !important; font-size: 3em; margin-bottom: 10px; font-weight: 700; }
    .hero-banner p { font-size: 1.2em; opacity: 0.9; }
    
    /* بطاقات الأرقام (Metrics) */
    .stMetric { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-right: 5px solid #1976d2; 
        text-align: center;
    }
    
    /* العناوين */
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 3. دالة استخراج البيانات 
@st.cache_data
def process_files(uploaded_files):
    all_data = {'presentation': [], 'category': [], 'reporters': [], 'guests': [], 'officials': []}
    
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
                    
                    elif 'التصنيف' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['category'].append(df[['التقرير', 'التصنيف', 'العدد']])
                        
                    elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                        df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                        all_data['reporters'].append(df[['التقرير', 'المراسل/الصحفي', 'عدد المداخلات']])
                    
                    elif 'الضيف' in cols and 'الصفة' in cols:
                        all_data['guests'].append(df)
                        
                    elif 'المسؤول' in cols and 'الصفة' in cols:
                        all_data['officials'].append(df)
        except Exception:
            continue
    return all_data

# 4. القائمة الجانبية (Navigation &
