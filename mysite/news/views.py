from django.shortcuts import render
import pandas as pd
import json
import os
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def genstat(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'general.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # Таблица salary_trend
    salary_trend = data.get('salary_trend', {})
    df_salary = pd.DataFrame(salary_trend.items(), columns=['Год', 'Зарплата'])
    df_salary = df_salary.iloc[2:]  # Исключаем первые две строки
    table_salary_html = df_salary.to_html(classes='data', index=False)
    
    # Таблица vacancy_trend
    vacancy_trend = data.get('vacancy_trend', {})
    df_vacancy = pd.DataFrame(vacancy_trend.items(), columns=['Год', 'Количество вакансий'])
    table_vacancy_html = df_vacancy.to_html(classes='data', index=False)

    # Таблица salary_by_city
    salary_by_city = data.get('salary_by_city', {})
    df_city = pd.DataFrame(salary_by_city.items(), columns=['Город', 'Зарплата'])
    table_city_html = df_city.to_html(classes='data', index=False)

    # Таблица salary_by_city
    vacancy_share_by_city = data.get('vacancy_share_by_city', {})
    df_rate = pd.DataFrame(vacancy_share_by_city.items(), columns=['Город', 'Доля вакансий по городам'])
    table_rate_html = df_rate.to_html(classes='data', index=False)

    # Таблица salary_by_city
    vacancy_share_by_city = data.get('vacancy_share_by_city', {})
    df_rate = pd.DataFrame(vacancy_share_by_city.items(), columns=['Город', 'Доля вакансий по городам'])
    table_rate_html = df_rate.to_html(classes='data', index=False)

    top_skills = data.get('top_skills',{})

    # Таблица top_skills_2015
    top_skills_2015 = top_skills.get('2015', {})
    df_2015 = pd.DataFrame(top_skills_2015.items(), columns=['Навык', 'Количество'])
    table_2015_html = df_2015.to_html(classes='data', index=False)

    # Таблица top_skills_2016
    top_skills_2016 = top_skills.get('2016', {})
    df_2016 = pd.DataFrame(top_skills_2016.items(), columns=['Навык', 'Количество'])
    table_2016_html = df_2016.to_html(classes='data', index=False)

    # Таблица top_skills_2017
    top_skills_2017 = top_skills.get('2017', {})
    df_2017 = pd.DataFrame(top_skills_2017.items(), columns=['Навык', 'Количество'])
    table_2017_html = df_2017.to_html(classes='data', index=False)

    # Таблица top_skills_2018
    top_skills_2018 = top_skills.get('2018', {})
    df_2018 = pd.DataFrame(top_skills_2018.items(), columns=['Навык', 'Количество'])
    table_2018_html = df_2018.to_html(classes='data', index=False)

    # Таблица top_skills_2019
    top_skills_2019 = top_skills.get('2019', {})
    df_2019 = pd.DataFrame(top_skills_2019.items(), columns=['Навык', 'Количество'])
    table_2019_html = df_2019.to_html(classes='data', index=False)

    # Таблица top_skills_2020
    top_skills_2020 = top_skills.get('2020', {})
    df_2020 = pd.DataFrame(top_skills_2020.items(), columns=['Навык', 'Количество'])
    table_2020_html = df_2020.to_html(classes='data', index=False)

    # Таблица top_skills_2021
    top_skills_2021 = top_skills.get('2021', {})
    df_2021 = pd.DataFrame(top_skills_2021.items(), columns=['Навык', 'Количество'])
    table_2021_html = df_2021.to_html(classes='data', index=False)

    # Таблица top_skills_2022
    top_skills_2022 = top_skills.get('2022', {})
    df_2022 = pd.DataFrame(top_skills_2022.items(), columns=['Навык', 'Количество'])
    table_2022_html = df_2022.to_html(classes='data', index=False)

    # Таблица top_skills_2023
    top_skills_2023 = top_skills.get('2023', {})
    df_2023 = pd.DataFrame(top_skills_2023.items(), columns=['Навык', 'Количество'])
    table_2023_html = df_2023.to_html(classes='data', index=False)

    # Таблица top_skills_2024
    top_skills_2024 = top_skills.get('2024', {})
    df_2024 = pd.DataFrame(top_skills_2024.items(), columns=['Навык', 'Количество'])
    table_2024_html = df_2024.to_html(classes='data', index=False)

    # Передача обеих таблиц в шаблон
    return render(request, 'genstat.html', {
        'table_salary': table_salary_html,
        'table_vacancy': table_vacancy_html,
        'table_city': table_city_html,
        'table_rate': table_rate_html,
        'table_2015': table_2015_html,
        'table_2016': table_2016_html,
        'table_2017': table_2017_html,
        'table_2018': table_2018_html,
        'table_2019': table_2019_html,
        'table_2020': table_2020_html,
        'table_2021': table_2021_html,
        'table_2022': table_2022_html,
        'table_2023': table_2023_html,
        'table_2024': table_2024_html,
    })
def relev(request):
    return render(request, 'relev.html')

def contact(request):
    return render(request, 'contact.html')