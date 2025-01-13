import requests
from datetime import datetime, timedelta
import re

KEYWORDS = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик']
HH_API_URL = "https://api.hh.ru/vacancies"

def get_api_params():
    # Формирование параметров для API
    return {
        'text': ' OR '.join(KEYWORDS),  # Поиск по ключевым словам
        'area': 1,  # Регион Россия
        'date_from': (datetime.utcnow() - timedelta(days=1)).isoformat(),  # Последние 24 часа
        'per_page': 10,
        'page': 0,
        'only_with_salary': False
    }

def fetch_vacancy_details(vacancy_url):
    # Получение детальной информации по вакансии
    details = requests.get(vacancy_url).json()
    description = re.sub(r'<.*?>', '', details.get('description', 'Нет описания'))
    return {
        'name': details.get('name', 'Не указано'),
        'description': description,
        'skills': ', '.join(skill['name'] for skill in details.get('key_skills', [])),
        'company': details.get('employer', {}).get('name', 'Не указано'),
        'salary': format_salary(details.get('salary')),
        'area': details.get('area', {}).get('name', 'Не указано'),
        'published_at': details.get('published_at', 'Не указано')
    }

def sort_vacancies_by_date(vacancies):
    # Сортировка вакансий по дате публикации
    return sorted(
        vacancies,
        key=lambda x: datetime.fromisoformat(fix_iso_format(x['published_at'])),
        reverse=True
    )

def fetch_vacancies():
    # Основная функция для получения и обработки вакансий
    api_params = get_api_params()
    response = requests.get(HH_API_URL, params=api_params)
    response.raise_for_status()  # Проверка статуса ответа
    vacancies = response.json().get('items', [])

    detailed_vacancies = [fetch_vacancy_details(vacancy['url']) for vacancy in vacancies]
    return sort_vacancies_by_date(detailed_vacancies)

def fix_iso_format(date_str):
    # Исправление формата даты ISO
    if '+' in date_str and ':' not in date_str.split('+')[-1]:
        date_str = date_str[:-2] + ':' + date_str[-2:]
    return date_str

def format_salary(salary):
    # Форматирование информации о зарплате
    if not salary:
        return "Не указано"
    if salary['currency'] != 'RUR':
        return "Не в рублях"
    return f"{salary['from'] or ''} - {salary['to'] or ''} {salary['currency']}"
