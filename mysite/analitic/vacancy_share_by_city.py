from . import analiticsScript
import pandas as pd
import re


EXCHANGE_RATES = analiticsScript.get_all_currency()

# Файл с данными о вакансиях
PARSING_FILE = 'vacancies_2024.csv'

# Ограничение на максимальную зарплату
MAX_SALARY = 10000000

# Ключевые слова для поиска вакансий (взяты с Ulern)
KEYWORDS = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик']

def process_data_need_vac():
    chunksize = 100000
    php_prof_vac = []

    # Чтение файла с вакансиями по частям
    for chunk in pd.read_csv(PARSING_FILE, usecols=['name', 'key_skills', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'], chunksize=chunksize, encoding='utf-8'):
        # Преобразование столбца даты
        chunk['published_at'] = pd.to_datetime(chunk['published_at'], errors='coerce', utc=True)
        chunk['published_month'] = chunk['published_at'].dt.tz_localize(None).dt.to_period('M')

        # Фильтрация по ключевым словам вакансии
        pattern_csharp = r'|'.join([re.escape(keyword) for keyword in KEYWORDS])

        # Фильтрация строк и проверка на вхождение ключевых слов, игнорируя регистр
        php_prof = chunk.loc[chunk['name'].str.contains(pattern_csharp, case=False, na=False)]

        # Преобразование зарплаты в рубли
        def convert_salary(row):
            salary_from = row['salary_from'] or 0
            salary_to = row['salary_to'] or 0
            avg_salary = (salary_from + salary_to) / 2 if (salary_from + salary_to) > 0 else None

            if avg_salary and avg_salary <= MAX_SALARY:
                currency = row['salary_currency']
                month = str(row['published_month'])
                rate = EXCHANGE_RATES.get(month, {}).get(currency, 1)  # Получение курса валюты
                return avg_salary * rate

            return None

        # Применение функции преобразования зарплаты
        php_prof.loc[:, 'salary_rub'] = php_prof.apply(convert_salary, axis=1)

        # Добавляем обработанные данные в общий список
        php_prof_vac.append(php_prof)

    # Объединение всех частей данных
    all_vac_concat = pd.concat(php_prof_vac)

    # Общий подсчет вакансий с зарплатой в рублях
    total_vacancies_rub = all_vac_concat['salary_rub'].notna().sum()

    # Вычисление минимального количества вакансий для города (1% от общего числа)
    min_vacancies_for_city = total_vacancies_rub // 100

    # Аналитика
    stats = {}

    city_vacancies = all_vac_concat.groupby('area_name').size()
    valid_cities = city_vacancies[city_vacancies >= min_vacancies_for_city].index
    salary_by_city = all_vac_concat[all_vac_concat['area_name'].isin(valid_cities)].groupby('area_name')['salary_rub'].mean().sort_values(ascending=False).to_dict()
    stats['salary_by_city'] = salary_by_city
    analiticsScript.save_plot(salary_by_city, 'Уровень зарплат по городам', 'Город', 'Средняя зарплата (руб.)', 'level_sal_cities.png')

