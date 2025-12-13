# SOLID Principle 
# SOLID is a set of 5 design rules that make code easier to change, 
# test, and extend without breaking existing behavior.

# S - Single Responsibility Principle 
    # A Class should have one job.

# O - Open/Closed Principle
    # Code should be open for extension but closed for modification.
    # Add new behavior by adding new code, not by editing stable code.

# L - Liskov Substitution Principle
    # objects of a superclass should be replaceable by objects of its subclasses without affecting the correctness
    # of the program, ensuring that derived classes behave as expected by the base class.

# I - Interface Segragation Principle
    # interfaces should be split into smaller, role-specific ones, ensuring classes only implement methods relevant to
    # them, which leads to more flexible, maintainable, and less coupled code.

# D - Dependency Inversion Principle
    # High-Level logic should depend on abstractions, not concrete implementations.
    # High-level modules should not depend on low-level modules; both should depend on abstractions.

from __future__ import annotations
from dataclasses import dataclass
