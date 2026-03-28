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
                    elif 'الساعة' in cols and 'العدد' in cols:
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
        d_r = df_r[df_r['التقرير'] == selected_report] if not df_r.empty else pd.DataFrame()
        d_g = df_g[df_g['التقرير'] == selected_report] if not df_g.empty else pd.DataFrame()
        d_o = df_o[df_o['التقرير'] == selected_report] if not df_o.empty else pd.DataFrame()
        d_h = df_h[df_h['التقرير'] == selected_report] if not df_h.empty else pd.DataFrame()

        st.markdown("---")
        # 1. بطاقات المؤشرات (Dashboard Cards)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المواد", f"{int(d_p['العدد'].sum()) if not d_p.empty else 0}")
        c2.metric("عدد المراسلين", f"{len(d_r['المراسل/الصحفي'].unique()) if not d_r.empty else 0}")
        c3.metric("إجمالي الضيوف", f"{len(d_g) if not d_g.empty else 0}")
        c4.metric("تصريحات المسؤولين", f"{len(d_o) if not d_o.empty else 0}")

        st.markdown("---")
        col_a, col_b = st.columns(2)
        # 2. رسم دائري: شكل التقديم
        with col_a:
            st.markdown("#### 🍩 توزيع المواد (شكل التقديم)")
            if not d_p.empty:
                fig_p = px.pie(d_p, values='العدد', names='شكل التقديم', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_p, use_container_width=True)
        # 3. رسم دائري: سياسة واقتصاد
        with col_b:
            st.markdown("#### 🌍 التصنيف الموضوعي (سياسة/اقتصاد)")
            if not d_c.empty:
                fig_c = px.pie(d_c, values='العدد', names='التصنيف', hole=0.4, color_discrete_map={'سياسة': '#ef553b', 'اقتصاد': '#00cc96'})
                st.plotly_chart(fig_c, use_container_width=True)

        # 4 & 5. رسوم الساعات (إذا توفرت)
        if not d_h.empty:
            st.markdown("---")
            st.markdown("#### ⏰ توزيع كثافة المواد على ساعات البث")
            if 'التصنيف' in d_h.columns:
                fig_h = px.bar(d_h, x='الساعة', y='العدد', color='التصنيف', barmode='group')
            else:
                fig_h = px.bar(d_h, x='الساعة', y='العدد')
            st.plotly_chart(fig_h, use_container_width=True)

        st.markdown("---")
        col_c, col_d = st.columns(2)
        # 6. رسم أفقي: المراسلين
        with col_c:
            st.markdown("#### 🎙️ نشاط المراسلين (ترتيب تنازلي)")
            if not d_r.empty:
                top_r = d_r.groupby('المراسل/الصحفي')['عدد المداخلات'].sum().reset_index().sort_values('عدد المداخلات', ascending=True)
                fig_r = px.bar(top_r, x='عدد المداخلات', y='المراسل/الصحفي', orientation='h', text='عدد المداخلات', color_discrete_sequence=['#1976d2'])
                fig_r.update_layout(xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_r, use_container_width=True)
        
        # 7. رسم أفقي: الضيوف
        with col_d:
            st.markdown("#### 👤 أبرز الضيوف تكراراً")
            if not d_g.empty:
                top_g = d_g.groupby('الضيف').size().reset_index(name='الظهور').sort_values('الظهور', ascending=True).tail(10)
                fig_g = px.bar(top_g, x='الظهور', y='الضيف', orientation='h', text='الظهور', color_discrete_sequence=['#00cc96'])
                fig_g.update_layout(xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_g, use_container_width=True)

    # ----------------------------------------------------------------------
    # التبويب الثاني: مقارنة الأمس واليوم
    # ----------------------------------------------------------------------
    with tab2:
        if len(report_names) < 2:
            st.info("⚠️ لا تتوفر بيانات كافية للمقارنة. يرجى رفع ملفين على الأقل (مثلاً: تقرير اليوم وتقرير الأمس).")
        else:
            st.markdown("### ⚖️ لوحة المقارنة والتغيرات")
            cc1, cc2 = st.columns(2)
            today_rep = cc1.selectbox("اختر تقرير (اليوم):", report_names, index=0)
            yest_rep = cc2.selectbox("اختر تقرير (الأمس):", report_names, index=1 if len(report_names)>1 else 0)
            
            # حساب المجاميع لليوم والأمس
            t_p = df_p[df_p['التقرير'] == today_rep]['العدد'].sum() if not df_p.empty else 0
            y_p = df_p[df_p['التقرير'] == yest_rep]['العدد'].sum() if not df_p.empty else 0
            
            t_r = len(df_r[df_r['التقرير'] == today_rep]['المراسل/الصحفي'].unique()) if not df_r.empty else 0
            y_r = len(df_r[df_r['التقرير'] == yest_rep]['المراسل/الصحفي'].unique()) if not df_r.empty else 0
            
            t_g = len(df_g[df_g['التقرير'] == today_rep]) if not df_g.empty else 0
            y_g = len(df_g[df_g['التقرير'] == yest_rep]) if not df_g.empty else 0

            # 1. جدول المقارنة الرقمي
            st.markdown("#### 📈 التغير في المؤشرات الرئيسية")
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي المواد الإخبارية", int(t_p), f"{int(t_p - y_p)} مادة عن الأمس")
            m2.metric("عدد المراسلين المشاركين", int(t_r), f"{int(t_r - y_r)} مراسل عن الأمس")
            m3.metric("عدد الضيوف المستضافين", int(t_g), f"{int(t_g - y_g)} ضيف عن الأمس")

            st.markdown("---")
            # 2. رسم عمودي مقارن
            st.markdown("#### 📊 مقارنة قوالب التقديم (أمس مقابل اليوم)")
            if not df_p.empty:
                comp_p = df_p[df_p['التقرير'].isin([today_rep, yest_rep])]
                fig_comp_p = px.bar(comp_p, x='شكل التقديم', y='العدد', color='التقرير', barmode='group', text='العدد', color_discrete_sequence=['#1976d2', '#90caf9'])
                st.plotly_chart(fig_comp_p, use_container_width=True)

            # 3. مقارنة سياسة واقتصاد
            st.markdown("---")
            st.markdown("#### 🌍 التغير في التغطية الموضوعية")
            if not df_c.empty:
                comp_c = df_c[df_c['التقرير'].isin([today_rep, yest_rep])]
                fig_comp_c = px.pie(comp_c, values='العدد', names='التصنيف', facet_col='التقرير', color='التصنيف', color_discrete_map={'سياسة': '#ef553b', 'اقتصاد': '#00cc96'})
                st.plotly_chart(fig_comp_c, use_container_width=True)

            # 4. مقارنة نشاط المراسلين
            st.markdown("---")
            st.markdown("#### 🎙️ رادار نشاط المراسلين (زيادة ونقصان المداخلات)")
            if not df_r.empty:
                df_r_today = df_r[df_r['التقرير'] == today_rep].groupby('المراسل/الصحفي')['عدد المداخلات'].sum().reset_index()
                df_r_yest = df_r[df_r['التقرير'] == yest_rep].groupby('المراسل/الصحفي')['عدد المداخلات'].sum().reset_index()
                
                merged_r = pd.merge(df_r_today, df_r_yest, on='المراسل/الصحفي', how='outer', suffixes=(' (اليوم)', ' (الأمس)')).fillna(0)
                merged_r['الفرق'] = merged_r['عدد المداخلات (اليوم)'] - merged_r['عدد المداخلات (الأمس)']
                merged_r = merged_r.sort_values('الفرق', ascending=False)
                
                st.dataframe(merged_r.style.background_gradient(subset=['الفرق'], cmap='coolwarm'), use_container_width=True)

    # ----------------------------------------------------------------------
    # التبويب الثالث: قاعدة البيانات
    # ----------------------------------------------------------------------
    with tab3:
        st.markdown("### 🗄️ استكشاف وتصدير البيانات")
        report_filter = st.selectbox("تصفية البيانات حسب التقرير:", ["الكل"] + report_names)
        
        if not df_g.empty:
            st.markdown("#### 🎙️ سجل الضيوف والخبراء")
            display_df = df_g if report_filter == "الكل" else df_g[df_g['التقرير'] == report_filter]
            st.dataframe(display_df, use_container_width=True)
            
        if not df_o.empty:
            st.markdown("#### 👔 سجل تصريحات المسؤولين")
            display_df_o = df_o if report_filter == "الكل" else df_o[df_o['التقرير'] == report_filter]
            st.dataframe(display_df_o, use_container_width=True)
