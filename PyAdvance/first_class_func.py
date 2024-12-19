def greet(name):
    return f"Hello {name}!"

# Assign function to a variable
greet_function = greet
print(greet_function("AJ Borbe"))

# passing function as an argument
def execute_function(func, value):
    return func(value)

print(execute_function(greet, "Aj Borbz!"))

def multiplier(factor):
    def multiply_by_factor(number):
        return number * factor
    return multiply_by_factor

double = multiplier(2)
print(double(5))

# Higher Order function
numbers = [1,2,3,4,5]
squared_numbers = list(map(lambda x: x**2, numbers))
print(squared_numbers)

# custom higher-order functions
def apply_operation(operation, values):
    return [operation(value) for value in values]

# Using with lambda functions
cubed_number = apply_operation(lambda x: x**3, numbers)
print(cubed_number)

