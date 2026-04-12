import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_dou_vacancies(category="Python"):
    print(f"Починаємо збір вакансій для категорії: {category}")
    
    url = f"https://jobs.dou.ua/vacancies/?category={category}"
    
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    wait = WebDriverWait(driver, 3)

    driver.get(url)
    
    # Проклікуємо "Бідьше вакансій"
    while True:
        try:
            more_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.more-btn > a")))
            more_btn.click()
            time.sleep(1)
        except (NoSuchElementException, TimeoutException):
            print("Всі вакансії завантажено.")
            break
            
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit() 
    
    vacancies_data = []
    
    vacancy_cards = soup.find_all('li', class_='l-vacancy')
    
    for card in vacancy_cards:
        title_element = card.find('a', class_='vt')
        title = title_element.text.strip() if title_element else None
        
        url = title_element['href'] if title_element else None
        
        company_element = card.find('a', class_='company')
        company = company_element.text.strip() if company_element else None
        
        city_element = card.find('span', class_='cities')
        city = city_element.text.strip() if city_element else None
        
        salary_element = card.find('span', class_='salary')
        salary_raw = salary_element.text.strip() if salary_element else None
        
        vacancies_data.append({
            'Category': category,
            'Title': title,
            'Company': company,
            'Location': city,
            'Salary_raw': salary_raw,
            'URL': url
        })
        
    df = pd.DataFrame(vacancies_data)
    
    output_path = f"data/raw/dou_{category.lower().replace('%2f', '_')}_raw.csv" 

    # Створюємо файл якщо його немає
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Зібрано {len(df)} вакансій. Збережено у {output_path}")
    
    return df

if __name__ == "__main__":
    df_vacancies = get_dou_vacancies("QA")
    print(df_vacancies.head())