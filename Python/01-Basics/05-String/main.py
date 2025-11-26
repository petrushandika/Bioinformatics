# What is a string in Python?
# A string is a sequence of characters enclosed in quotes.
# Strings can be defined using single quotes (' '), double quotes (" "), or triple quotes (''' ''' or """ """).
# Strings are immutable, meaning they cannot be changed after they are created.
# You can perform various operations on strings, such as concatenation, slicing, and formatting.

# String Examples
name = "Petrus"
age = 23

message = "Hello, my name is " + name + " and I am " + str(age) + " years old."
print(message)

# Length of a string
length = len(name)
print(length)

# Accessing characters in a string (by index)
first = name[0]
print(first)

last = name[-1]
print(last)

# Slicing a string
language = "Python"
print(language[0:3])  # Output: Pyt
print(language[3:])   # Output: hon
print(language[:]) # Output: Python

# String methods
# Uppercase for change to uppercase
print(language.upper())  # Output: PYTHON

# Lowercase for change to lowercase
print(language.lower())  # Output: python

# Capitalize for capitalize the first character
print(language.capitalize())  # Output: Python

# Strip to remove whitespace from the beginning and end
whitespace = "   Hello, World!   "
print(whitespace.strip())  # Output: Hello, World!

# Replace to replace a substring with another substring
text = "I love Python"
print(text.replace("Python", "Java")) # Output: I love Java

# Count to count occurrences of a substring
print(text.count("o"))  # Output: 2

# Find to find the index of a substring
print(text.find("Python"))  # Output: 7