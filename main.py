from sqlalchemy import create_engine, ForeignKey, Column, String, DateTime, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

DRAFT = "Черновик"
ACTIVE = "Активен"
COMPLETED = "Завершен"


class Project(Base):
    __tablename__ = "projects"


    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    date_creation = Column("date_creation", DateTime)
    contracts = relationship("Contract", back_populates="projects")


    @classmethod
    def menu_projects(cls, session):
        table_projects = session.query(cls).all()
        for project in table_projects:
            print(f"{project.id}. Название: {project.name}")
        
        choice_id = int(input("Введите номер проекта: "))
        project = session.query(cls).filter_by(id=choice_id).first()
        
        return project


    @classmethod
    def display_table(cls, session):
        projects = session.query(cls).all()
        for project in projects:
            print(f"{project.id}-----------------------------------------------")
            print(f"Наименование: {project.name}")
            print(f"Дата создания: {project.date_creation}")
            if project.contracts:
                print("Договоры:")
                for contract in project.contracts:
                    print(f"{contract.id}. Наименование: {contract.name} Статус: {contract.status}")


    @classmethod
    def add_contract(cls, session, project, contract):
        if project and contract:
            if contract.status == ACTIVE:
                if not any(con.status == ACTIVE for con in project.contracts) or len(project.contracts)==0:
                    if contract.projects == None:
                        contract.date_signing = datetime.datetime.now()
                        contract.project_id = project.id
                        session.commit()
                        print("Договор добавлен")
                    else:
                        print("Договор исползуется в других проектах")
                else:
                    print("В проекте есть активный договор")
            elif contract.status == DRAFT:
                print("Нельзя добавить черновой договор в проект.")
            else:
                print("Нельзя добавить неактивный договор в проект.")
        else:
            print("Ошибка ввода данных")
           

    def __init__(self, name):
        self.name = name
        self.date_creation = datetime.datetime.now()
      

    def __repr__(self):
        return f"{self.name, self.date_creation}"


class Contract(Base):
    __tablename__ = "contracts"


    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    date_creation = Column("date_creation", DateTime)
    date_signing = Column("date_signing", DateTime)
    status = Column("status", String)
    project_id = Column("project_id", Integer, ForeignKey("projects.id"))
    projects = relationship("Project", back_populates="contracts")


    @classmethod
    def menu_contracts(cls, session, id_project=None):
        table_contracts = (
            session.query(cls).filter_by(project_id=id_project)
            if id_project is not None else session.query(cls).all()
        )
        for contract in table_contracts:
            print(f"{contract.id}. Название: {contract.name}")
        
        choice_id = int(input("Введите номер договора: "))
        contract = session.query(cls).filter_by(id=choice_id).first()
        
        return contract


    @classmethod
    def confirm_contract(cls, session, contract):
        if contract.project_id == None:
            contract.status = ACTIVE
            session.commit()
            print("Статус договора изменен")
        else:
            print("Документ принадлежи проекту и не может быть активирован")


    @classmethod 
    def finish_contract(cls, session, contract):
        contract.status = COMPLETED
        session.commit()
        print("Статус договора изменен")


    @classmethod
    def search_free_contract(cls, session):
        free_contract = session.query(cls).filter_by(status=ACTIVE).filter_by(project_id=None).first()
        if free_contract:
            return True
        else:
            return False


    @classmethod
    def display_table(cls, session):
        contracts = session.query(cls).all()
        for contract in contracts:
            print(f"{contract.id}-----------------------------------------------")
            print(f"Наименование: {contract.name}")
            print(f"Дата создания: {contract.date_creation}")
            print(f"Дата подписания: {contract.date_signing}")
            print(f"Статус: {contract.status}")
            if contract.projects:
                print(f"Проект: {contract.projects.name}")


    def __init__(self, name):
        self.name = name
        self.date_creation = datetime.datetime.now()
        self.date_signing = None
        self.status = DRAFT
        self.project_id = None


    def __repr__(self):
        return f"{self.name, self.date_creation, self.date_signing, self.status, self.project_id}"


def is_table_empty(session, model):
    if session.query(model).count() == 0:
        return True
    else:
        return False


def main():
    engine = create_engine('sqlite:///mydb.db')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    while True:
        print("\nГлавное меню:")
        print("1. Проект")
        print("2. Договор")
        print("3. Выйти")

        choice = input("Выберите действие (1-3): ")

        if choice == '1':
            while(True):
                print("\nПроекты:")
                print("1. Создать проект")
                print("2. Добавить договор")
                print("3. Завершить договор")
                print("4. Список проектов")
                print("5. Выйти из меню проекты")
                choice_project = input("Выберите действие (1-5): ")

                if choice_project == '1':
                    if Contract.search_free_contract(session):
                        name = input("Введите имя проекта :")
                        project = Project(name)
                        session.add(project)
                        session.commit()
                        print("Проект создан")
                    else:
                        print("В базе нет свободного договора. Создайте договор")
                elif choice_project == '2':
                    if  not is_table_empty(session, Contract) and  not is_table_empty(session, Project):
                        if Contract.search_free_contract(session):
                                Project.add_contract(
                            session,
                            Project.menu_projects(session),
                            Contract.menu_contracts(session)
                            )
                        else:
                            print("В базе нет свободного договора. Создайте договор")
                    else:
                        print("База договоров или проектов пуста")
                elif choice_project == '3':
                    if  not is_table_empty(session, Contract) and  not is_table_empty(session, Project):
                        project = Project.menu_projects(session)
                        Contract.finish_contract(
                                session, 
                                Contract.menu_contracts(session, project.id)
                            )
                    else:
                       print("База договоров или проектов пуста")
                elif choice_project == '4':
                    if  not is_table_empty(session, Project):
                        Project.display_table(session)
                    else:
                        print("База проектов пуста")
                elif choice_project == '5':
                    break

        elif choice == '2':
            while(True):
                print("\nДоговора:")
                print("1. Создать договор")
                print("2. Подтвердить договор")
                print("3. Завершить договор")
                print("4. Список договоров")
                print("5. Выйти из меню договоры")
                choice_contract = input("Выберите действие (1-5): ")

                if choice_contract == '1':
                    name = input("Введите имя договора :")
                    contract = Contract(name)
                    session.add(contract)
                    session.commit()
                    print("Договор создан")
                elif choice_contract == '2':
                    if not is_table_empty(session, Contract):
                         Contract.confirm_contract(session, Contract.menu_contracts(session))
                    else:
                         print("База договоров пуста")
                   
                elif choice_contract == '3':
                    if not is_table_empty(session, Contract):
                         Contract.finish_contract(session, Contract.menu_contracts(session))
                    else:
                         print("База договоров пуста")
                   
                elif choice_contract == '4':
                    if not is_table_empty(session, Contract):
                        Contract.display_table(session)
                    else:
                         print("База договоров пуста")
                    
                elif choice_contract == '5':
                    break
        elif choice == '3':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")

            
main()
