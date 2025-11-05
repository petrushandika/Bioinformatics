# Variable is "container" or "box" to store data values. In Python, variables are created when you assign a value to it.

# Analogy: Think of a variable as a labeled box where you can store items (data values). You can put items into the box, take them out, or replace them with new items.

# Example of creating variables and assigning values
name = "Petrus"; # String variable
age = 23;        # Integer variable
height = 171.5;   # Float variable
true = True; # Boolean variable

# Rules for naming variables:
# 1. Variable names must start with a letter (a-z, A-Z) or an underscore (_).
# 2. The rest of the name can contain letters, digits (0-9), or underscores.
# 3. Variable names are case-sensitive (e.g., age and Age are different variables
# 4. Variable names cannot be the same as Python reserved keywords (e.g., if, else, while, etc.)
# 5. Variable names should not contain spaces. Use underscores (_) to separate words (e.g., my_variable).
# 6. Variable names should be descriptive to make the code more readable (e.g., use age instead of a).

# Printing variable values
print("Name:", name);
print("Age:", age);
print("Height:", height);
print("Is True:", true);

# Updating variable values
age = 24;  # Update age to 24
print("Updated Age:", age);

# Demonstrating case sensitivity
Age = 30;  # This is a different variable from age
print("Age variable:", age);
print("Age with capital A variable:", Age);


# Demonstrating invalid variable names (uncommenting these lines will cause errors)
# 1. 2name = "John";  # Invalid: starts with a digit
# 2. my-name = "Doe"; # Invalid: contains hyphen
# 3. if = 10;         # Invalid: 'if' is a reserved keyword
# 4. my variable = 5; # Invalid: contains space
# 5. print("Value:", my-variable); # Invalid: contains hyphen

# Best practices for variable naming:
# 1. Use meaningful names that describe the purpose of the variable (e.g., age instead of a).
# 2. Use lowercase letters and underscores to separate words (e.g., my_variable).
# 3. Avoid using single-character variable names except for counters or iterators (e.g., i, j).
# 4. Keep variable names concise but informative (e.g., use total_price instead of totalamountofprice).
# 5. Be consistent with naming conventions throughout your code (e.g., always use snake_case for variable names).
# 6. Avoid using reserved keywords as variable names (e.g., if, else, while, etc.).

# By following these rules and best practices, you can create clear and effective variable names in your Python programs.