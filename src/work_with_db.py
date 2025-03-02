import psycopg2


class DBManager:
    def __init__(self, dbname, user, password, host="localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании."""
        self.cur.execute(
            "SELECT e.name, COUNT(v.vacancy_id) "
            "FROM employers e "
            "LEFT JOIN vacancies v ON e.employer_id = v.employer_id "
            "GROUP BY e.name"
        )
        return self.cur.fetchall()

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию."""
        self.cur.execute(
            "SELECT e.name, v.title, v.salary_from, v.salary_to, v.currency, v.url "
            "FROM vacancies v "
            "JOIN employers e ON v.employer_id = e.employer_id"
        )
        return self.cur.fetchall()

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям."""
        self.cur.execute(
            "SELECT AVG((salary_from + salary_to) / 2) "
            "FROM vacancies "
            "WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL"
        )
        return self.cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        self.cur.execute(
            "SELECT e.name, v.title, v.salary_from, v.salary_to, v.currency, v.url "
            "FROM vacancies v "
            "JOIN employers e ON v.employer_id = e.employer_id "
            "WHERE (salary_from + salary_to) / 2 > %s",
            (avg_salary,)
        )
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова."""
        self.cur.execute(
            "SELECT e.name, v.title, v.salary_from, v.salary_to, v.currency, v.url "
            "FROM vacancies v "
            "JOIN employers e ON v.employer_id = e.employer_id "
            "WHERE v.title ILIKE %s",
            (f"%{keyword}%",)
        )
        return self.cur.fetchall()

    def close(self):
        """Закрывает соединение с БД."""
        self.cur.close()
        self.conn.close()
