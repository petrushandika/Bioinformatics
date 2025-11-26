# Operator Arithmetic for using basic arithmetic operations
# Operators are special symbols or keywords that perform specific operations on one or more operands (values or variables).
# In Python, there are several types of operators, including arithmetic, comparison, logical, assignment, and more.

# Operator basic arithmetic operators in Python:
# Addition (+): Adds two operands.
# Subtraction (-): Subtracts the second operand from the first.
# Multiplication (*): Multiplies two operands.
# Division (/): Divides the first operand by the second (result is a float).
# Floor Division (//): Divides the first operand by the second and returns the largest integer less than or equal to the result.
# Modulus (%): Returns the remainder of the division of the first operand by the second.

a = 10
b = 3

addition = a + b
subtraction = a - b
multiplication = a * b
division = a / b
floor_division = a // b
modulus = a % b

print(addition)
print(subtraction)
print(multiplication)
print(division)
print(floor_division)
print(modulus)

# Operator Assignment Operators
# Assignment operators are used to assign values to variables. They can also perform operations and assign the result to the variable in a single step.

x = 5
print("Initial value of x:", x)

x += 3  # Equivalent to x = x + 3
print("After x += 3:", x)

x -= 2  # Equivalent to x = x - 2
print("After x -= 2:", x)

x *= 4  # Equivalent to x = x * 4
print("After x *= 4:", x)

x /= 2  # Equivalent to x = x / 2
print("After x /= 2:", x)

x %= 3  # Equivalent to x = x % 3
print("After x %= 3:", x)

# Operator Comparison Operators
# Comparison operators are used to compare two values and return a Boolean result (True or False).
y = 8
z = 12

print("Is y equal to z?", y == z)
print("Is y not equal to z?", y != z)
print("Is y greater than z?", y > z)
print("Is y less than z?", y < z)
print("Is y greater than or equal to z?", y >= z)
print("Is y less than or equal to z?", y <= z)

# Operator Logical Operators
# Logical operators are used to combine multiple Boolean expressions and return a Boolean result.
p = True
q = False

print("p and q:", p and q)  # Logical AND
print("p or q:", p or q)    # Logical OR
print("not p:", not p)       # Logical NOT
print("not q:", not q)       # Logical NOT

# Operator String

# String operators are used to perform operations on strings.
first = "Petrus"
last = "Handika"
full_name = first + " " + last  # Concatenation
print("Full Name:", full_name)

greeting = "Hello, " * 3  # Repetition
print("Greeting:", greeting)

# Operator Membership Operators
# Membership operators are used to test whether a value is present in a sequence (like a string, list, or tuple).
text = "Hello, welcome to Python programming." 
print("Is 'Python' in text?", 'Python' in text)
print("Is 'Java' not in text?", 'Java' not in text)