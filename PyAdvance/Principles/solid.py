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
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Notification:
    recipient: str
    message: str 

class Notifier(ABC):

    @abstractmethod
    def send(self, notification: Notification) -> None:
        raise NotImplementedError
    
class SMSNotifier(Notifier):
    def __init__(self, provider_api_key: str) -> None:
        self.provider_api_key = provider_api_key

    def send(self, notification: Notification) -> None:
        print(f"[SMS] to {notification.recipient} msg={notification.message}")

class SlackNotifier(Notifier):
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send(self, notification: Notification) -> None:
        print(f"[SLACK] to={notification.recipient} msg={notification.message}")

    
## Add High-level service
class NotificationService:
    """
    High-level logic depends on the Notifier abstraction, not a concrete class.
    That makes the service testable and swappable.
    """
    def __init__(self, notifier: Notifier) -> None:
        self.notifier = notifier

    def notifiy(self, recipient: str, message: str) -> None:
        notification = Notification(recipient=recipient, message=message)
        self.notifier.send(notification)
        