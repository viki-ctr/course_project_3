from typing import Any

import psycopg2


def create_database(dbname: str, params: dict) -> None:
    """
    Создает базу данных, если она не существует.
    :param dbname: Имя базы данных.
    :param params: Параметры подключения к базе данных.
    """

    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"База данных {dbname} создана.")
    else:
        print(f"База данных {dbname} уже существует.")

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=dbname, **params)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employers (
            employer_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            website VARCHAR(255)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id SERIAL PRIMARY KEY,
            employer_id INT REFERENCES employers(employer_id),
            title VARCHAR(255) NOT NULL,
            salary_from INT,
            salary_to INT,
            currency VARCHAR(10),
            url VARCHAR(255) NOT NULL
        )
        """
    )

    conn.commit()
    cur.close()
    conn.close()


def save_data_to_database(
    companies_data: list[dict[str, Any]], vacancies_data: list[dict], params: dict, database_name: str = "headhunter"
) -> None:
    """
    Сохранение данных о компаниях и вакансиях в базу данных.
    :param companies_data: Данные о компаниях.
    :param vacancies_data: Данные о вакансиях.
    :param params: Параметры подключения к базе данных.
    :param database_name: Имя базы данных.
    """
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        for company in companies_data:
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, description, website)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING
                """,
                (
                    company["company_id"],
                    company["company_name"],
                    company.get("description", ""),
                    company.get("company_url", ""),
                ),
            )

        for vacancy in vacancies_data:
            salary_from = 0
            salary_to = 0
            currency = 0
            cur.execute(
                """
                INSERT INTO vacancies (vacancy_id, employer_id, title, salary_from, salary_to, currency, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO NOTHING
                """,
                (
                    vacancy["vacancy_id"],
                    vacancy["company_id"],
                    vacancy["name"],
                    salary_from,
                    salary_to,
                    currency,
                    vacancy["url"]
                ),
            )

    conn.commit()
    conn.close()
