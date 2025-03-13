from config.config import config
from src.create_table import create_database, save_data_to_database
from src.hh_parser import HeadHunterAPI
from src.work_with_db import DBManager


def main() -> None:
    """
    Главная функция проекта для взаимодействия с пользователем.
    :return: None
    """
    vacancies = []
    params = config()
    default_database_name = "headhunter"
    default_companies = [
        "HeadHunter",
        "ПАКС",
        "Level Group",
        "Роскосмос",
        "институт теплотехники",
        "сколково",
        "Дело жизни",
        "SkyPro",
        "ГИБДД",
        "DatsTeam",
    ]
    query = input(
        """Введите названия компаний через пробел, информацию о вакансиях которых вы хотели бы получить:
(По умолчанию будут использованы активные вакансии компаний:
HeadHunter, ПАКС, Level Group, Роскосмос, институт теплотехники, Сколково, Дело жизни, SkyPro, ГИБДД, DatsTeam) \n"""
    ).split()
    database_name_query = input("Введите название базы данных:\nПо умолчанию создается БД headhunter\n")
    if database_name_query:
        database_name = database_name_query
    else:
        database_name = default_database_name
    if query:
        companies_keywords = query
    else:
        companies_keywords = default_companies
    companies = HeadHunterAPI().get_companies(companies_keywords)
    for company in companies:
        vacancies.extend(HeadHunterAPI().get_vacancies(company["company_id"]))
    target_vacancy_list = list(map(lambda x: HeadHunterAPI.transfom_data(x), vacancies))

    create_database(database_name, params)
    save_data_to_database(companies, target_vacancy_list, params, database_name)
    print("Выводятся данные о выбранных компания и количестве открытых вакансий:")
    DBManager(database_name, params).get_companies_and_vacancies_count()
    case = input(
        """Мы получили данные обо всех открытых вакансиях выбранных компаний.
    Выберите расчетный случай:
    1 - Вывести все вакансии
    2 - Вывести среднюю зарплату по вакансиям
    3 - Вывести вакансии с заработной платой выше среднего
    4 - Вывести вакансии по ключевому слову
    5 - Выход\n"""
    )
    while True:
        if case == "1":
            top_n = int(input("""Введите количество вакансий для вывода: """))
            rows = DBManager(database_name, params).get_all_vacancies()
            for row in rows[:top_n]:
                print(
                    f"""Название компании:\n{row[0]}\nНазвание вакансии:\n{row[1]}
Размер заработной платы: {row[2]}р.
Ссылка на вакансию: {row[3]}"""
                )

        elif case == "2":
            print(
                f"Средняя зарплата всех полученных вакансий: {DBManager(database_name, params).get_avg_salary()}р.\n"
            )

        elif case == "3":
            rows = DBManager(database_name, params).get_vacancies_with_higher_salary()
            top_n = int(input("""Введите количество вакансий для вывода: """))
            for row in rows[:top_n]:
                print(
                    f"""Название вакансии:\n{row[2]} Размер заработной платы: {row[3]}р.\n"""
                )

        elif case == "4":
            keyword = input("Введите ключевое слово в названии вакансии: ")
            rows = DBManager(database_name, params).get_vacancies_with_keyword(keyword)
            for row in rows:
                print(f"""Название вакансии:\n{row[2]} Размер заработной платы: {row[3]}р.\n""")

        elif case == "5":
            print("Спасибо! Приходите еще!")
            break

        else:
            case = input("Неправильно выбран расчетный случай, попробуйте еще раз: ")
            break

        case = input("Выберите расчетный случай от 1 до 5: ")


if __name__ == "__main__":
    main()
