import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="Asharq News Master Analytics", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    .main-header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem; }
    .stMetric { background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. دالة المعالجة الذكية (مع معالجة الأخطاء)
@st.cache_data
def load_all_data(uploaded_files):
    storage = {'p': [], 'r': [], 'g': [], 'c': [], 'h': []}
    for file in uploaded_files:
        try:
            doc = Document(file)
            fname = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['الملف'] = fname # ربط كل معلومة باسم ملفها (تاريخها)
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
                    elif 'الساعة' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'], errors='coerce').fillna(0)
                        storage['h'].append(df)
        except: continue
    return storage

# 3. الواجهة
st.markdown('<div class="main-header"><h1>مركز التحليل الإحصائي الزمني</h1><p>مراقبة وتحليل أداء المحتوى عبر جميع التقارير المرفوعة</p></div>', unsafe_allow_html=True)

files = st.sidebar.file_uploader("📥 ارفع كل ملفات التقارير هنا:", type="docx", accept_multiple_files=True)

if files:
    raw = load_all_data(files)
    
    # تحويل القوائم إلى جداول مجمعة مع تفادي أخطاء الفراغ
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()
    df_g = pd.concat(raw['g']) if raw['g'] else pd.DataFrame()
    df_c = pd.concat(raw['c']) if raw['c'] else pd.DataFrame()
    df_h = pd.concat(raw['h']) if raw['h'] else pd.DataFrame()

    tab1, tab2, tab3 = st.tabs(["📈 التحليل الزمني (شامل)", "🎙️ أداء الشبكة", "🔍 مستكشف الملفات"])

    # --- التبويب الأول: التحليل الزمني الشامل لكل الملفات ---
    with tab1:
        st.markdown("### 📊 تطور حجم الإنتاج عبر التقارير المرفوعة")
        if not df_p.empty:
            # تجميع إجمالي المواد لكل ملف (يوم)
            trend_data = df_p.groupby('الملف')['العدد'].sum().reset_index()
            fig_trend = px.line(trend_data, x='الملف', y='العدد', markers=True, title="إجمالي المواد الإخبارية لكل يوم", line_shape="spline")
            st.plotly_chart(fig_trend, use_container_width=True)

            st.markdown("### 🧬 مقارنة قوالب العرض (مكدسة)")
            # عرض كيف يتغير توزيع (مذيع، ضيف، مراسل) عبر الأيام
            fig_stack = px.bar(df_p, x='الملف', y='العدد', color='شكل التقديم', title="تغير نسب القوالب عبر الأيام")
            st.plotly_chart(fig_stack, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🌍 توجه التغطية (سياسة vs اقتصاد)")
        if not df_c.empty:
            fig_topic = px.area(df_c.groupby(['الملف', 'التصنيف'])['العدد'].sum().reset_index(), 
                                x='الملف', y='العدد', color='التصنيف', title="تطور الاهتمام الموضوعي")
            st.plotly_chart(fig_topic, use_container_width=True)

    # --- التبويب الثاني: أداء الشبكة (مراسلين وضيووف) ---
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🎙️ أكثر المراسلين ظهوراً (إجمالي)")
            if not df_r.empty:
                top_r = df_r.groupby('المراسل/الصحفي')['عدد المداخلات'].sum().sort_values(ascending=False).head(15).reset_index()
                st.plotly_chart(px.bar(top_r, x='عدد المداخلات', y='المراسل/الصحفي', orientation='h', color='عدد المداخلات'), use_container_width=True)
        with col2:
            st.markdown("### 👤 أكثر الضيوف استضافة")
            if not df_g.empty:
                top_g = df_g.groupby('الضيف').size().sort_values(ascending=False).head(15).reset_index(name='الظهور')
                st.plotly_chart(px.bar(top_g, x='الظهور', y='الضيف', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

    # --- التبويب الثالث: مستكشف ملف محدد ---
    with tab3:
        st.markdown("### 🔎 تفاصيل ملف محدد")
        fnames = [f.name.replace('.docx', '') for f in files]
        selected = st.selectbox("اختر ملفاً لاستعراض بياناته الخام:", fnames)
        
        st.write(f"بيانات الضيوف في {selected}:")
        if not df_g.empty:
            st.dataframe(df_g[df_g['الملف'] == selected], use_container_width=True)
else:
    st.info("👈 يرجى رفع مجموعة من ملفات التقارير (docx) من القائمة الجانبية لبدء التحليل الزمني.")
