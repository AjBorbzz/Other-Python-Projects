### Foundational Design Principles
The principles guide fundamental software structure and organization:
* **Modularity:** Breaking down a complex system into smaller, independent, and interchangeable components or modules, each responsible for a specific functionality. This enhances reusability and maintainability.
* **Abstraction:** Simplifying complex systems by modeling classes appropriate to the problem and hiding unnecessary details behind clean interfaces. This allows developers to work at the most relevant level of detail.
* **Encapsulation:** Bundling data with the methods that operate on that data, restricting direct access to the internal state. This protects data integrity and reduces unexpected side effects.
* **Separation of Concerns (SoC):** Organizing a system into distinct sections, each addressing a separate concern. This is similar to the Single Responsibility Principle but applies at a broader, system-wide architectural level.
### High Cohesion & Low Coupling:
* **Cohesion** refers to how closely related the elements within a module are in function. High cohesion is desirable.
* **Coupling** refers to the degree of interdependence between modules. Low coupling is desirable as it reduces the risk of changes in one part of the system affecting others. 
### Practical Development Principles
These principles focus on efficiency, simplicity, and maintainability in day-to-day coding: 
* **DRY (Don't Repeat Yourself):** Every piece of knowledge (logic or data) should have a single, unambiguous, authoritative representation within a system. Duplication leads to maintenance headaches.
* **KISS (Keep It Simple, Stupid):** Strive for simplicity in your solutions and avoid unnecessary complexity or over-engineering. Simple designs are easier to understand, test, and maintain.
* **YAGNI (You Aren't Gonna Need It):** Only implement features or functionality when they are actually needed, not based on speculative future needs. This prevents wasted time and unnecessary complexity.
* **Law of Demeter (LoD):** A principle that suggests a module should only communicate with its immediate "friends" or neighbors, avoiding long chains of method calls (e.g., a.getB().getC().doSomething()). This reduces coupling and improves maintainability.
* **Principle of Least Astonishment (POLA):** The behavior of a component should be predictable and intuitive to the user or developer, reducing confusion and minimizing mistakes. 