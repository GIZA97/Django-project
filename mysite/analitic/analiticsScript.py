import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import re
import requests
import xml.etree.ElementTree as ET

# Функция для получения курсов валют из API Центрального банка России
def get_all_currency():
    month = 1
    year = 2003
    all_currency = 'BYR,USD,EUR,KZT,UAH,AZN,KGS,UZS,GEL'.split(',')  # Список кодов валют для отслеживания
    len_cur = len(all_currency)
    result = {}
    while True:
        if year == 2024 and month == 12:  # Завершение цикла при достижении декабря 2024 года
            break
        month_str = str(month)
        if month < 10:  # Добавление ведущего нуля для месяцев с одной цифрой
            month_str = '0' + month_str
        try:
            # Запрос данных с сайта ЦБ РФ
            response = requests.get(f'https://cbr.ru/scripts/XML_daily.asp?date_req=01/{month_str}/{year}')
            result[f'{year}-{month_str}'] = {}
            root = ET.fromstring(response.content)  # Парсинг XML-ответа
            for item in root.findall('Valute'):
                name = item.find('CharCode').text  # Извлечение кода валюты
                try:
                    index = all_currency.index(name) + 1  # Проверка наличия валюты в списке
                    # Извлечение курса валюты и преобразование его в float
                    result[f'{year}-{month_str}'][name] = float(item.find('VunitRate').text.replace(',', '.'))
                except ValueError:
                    continue  # Пропуск валют, не входящих в список
        except Exception:
            continue  # Игнорирование ошибок запроса
        if month == 12:  # Переход на следующий год
            month = 1
            year += 1
        else:
            month += 1
    return result

# Функция для сохранения графиков в формате PNG
# data - данные для графика
# title - заголовок графика
# ylabel, xlabel - подписи осей
# filename - имя файла для сохранения
def save_plot(data, title, ylabel, xlabel, filename):
    plt.figure(figsize=(10, 6))
    plt.barh(data.keys(), data.values(), color='red')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=0)
    plt.tight_layout(pad=2.0)
    plt.savefig(filename)  # Сохранение графика в файл
    plt.close()

# Получаем курсы валют из API Центрального банка России в виде словаря
EXCHANGE_RATES = get_all_currency()

# Файл с данными о вакансиях
PARSING_FILE = 'vacancies_2024.csv'

# Ограничение на максимальную зарплату
MAX_SALARY = 10000000

# Ключевые слова для поиска вакансий (взяты с Ulern)
KEYWORDS = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик']

# Обработка всех вакансий и сохранение общей аналитики
def process_all_vacancies():
    chunksize = 100000
    all_data = []

    for chunk in pd.read_csv(PARSING_FILE, chunksize=chunksize, encoding='utf-8',
                             usecols=['name', 'key_skills', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']):
        chunk['published_at'] = pd.to_datetime(chunk['published_at'], errors='coerce', utc=True)
        chunk['published_month'] = chunk['published_at'].dt.tz_localize(None).dt.to_period('M')

        def convert_salary(row):
            salary_from = row['salary_from'] or 0
            salary_to = row['salary_to'] or 0
            avg_salary = (salary_from + salary_to) / 2 if (salary_from + salary_to) > 0 else None
            if avg_salary and avg_salary <= MAX_SALARY:
                currency = row['salary_currency']
                month = str(row['published_month'])
                rate = EXCHANGE_RATES.get(month, {}).get(currency, 1)
                return avg_salary * rate
            return None

        chunk['salary_rub'] = chunk.apply(convert_salary, axis=1)
        all_data.append(chunk)

    all_data = pd.concat(all_data)

    total_vacancies = all_data['salary_rub'].notna().sum()
    min_vacancies_for_city = total_vacancies // 100

    stats = {}

    # Динамика уровня зарплат по годам
    salary_trend = all_data.groupby(all_data['published_month'].dt.year)['salary_rub'].mean().to_dict()
    stats['salary_trend'] = salary_trend
    save_plot(salary_trend, 'Динамика уровня зарплат по годам', 'Год', 'Средняя зарплата (руб.)', 'dyn_sal_city.png')

    # Динамика количества вакансий по годам
    vacancy_trend = all_data.groupby(all_data['published_month'].dt.year).size().to_dict()
    stats['vacancy_trend'] = vacancy_trend
    save_plot(vacancy_trend, 'Динамика количества вакансий по годам', 'Год', 'Количество вакансий', 'dyn_count_vac.png')

    # Уровень зарплат по городам
    city_vacancies = all_data.groupby('area_name').size()
    valid_cities = city_vacancies[city_vacancies >= min_vacancies_for_city].index
    salary_by_city = all_data[all_data['area_name'].isin(valid_cities)].groupby('area_name')['salary_rub'].mean().sort_values(ascending=False).to_dict()
    stats['salary_by_city'] = salary_by_city
    save_plot(salary_by_city, 'Уровень зарплат по городам', 'Город', 'Средняя зарплата (руб.)', 'lev_sal_city.png')

    # Доля вакансий по городам
    vacancy_share_by_city = (all_data[all_data['area_name'].isin(valid_cities)]['area_name']
                              .value_counts(normalize=True) * 100).sort_values(ascending=False).to_dict()
    stats['vacancy_share_by_city'] = vacancy_share_by_city
    save_plot(vacancy_share_by_city, 'Доля вакансий по городам', 'Город', 'Доля вакансий (%)', 'rate_vac_city.png')

    # TТОП-20 навыков по годам
    def extract_skills(key_skills):
        if pd.isna(key_skills):
            return []
        return [skill.strip() for skill in re.split(r',|\n', key_skills) if skill.strip()]

    all_data['skills'] = all_data['key_skills'].apply(extract_skills)
    skill_trends = {}
    for year, group in all_data.groupby(all_data['published_month'].dt.year):
        all_skills = group['skills'].explode()
        skill_trends[year] = all_skills.value_counts().head(20).to_dict()

    stats['top_skills'] = skill_trends
    for year, skills in skill_trends.items():
        save_plot(skills, f'ТОП-20 навыков за {year}', 'Навык', 'Количество упоминаний', f'skills_{year}_g.png')

    # Сохранение в json файл
    with open('general.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

# Запуск обработки данных
process_all_vacancies()
