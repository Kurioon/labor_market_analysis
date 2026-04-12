import os
import pandas as pd
from scraper.dou_parser import get_dou_vacancies
from analysis.data_cleaning import clean_dou_data

def main():
    categories = ["Python", "Front-end", "QA", "DevOps", "AI%2FML"]
    all_cleaned_data = []

    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    for cat in categories:
        print(f"\n--- Обробка категорії: {cat} ---")
        
        safe_cat_name = cat.lower().replace('%2f', '_')
        raw_file_path = f"data/raw/dou_{safe_cat_name}_raw.csv"
        cleaned_file_path = f"data/processed/dou_{safe_cat_name}_cleaned.csv"

        # 1. ЕТАП ЗБОРУ (ПАРСИНГ)
        print("1. Запуск парсера...")
        raw_df = get_dou_vacancies(cat)
        
        if raw_df is None or raw_df.empty:
            print(f"Дані для категорії {cat} не зібрано. Пропускаємо очищення.")
            continue

        # 2. ЕТАП ОЧИЩЕННЯ
        if os.path.exists(raw_file_path):
            print("2. Запуск модуля очищення...")
            cleaned_df = clean_dou_data(raw_file_path, cleaned_file_path, cat)
            all_cleaned_data.append(cleaned_df)
        else:
            print(f"Помилка: Файл {raw_file_path} не знайдено. Очищення неможливе.")

    # 3. ЕТАП ОБ'ЄДНАННЯ
    if all_cleaned_data:
        print("\n--- Формування фінального датасету ---")
        final_df = pd.concat(all_cleaned_data, ignore_index=True)
        final_path = "data/processed/dou_all_categories_final.csv"
        
        # Зберігаємо фінальний результат
        final_df.to_csv(final_path, index=False, encoding='utf-8-sig')
        print(f"Система успішно завершила роботу. Загалом вакансій: {len(final_df)}.")
        print(f"Файл збережено за шляхом: {final_path}")
    else:
        print("\nНемає даних для об'єднання.")

if __name__ == "__main__":
    main()