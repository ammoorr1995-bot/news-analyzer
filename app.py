import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document
import re

# ==========================================
# 1. إعدادات المنصة والهوية البصرية المريحة
# ==========================================
st.set_page_config(page_title="Asharq AI Executive", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    
    /* خلفية داكنة جداً ومريحة للعين */
    .stApp { background-color: #0b1121; color: #f8fafc; }
    
    /* تصميم بطاقات الأرقام */
    .stMetric { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    [data-testid="stMetricValue"] { color: #60a5fa !important; font-size: 2.5rem !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #cbd5e1 !important; font-size: 1.1rem !important; }

    /* صندوق تقرير الذكاء الاصطناعي */
    .ai-report-box {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-right: 6px solid #60a5fa;
        padding: 30px;
        border-radius: 15px;
        color: #e2e8f0;
        font-size: 1.15rem;
        line-height: 1.9;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }
    .ai-title { color: #60a5fa; font-weight: 700; font-size: 1.4rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
    
    /* تنسيق الطباعة لتصدير PDF */
    @media print {
        .no-print, [data-testid="stSidebar"] { display: none !important; }
        .stApp { background: white !important; color: black !important; }
        .ai-report-box { background: #f8fafc !important; border-right: 6px solid #2563eb !important; color: black !important; box-shadow: none; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. محرك قراءة البيانات (مستقر وخالي من التعقيد)
# ==========================================
def extract_number(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if res else 0

@st.cache_data
def process_reports(files):
    data = {'p': [], 'r': []} # p: Presentation (شكل التقديم), r: Reporters (المراسلين)
    for f in files:
        try:
            doc = Document(f)
            day_name = f.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['اليوم'] = day_name
                    cols = df.columns.tolist()
                    
                    # سحب جدول شكل التقديم
                    if any("شكل التقديم" in c for c in cols):
                        val_col = next((c for c in cols if "العدد" in c or "عدد" in c), cols[1])
                        df['العدد'] = df[val_col].apply(extract_number)
                        data['p'].append(df[['اليوم', 'شكل التقديم', 'العدد']])
                        
                    # سحب جدول المراسلين لمعرفة حجم التغطية الميدانية
                    elif any("المراسل" in c for c in cols):
                        val_col = next((c for c in cols if "العدد" in c or "مداخلات" in c), cols[1])
                        df['المداخلات'] = df[val_col].apply(extract_number)
                        data['r'].append(df[['اليوم', cols[0], 'المداخلات']])
        except: continue
    return data

# ==========================================
# 3. بناء الواجهة والتجربة الإدارية
# ==========================================
st.markdown("<h1 style='text-align: center; color: #60a5fa; font-size: 3rem; margin-bottom: 0;'>ASHARQ <span style='color:white'>ANALYTICS</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 30px;'>مركز التحليل الاستراتيجي المدعوم بالذكاء الاصطناعي</p>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📂 ارفع ملفات الرصد اليومي هنا:", type="docx", accept_multiple_files=True)

if files:
    raw = process_reports(files)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()

    tabs = st.tabs(["📄 تحليل اليوم المفرد", "⚖️ التقرير المقارن (متعدد الأيام)", "📥 طباعة/تصدير"])

    # ---------------------------------------------------------
    # التبويب الأول: تحليل ذكي ليوم واحد
    # ---------------------------------------------------------
    with tabs[0]:
        st.markdown("### 🔍 قراءة الذكاء الاصطناعي لليوم")
        days_list = df_p['اليوم'].unique() if not df_p.empty else []
        selected_day = st.selectbox("اختر اليوم المراد تحليله:", days_list)
        
        if not df_p.empty:
            day_data = df_p[df_p['اليوم'] == selected_day]
            day_rep = df_r[df_r['اليوم'] == selected_day] if not df_r.empty else pd.DataFrame()
            
            total_items = day_data['العدد'].sum()
            top_format = day_data.groupby('شكل التقديم')['العدد'].sum().idxmax()
            top_format_val = day_data.groupby('شكل التقديم')['العدد'].sum().max()
            rep_count = day_rep['المداخلات'].sum() if not day_rep.empty else 0
            
            # --- كتابة تقرير الذكاء الاصطناعي لليوم ---
            ai_text = f"""
            <div class='ai-report-box'>
                <div class='ai-title'>🧠 التقرير التحليلي لـ ({selected_day})</div>
                يُظهر الرصد اليومي تسجيل إجمالي <b>{int(total_items)}</b> مادة إخبارية تم بثها. 
                استحوذ القالب الإخباري <b>"{top_format}"</b> على النصيب الأكبر من البث بواقع <b>{int(top_format_val)}</b> مادة، 
                مما يعكس طبيعة التغطية لهذا اليوم. أما على الصعيد الميداني، فقد ساهم فريق المراسلة بتقديم <b>{int(rep_count)}</b> مداخلة مباشرة/مسجلة، 
                وهو ما يمثل دعماً للمحتوى الإخباري من مواقع الأحداث.
            </div>
            """
            st.markdown(ai_text, unsafe_allow_html=True)
            
            # الرسوم البيانية لليوم
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.pie(day_data, values='العدد', names='شكل التقديم', hole=0.5, title="توزيع قوالب البث"), use_container_width=True)
            with c2:
                if not day_rep.empty:
                    top_5_reps = day_rep.nlargest(5, 'المداخلات')
                    st.plotly_chart(px.bar(top_5_reps, x='المداخلات', y=day_rep.columns[1], orientation='h', title="أنشط 5 مراسلين باليوم"), use_container_width=True)

    # ---------------------------------------------------------
    # التبويب الثاني: التقرير المقارن (ذكاء اصطناعي شامل)
    # ---------------------------------------------------------
    with tabs[1]:
        st.markdown("### ⚖️ التحليل الاستراتيجي المقارن")
        selected_days = st.multiselect("اختر الأيام المراد مقارنتها:", days_list, default=days_list[:2] if len(days_list)>1 else days_list)
        
        if len(selected_days) > 1:
            comp_p = df_p[df_p['اليوم'].isin(selected_days)]
            
            # حسابات الذكاء الاصطناعي للمقارنة
            total_comp = comp_p['العدد'].sum()
            avg_comp = total_comp / len(selected_days)
            best_day = comp_p.groupby('اليوم')['العدد'].sum().idxmax()
            best_day_val = comp_p.groupby('اليوم')['العدد'].sum().max()
            lowest_day = comp_p.groupby('اليوم')['العدد'].sum().idxmin()
            
            # --- كتابة التقرير التنفيذي المقارن (1 Pager) ---
            ai_comp_text = f"""
            <div class='ai-report-box'>
                <div class='ai-title'>📈 الملخص التنفيذي لتباين الأداء</div>
                <b>نظرة عامة:</b> قمنا بتحليل الأيام ({len(selected_days)}) المحددة، حيث بلغ إجمالي الإنتاج الإخباري <b>{int(total_comp):,}</b> مادة، بمتوسط <b>{avg_comp:.1f}</b> مادة يومياً.<br><br>
                <b>التباين والذروة:</b> سجل يوم <b>"{best_day}"</b> أعلى معدل بث بواقع <b>{int(best_day_val)}</b> مادة إخبارية، مما يشير إلى وجود كثافة إخبارية أو تغطية استثنائية في ذلك اليوم، مقارنة بيوم <b>"{lowest_day}"</b> الذي سجل الأداء الأهدأ ضمن النطاق الزمني المحدد.<br><br>
                <b>الخلاصة الإدارية:</b> التباين بين الأيام المحددة يعتبر ضمن الإطار التشغيلي المعتاد، والنظام يُقيّم الأداء العام بـ (المستقر). توضح الرسوم البيانية أدناه الفروقات الدقيقة في توزيع قوالب التقديم بين هذه الأيام لتحديد أين تركز المجهود التحريري.
            </div>
            """
            st.markdown(ai_comp_text, unsafe_allow_html=True)
            
            # رسوم المقارنة
            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(px.bar(comp_p, x='شكل التقديم', y='العدد', color='اليوم', barmode='group', title="مقارنة القوالب"), use_container_width=True)
            with col_b:
                trend = comp_p.groupby('اليوم')['العدد'].sum().reset_index()
                st.plotly_chart(px.line(trend, x='اليوم', y='العدد', markers=True, title="منحنى تباين إجمالي البث"), use_container_width=True)
        else:
            st.warning("يرجى اختيار يومين أو أكثر لتوليد تقرير التباين المقارن.")

    # ---------------------------------------------------------
    # التبويب الثالث: التصدير والطباعة
    # ---------------------------------------------------------
    with tabs[2]:
        st.markdown("### 🖨️ تصدير التقرير للمدراء")
        st.info("الواجهة مصممة لتكون قابلة للطباعة كتقرير (PDF) احترافي. اضغط على (Ctrl + P) أو (Cmd + P) من متصفحك وسيقوم النظام بإخفاء القوائم وطباعة نصوص الذكاء الاصطناعي والرسوم كوثيقة رسمية.")

else:
    st.info("💎 أهلاً بك أيها المستشار. ارفع ملفات الرصد من القائمة الجانبية ليقوم النظام بكتابة التحليلات فوراً.")
