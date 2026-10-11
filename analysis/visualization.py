import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import ast

def setup_style():
    # Налаштування єдиного стилю для всіх графіків.
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams['font.size'] = 12
    plt.rcParams['figure.figsize'] = (10, 6)

def plot_vacancies_by_category(df):
    # Графік 1: Кількість вакансій за категоріями.
    fig = plt.figure() 
    
    category_counts = df['Category'].value_counts()
    
    ax = sns.barplot(x=category_counts.index, y=category_counts.values, hue=category_counts.index, legend=False)
    
    plt.title('Кількість вакансій за ІТ-напрямками', fontsize=16, pad=15)
    plt.xlabel('Категорія', fontsize=12)
    plt.ylabel('Кількість вакансій', fontsize=12)
    
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points')
    
    plt.tight_layout()
    return fig 

def plot_salary_comparison_global(df):
    # Графік 5: Порівняння медіанних зарплат за категоріями.
    fig = plt.figure(figsize=(12, 6))
    salary_df = df.dropna(subset=['Salary_min'])
    order = salary_df.groupby('Category')['Salary_min'].median().sort_values(ascending=False).index
    sns.boxplot(data=salary_df, x='Category', y='Salary_min', order=order)
    plt.title('Порівняння рівня зарплат за категоріями (Median)', fontsize=16)
    plt.ylabel('Зарплата (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def plot_salary_distribution_by_grade(df):
    # Графік 2: Розподіл зарплат за грейдами (Boxplot).
    fig = plt.figure(figsize=(12, 7)) 
    
    salary_df = df.dropna(subset=['Salary_min'])
    salary_df = salary_df[salary_df['Grade'] != 'Not Specified']
    
    grade_order = ['Junior', 'Middle', 'Senior']
    
    sns.boxplot(data=salary_df, x='Grade', y='Salary_min', hue='Grade', hue_order=grade_order, showfliers=False, boxprops={'alpha': 0.7})
    sns.stripplot(data=salary_df, x='Grade', y='Salary_min', hue='Grade', hue_order=grade_order, dodge=True, palette='dark:black', alpha=0.5, jitter=True)
    
    plt.title('Розподіл зарплати за грейдами', fontsize=16, pad=15)
    plt.xlabel('Грейд', fontsize=12)
    plt.ylabel('Зарплата (USD)', fontsize=12)
    
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[:3], labels[:3], title='Грейд')
    
    plt.tight_layout()
    return fig 

def plot_remote_vs_office(df):
    # Графік 3: Співвідношення віддаленої роботи до офісної/змішаної.
    fig = plt.figure(figsize=(8, 8)) 
    
    remote_counts = df['Is_Remote'].value_counts()
    labels = ['Віддалено (Remote)', 'Офіс / Гібрид'] if remote_counts.index[0] == True else ['Офіс / Гібрид', 'Віддалено (Remote)']
    
    plt.pie(remote_counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'], explode=(0.05, 0))
    plt.title('Частка вакансій з можливістю віддаленої роботи', fontsize=16)
    
    plt.tight_layout()
    return fig 

def plot_top_cities(df):
    # Графік 4: Топ-10 міст за кількістю вакансій.
    fig = plt.figure(figsize=(12, 6))

    df_cities = df.copy()
    
    def safe_literal_eval(val):
        if isinstance(val, list):
            return val
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
            
    df_cities['City_List'] = df_cities['City_List'].apply(safe_literal_eval)
    
    df_exploded = df_cities.explode('City_List')
    
    physical_cities = df_exploded[~df_exploded['City_List'].isin(['Remote Only', 'Other', 'Not Specified'])]
    
    top_10_cities = physical_cities['City_List'].value_counts().head(10)
    
    if not top_10_cities.empty:
        ax = sns.barplot(x=top_10_cities.values, y=top_10_cities.index, hue=top_10_cities.index, legend=False)
        plt.title('Топ-10 міст за кількістю вакансій', fontsize=16, pad=15)
        plt.xlabel('Кількість вакансій', fontsize=12)
        plt.ylabel('Місто', fontsize=12)
    else:
        plt.title('Топ-10 міст за кількістю вакансій', fontsize=16, pad=15)
        plt.text(0.5, 0.5, 'Усі вакансії лише для віддаленої роботи', 
                 ha='center', va='center', fontsize=14, color='gray')
        plt.axis('off')

    plt.tight_layout()
    return fig

def generate_all_reports(input_file):
    # Головна функція для генерації всіх графіків.
    print("Початок генерації візуалізацій...")
    
    output_dir = 'reports/figures'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        df = pd.read_csv(input_file)
        print(f"Дані завантажено. Всього записів: {len(df)}")
    except FileNotFoundError:
        print(f"Помилка: Файл {input_file} не знайдено. Спочатку збери дані (запусти main.py).")
        return
        
    setup_style()
    
    fig1 = plot_vacancies_by_category(df)
    fig1.savefig(os.path.join(output_dir, 'vacancies_by_category.png'), dpi=300)
    plt.close(fig1)
    
    fig2 = plot_salary_comparison_global(df)
    fig2.savefig(os.path.join(output_dir, 'global_salary_comparison.png'), dpi=300)
    plt.close(fig2)
    
    fig3 = plot_remote_vs_office(df)
    fig3.savefig(os.path.join(output_dir, 'remote_vs_office_pie.png'), dpi=300)
    plt.close(fig3)
    
    fig4 = plot_top_cities(df)
    fig4.savefig(os.path.join(output_dir, 'top_10_cities.png'), dpi=300)
    plt.close(fig4)
    
    print(f"\nУсі візуалізації успішно створено у папці: {output_dir}/")