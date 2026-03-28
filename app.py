import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="Asharq News Insights", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .hero-section { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 2.5rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; border-top: 5px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; }
    h3 { color: #1e3a8a; font-weight: 700; border-right: 5px solid #3b82f6; padding-right: 10px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. دالة المعالجة الذكية
@st.cache_data
def load_and_process(uploaded_files):
    all_data = {'presentation': [], 'category': [], 'reporters': [], 'guests': [], 'officials': [], 'hourly': []}
    for file in uploaded_files:
        try:
            doc = Document(file)
            name = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['التقرير'] = name
                    cols = df.columns.tolist()
                    if 'شكل التقديم' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['presentation'].append(df[['التقرير', 'شكل التقديم', 'العدد']])
                    elif 'التصنيف' in cols and 'العدد' in cols and 'شكل التقديم' not in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['category'].append(df[['التقرير', 'التصنيف', 'العدد']])
                    elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                        df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                        all_data['reporters'].append(df[['التقرير', 'المراسل/الصحفي', 'عدد المداخلات']])
                    elif 'الضيف' in cols and 'الصفة' in cols: all_data['guests'].append(df)
                    elif 'المسؤول' in cols and 'الصفة' in cols: all_data['officials'].append(df)
                    elif 'الساعة' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'], errors='coerce').fillna(0)
                        all_data['hourly'].append(df)
        except: continue
    return all_data

# 3. واجهة الاستخدام
st.markdown('<div class="hero-section"><h1>منصة التحليل البصري والمقارنات</h1><p>تحويل تقارير الرصد اليومي إلى رؤى تفاعلية ذكية</p></div>', unsafe_allow_html=True)

files = st.sidebar.file_uploader("📥 ارفع تقارير اليوم والأمس (docx):", type="docx", accept_multiple_files=True)

if files:
    data = load_and_process(files)
    names = [f.name.replace('.docx', '') for f in files]
    
    t1, t2 = st.tabs(["📑 تقرير اليوم التفصيلي", "⚖️ المقارنة مع اليوم السابق"])

    # --- الجزء الأول: تحليل اليوم الحالي ---
    with t1:
        current = st.selectbox("اختر التقرير المراد تحليله:", names)
        d_p = pd.concat(data['presentation']).query(f"التقرير == '{current}'") if data['presentation'] else pd.DataFrame()
        d_c = pd.concat(data['category']).query(f"التقرير == '{current}'") if data['category'] else pd.DataFrame()
        d_r = pd.concat(data['reporters']).query(f"التقرير == '{current}'") if data['reporters'] else pd.DataFrame()
        d_g = pd.concat(data['guests']).query(f"التقرير == '{current}'") if data['guests'] else pd.DataFrame()
        d_h = pd.concat(data['hourly']).query(f"التقرير == '{current}'") if data['hourly'] else pd.DataFrame()

        # بطاقات المؤشرات
        st.markdown("### 🏷️ ملخص المؤشرات الرئيسية")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المواد", f"{int(d_p['العدد'].sum()) if not d_p.empty else 0}")
        c2.metric("المراسلين", f"{len(d_r['المراسل/الصحفي'].unique()) if not d_r.empty else 0}")
        c3.metric("الضيوف", f"{len(d_g) if not d_g.empty else 0}")
        c4.metric("التغطية", "24/7")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🍩 توزيع قوالب العرض")
            if not d_p.empty:
                st.plotly_chart(px.pie(d_p, values='العدد', names='شكل التقديم', hole=0.5), use_container_width=True)
        with col2:
            st.markdown("### 🌍 السياسة مقابل الاقتصاد")
            if not d_c.empty:
                st.plotly_chart(px.pie(d_c, values='العدد', names='التصنيف', hole=0.5, color_discrete_map={'سياسة':'#1e3a8a','اقتصاد':'#10b981'}), use_container_width=True)

        if not d_h.empty:
            st.markdown("### 📊 كثافة المواد حسب ساعات البث")
            fig_h = px.bar(d_h, x='الساعة', y='العدد', color='التصنيف' if 'التصنيف' in d_h.columns else None, barmode='group')
            st.plotly_chart(fig_h, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### 🎙️ ترتيب المراسلين بنشاطهم")
            if not d_r.empty:
                st.plotly_chart(px.bar(d_r.sort_values('عدد المداخلات'), x='عدد المداخلات', y='المراسل/الصحفي', orientation='h'), use_container_width=True)
        with col4:
            st.markdown("### 👤 أبرز الضيوف ظهوراً")
            if not d_g.empty:
                top_g = d_g['الضيف'].value_counts().reset_index().head(10)
                st.plotly_chart(px.bar(top_g, x='count', y='الضيف', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

    # --- الجزء الثاني: المقارنة الذكية ---
    with t2:
        if len(names) < 2:
            st.warning("⚠️ يرجى رفع ملفين على الأقل لتفعيل خاصية المقارنة.")
        else:
            c_today, c_yest = st.columns(2)
            today = c_today.selectbox("تقرير (اليوم):", names, index=0)
            yest = c_yest.selectbox("تقرير (الأمس):", names, index=1)

            # حساب فروقات الأرقام
            t_total = pd.concat(data['presentation']).query(f"التقرير == '{today}'")['العدد'].sum()
            y_total = pd.concat(data['presentation']).query(f"التقرير == '{yest}'")['العدد'].sum()
            diff = t_total - y_total
            perc = (diff / y_total * 100) if y_total != 0 else 0

            st.markdown("### ⚖️ جدول المقارنة الرقمي")
            m1, m2 = st.columns(2)
            m1.metric("إجمالي المواد", f"{int(t_total)}", f"{perc:.1f}% {'▲' if diff > 0 else '▼'}")
            
            # رسم مقارنة الأعمدة (أمس vs اليوم)
            st.markdown("### 📊 مقارنة قوالب التقديم (أمس vs اليوم)")
            comp_p = pd.concat(data['presentation']).query(f"التقرير in ['{today}', '{yest}']")
            st.plotly_chart(px.bar(comp_p, x='شكل التقديم', y='العدد', color='التقرير', barmode='group'), use_container_width=True)

            # مقارنة الساعات (رسم خطي)
            st.markdown("### 📉 التغير في كثافة الساعات (خط زمني)")
            comp_h = pd.concat(data['hourly']).query(f"التقرير in ['{today}', '{yest}']")
            if not comp_h.empty:
                st.plotly_chart(px.line(comp_h, x='الساعة', y='العدد', color='التقرير', markers=True), use_container_width=True)

            st.markdown("### 🎙️ تحليل نشاط المراسلين (المقارن)")
            df_r_all = pd.concat(data['reporters'])
            r_today = df_r_all.query(f"التقرير == '{today}'").groupby('المراسل/الصحفي')['عدد المداخلات'].sum()
            r_yest = df_r_all.query(f"التقرير == '{yest}'").groupby('المراسل/الصحفي')['عدد المداخلات'].sum()
            r_comp = pd.concat([r_today, r_yest], axis=1, keys=['اليوم', 'الأمس']).fillna(0)
            r_comp['الفرق'] = r_comp['اليوم'] - r_comp['الأمس']
            st.table(r_comp.sort_values('الفرق', ascending=False))

else:
    st.info("👈 ابدأ برفع ملفات الرصد اليومي من القائمة الجانبية.")
