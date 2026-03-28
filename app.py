import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات المنصة
st.set_page_config(page_title="Asharq Intelligence Hub", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background-color: #0b1120; color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-left: 1px solid #1e293b; }
    .ai-insight { background: rgba(59, 130, 246, 0.1); border-right: 5px solid #3b82f6; padding: 20px; border-radius: 10px; color: #93c5fd; font-size: 1.1rem; }
    h1, h2, h3 { color: #f8fafc; font-weight: 800; text-align: right; }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 12px; border-bottom: 4px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# دالة ذكية لتنظيف الأرقام (تتعامل مع أي نص بداخله رقم)
def clean_num(text):
    if pd.isna(text): return 0
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 0

# 2. محرك القراءة العبقري (Advanced Data Extractor)
@st.cache_data
def parse_reports(uploaded_files):
    pool = {'p': [], 'r': [], 'g': [], 'c': []}
    for file in uploaded_files:
        try:
            doc = Document(file)
            tag = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Source_Date'] = tag
                    cols = df.columns.tolist()
                    
                    # البحث المرن عن الأعمدة
                    col_num = next((c for c in cols if "العدد" in c or "عدد" in c), None)
                    
                    if any("شكل التقديم" in c for c in cols) and col_num:
                        df['العدد'] = df[col_num].apply(clean_num)
                        pool['p'].append(df)
                    elif any("المراسل" in c for c in cols) and col_num:
                        df['عدد المداخلات'] = df[col_num].apply(clean_num)
                        pool['r'].append(df)
                    elif any("الضيف" in c for c in cols):
                        pool['g'].append(df)
        except: continue
    return pool

# 3. واجهة التحكم
st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🏢 ASHARQ <span style='color:#3b82f6'>INTEL HUB</span></h1>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📥 ارفع ملفات التقارير هنا:", type="docx", accept_multiple_files=True)

if files:
    raw = parse_reports(files)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()
    df_g = pd.concat(raw['g']) if raw['g'] else pd.DataFrame()

    menu = st.tabs(["📅 تحليل يومي", "⚖️ مقارنة ذكية", "📊 تقرير شهري شامل", "📥 تصدير PDF"])

    with menu[0]:
        st.markdown("### 🔍 فحص اليوم المختار")
        day = st.selectbox("اختر التاريخ:", df_p['Source_Date'].unique() if not df_p.empty else [])
        if not df_p.empty:
            day_data = df_p[df_p['Source_Date'] == day]
            c1, c2 = st.columns([2, 1])
            with c1:
                st.plotly_chart(px.pie(day_data, values='العدد', names='شكل التقديم', hole=0.5, template="plotly_dark"), use_container_width=True)
            with c2:
                total = day_data['العدد'].sum()
                st.markdown(f"<div class='ai-insight'><b>الخلاصة الإحصائية لـ {day}:</b><br>إجمالي المواد: {int(total)} مادة.<br>تم تحليل البيانات بنجاح وبناء المخطط البياني.</div>", unsafe_allow_html=True)

    with menu[1]:
        st.markdown("### ⚖️ مقارنة بين فترتين")
        if len(files) > 1:
            d1 = st.selectbox("اليوم الأول:", df_p['Source_Date'].unique(), index=0)
            d2 = st.selectbox("اليوم الثاني:", df_p['Source_Date'].unique(), index=1)
            comp = df_p[df_p['Source_Date'].isin([d1, d2])]
            st.plotly_chart(px.bar(comp, x='شكل التقديم', y='العدد', color='Source_Date', barmode='group', template="plotly_dark"), use_container_width=True)
        else:
            st.warning("يرجى رفع ملفين على الأقل للمقارنة.")

    with menu[2]:
        st.markdown("### 📈 التوجهات العامة والنمو الشهري")
        if not df_p.empty:
            monthly = df_p.groupby('Source_Date')['العدد'].sum().reset_index()
            st.plotly_chart(px.line(monthly, x='Source_Date', y='العدد', markers=True, title="خط الإنتاج الزمني"), use_container_width=True)
            
            st.markdown("### 🎙️ أداء المراسلين والضيوف (تراكمي)")
            col_a, col_b = st.columns(2)
            with col_a:
                if not df_r.empty:
                    top_r = df_r.groupby('المراسل/الصحفي')['عدد المداخلات'].sum().reset_index().sort_values('عدد المداخلات', ascending=False).head(10)
                    st.plotly_chart(px.bar(top_r, x='عدد المداخلات', y='المراسل/الصحفي', orientation='h', title="أكثر 10 مراسلين نشاطاً"), use_container_width=True)
            with col_b:
                if not df_g.empty:
                    top_g = df_g.groupby('الضيف').size().reset_index(name='الظهور').sort_values('الظهور', ascending=False).head(10)
                    st.plotly_chart(px.bar(top_g, x='الظهور', y='الضيف', orientation='h', title="أكثر الضيوف استضافة", color_discrete_sequence=['#10b981']), use_container_width=True)

    with menu[3]:
        st.markdown("### 📥 تصدير التقرير النهائي")
        st.markdown("<div class='ai-insight'>للحصول على تقرير PDF احترافي وجاهز للطباعة: قم بالضغط على (Ctrl + P) أو اختيار Print من المتصفح، ثم اختر حفظ بتنسيق PDF. الواجهة مهيأة للطباعة بشكل أنيق.</div>", unsafe_allow_html=True)
        if not df_p.empty:
            csv = df_p.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل البيانات كاملة (Excel/CSV)", data=csv, file_name="Asharq_Data.csv", mime="text/csv")

else:
    st.info("👈 بانتظار رفع ملفات الوورد (docx) لتشغيل محرك التحليل الذكي.")
