import streamlit as st
import pandas as pd
import os
import ast
import subprocess
import sys 
from analysis.visualization import (
    setup_style, 
    plot_vacancies_by_category, 
    plot_salary_comparison_global,
    plot_remote_vs_office, 
    plot_top_cities,
    plot_salary_distribution_by_grade
)

# 1. Налаштування сторінки
st.set_page_config(page_title="Аналітика ІТ-ринку (DOU)", page_icon="📊", layout="wide")
setup_style() # Налаштовуємо стиль один раз

DATA_PATH = "data/processed/dou_all_categories_final.csv"

def run_parser():
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH)
    def safe_literal_eval(val):
        try: return ast.literal_eval(val)
        except: return []
    if 'City_List' in df.columns:
        df['City_List'] = df['City_List'].apply(safe_literal_eval)
    return df

# --- SIDEBAR ---
st.sidebar.title("Налаштування ⚙️")
if st.sidebar.button("🔄 Оновити дані (Парсинг)", use_container_width=True):
    with st.spinner("Збираємо дані..."):
        if run_parser():
            st.sidebar.success("Оновлено!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.sidebar.error("Помилка парсингу.")

# --- MAIN SCREEN ---
st.title("📊 Інтерактивний дашборд ІТ-вакансій (DOU)")
df = load_data()

if df is None or df.empty:
    st.warning("⚠️ Дані відсутні. Оновіть систему.")
else:
    tab1, tab2 = st.tabs(["🌐 Загальна аналітика", "🎯 Аналіз за категорією"])

    with tab1:
        st.header("Огляд ринку")
        
        # Ряд 1: Попит та Зарплати
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(plot_vacancies_by_category(df))
        with col2:
            st.pyplot(plot_salary_comparison_global(df))

        # Ряд 2: Міста та Remote
        col3, col4 = st.columns(2)
        with col3:
            st.pyplot(plot_top_cities(df))
        with col4:
            st.pyplot(plot_remote_vs_office(df))

    with tab2:
        categories = sorted(df['Category'].unique().tolist())
        selected_cat = st.selectbox("Оберіть категорію:", categories)
        df_cat = df[df['Category'] == selected_cat]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.pyplot(plot_remote_vs_office(df_cat))
        with col_b:
            st.pyplot(plot_top_cities(df_cat))

        st.divider()
        st.pyplot(plot_salary_distribution_by_grade(df_cat))