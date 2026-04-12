import pandas as pd
import re
import os

def clean_dou_data(input_path, output_path, category):
    print(f"Очищення даних для категорії: {category}...")
    df = pd.read_csv(input_path)
    
    # 1. Витягування грейду (Junior/Middle/Senior) з назви вакансії
    def extract_grade(title):
        title_lower = str(title).lower()
        if 'junior' in title_lower or 'trainee' in title_lower:
            return 'Junior'
        elif 'middle' in title_lower:
            return 'Middle'
        elif 'senior' in title_lower or 'lead' in title_lower or 'architect' in title_lower:
            return 'Senior'
        else:
            return 'Not Specified'
            
    df['Grade'] = df['Title'].apply(extract_grade)
    
    # 2. Обробка зарплати (перетворення тексту "$2000 - $4000" у два окремі числові стовпці)
    def parse_salary(salary_str):
        if pd.isna(salary_str):
            return pd.Series([None, None])
        
        clean_str = str(salary_str).replace(' ', '').replace('$', '')
        
        numbers = re.findall(r'\d+', clean_str)
        
        if len(numbers) == 2:
            return pd.Series([int(numbers[0]), int(numbers[1])])
        elif len(numbers) == 1:
            return pd.Series([int(numbers[0]), int(numbers[0])])
        else:
            return pd.Series([None, None])
            
    df[['Salary_min', 'Salary_max']] = df['Salary_raw'].apply(parse_salary)
    
    # 3. Витягування навичок
    skills_dictionary = {
        "Python": ['django', 'flask', 'fastapi', 'sql', 'docker', 'aws', 'linux', 'git', 'postgresql'],
        "Front-end": ['react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css', 'redux', 'figma'],
        "QA": ['selenium', 'cypress', 'postman', 'jmeter', 'sql', 'jira', 'pytest', 'appium'],
        "DevOps": ['docker', 'kubernetes', 'aws', 'terraform', 'jenkins', 'linux', 'ansible', 'ci/cd', 'bash'],
        "AI%2FML": ['pytorch', 'tensorflow', 'scikit-learn', 'pandas', 'numpy', 'sql', 'nlp', 'cv']
    }
    
    target_skills = skills_dictionary.get(category, ['git', 'sql', 'docker', 'linux'])

    def extract_skills(title):
        title_lower = str(title).lower()
        found_skills = [skill for skill in target_skills if skill in title_lower]
        return ', '.join(found_skills) if found_skills else 'Not Specified'
        
    df['Skills'] = df['Title'].apply(extract_skills)
    
    # 4. Нормалізація локації
    def normilize_location(loc_str):
        if pd.isna(loc_str):
            return pd.Series(['Not Specified', False])
        
        loc_lower = str(loc_str).lower()
        is_remote = "віддален" in loc_lower or 'remote' in loc_lower 

        cities_found=[]
        if 'київ' in loc_lower or 'kyiv' in loc_lower: cities_found.append('Київ')
        if 'львів' in loc_lower or 'lviv' in loc_lower: cities_found.append('Львів')
        if 'дніпро' in loc_lower or 'dnipro' in loc_lower: cities_found.append('Дніпро')
        if 'івано-франківськ' in loc_lower or 'ivano-frankivsk' in loc_lower or 'франківськ' in loc_lower: cities_found.append('Івано-Франківськ')
        if 'вінниця' in loc_lower or 'vinnytsia' in loc_lower: cities_found.append('Вінниця')
        if 'одеса' in loc_lower or 'odesa' in loc_lower or 'odessa' in loc_lower: cities_found.append('Одеса')
        if 'тернопіль' in loc_lower or 'ternopil' in loc_lower: cities_found.append('Тернопіль')
        if 'харків' in loc_lower or 'kharkiv' in loc_lower: cities_found.append('Харків')
        if 'чернівці' in loc_lower or 'chernivtsi' in loc_lower: cities_found.append('Чернівці')
        if 'полтава' in loc_lower or 'poltava' in loc_lower: cities_found.append('Полтава')
        if 'черкаси' in loc_lower or 'cherkasy' in loc_lower: cities_found.append('Черкаси')
        if 'луцьк' in loc_lower or 'lutsk' in loc_lower: cities_found.append('Луцьк')
        if 'хмельницький' in loc_lower or 'khmelnytskyi' in loc_lower: cities_found.append('Хмельницький')
        if 'ужгород' in loc_lower or 'uzhhorod' in loc_lower: cities_found.append('Ужгород')
        if 'рівне' in loc_lower or 'rivne' in loc_lower: cities_found.append('Рівне')

        if not cities_found:
            cities_found = ['Remote Only'] if is_remote else ['Other']

        return pd.Series([cities_found, is_remote])
    
    df[['City_List', 'Is_Remote']] = df['Location'].apply(normilize_location)

    df = df.drop(['Salary_raw', 'Location'], axis=1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    return df

if __name__ == "__main__":
    input_file = "data/raw/dou_python_raw.csv"
    output_file = "data/processed/dou_python_cleaned.csv"
    
    os.makedirs('data/processed', exist_ok=True)
    
    if os.path.exists(input_file):
        clean_dou_data(input_file, output_file, "Python") 
    else:
        print(f"Помилка: Файл {input_file} не знайдено. Переконайтеся, що скрипт запускається з кореневої папки проєкту.")