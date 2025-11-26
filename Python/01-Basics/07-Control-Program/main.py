# Control Program is a simple program to demonstrate control flow in Python.
# With control flow, you can dictate the order in which statements are executed based on certain conditions.

# If Statement
# The if statement is used to test a specific condition.
# If the condition evaluates to True, the block of code inside the if statement is executed.

number = int(input("Enter a number: "))

if number > 0: 
    print("The number is positive.")

if number < 0:
    print("The number is negative.")

if number == 0:
    print("The number is zero.")

# If-Else Statement
# The if-else statement provides an alternative block of code to execute when the condition is False
value = int(input("Enter another number: "))

if value > 60:
    print("You passed the exam.")

else:
    print("You failed the exam.")

# If-Elif-Else Statement
# The if-elif-else statement allows you to check multiple conditions in sequence.

score = int(input("Enter your score: "))

if score >= 85:
    print("Grade: A")

elif score >= 70:
    print("Grade: B")

elif score >= 50:
    print("Grade: C")

elif score >= 40:
    print("Grade: D")

else:
    print("Grade: E")

# Condition with Logical Operators
# You can combine multiple conditions using logical operators: and, or, not.
age = int(input("Enter your age: "))
license = input("Do you have a driving license? (yes/no): ")

if age >= 18 and license.lower() == 'yes':
    print("You are eligible to drive.")
else:
    print("You are not eligible to drive.")

# Nested If Statement
# You can also nest if statements within other if statements.
username = input("Enter your username: ")
password = input("Enter your password: ")

if username == "admin":
    if password == "admin":
        print("Login successful.")
        print("Welcome, admin!")
    else:
        print("Incorrect password.")
else:
    print("Invalid username.")

# Match Case Statement
# The match-case statement is used for pattern matching, similar to switch-case in other languages.

day = input("Enter a day of the week: ").lower()

match day:
    case "monday":
        print("It's the start of the week!")
    case "wednesday":
        print("It's midweek!")
    case "friday":
        print("It's the end of the week!")
    case _:
        print("It's just another day.")

# Conditional Expressions (Ternary Operator)
# A conditional expression allows you to evaluate something based on a condition in a single line.

temperature = int(input("Enter the temperature in Celsius: "))
status = "Hot" if temperature > 30 else "Cold"
print(status)