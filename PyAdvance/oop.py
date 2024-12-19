from abc import ABC, abstractmethod

class Employee(ABC):
    def __init__(self, name, salary):
        self.__name = name
        self.__salary = salary

    @property
    def name(self):
        return self.__name

    @property
    def salary(self):
        return self.__salary

    @salary.setter
    def salary(self, value):
        if value < 0:
            raise ValueError("Salary must not be non-negative")
        self.__salary = value

    @abstractmethod
    def calculate_bonus(self):
        """ Abstract method to be implemented by subclass"""
        pass

    def __str__(self):
        return f"{self.name}, Salary: {self.salary}"

class Developer(Employee):
    def __init__(self, name, salary, programming_language):
        super().__init__(name,salary)
        self.programming_language = programming_language
    
    def calculate_bonus(self):
        # bonus is 10% of salary
        return self.salary * 0.1

    def __str__(self):
        return f"{super().__str__()}, language: {self.programming_language}"

class Manager(Employee):
    def __init__(self, name, salary, team_size):
        super().__init__(name, salary)
        self.team_size = team_size

    def calculate_bonus(self):
        # Bonus is 15% of the salary
        return self.salary * 0.15 + self.team_size * 100

    def __str__(self):
        return f"{super().__str__()}, team_size: {self.team_size}"

def print_employee(employee):
    print(employee)
    print(f"Bonus: {employee.calculate_bonus(): .2f}")

if __name__ == "__main__":
    dev = Developer("Aj Borbe", 120000, "Python")
    mgr = Manager("Mei Borbe", 180000, 10)

    print("Employee Details:")
    print_employee(dev)
    print()
    print_employee(mgr)