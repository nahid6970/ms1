# filename: reverse_string.py

def reverse_string(input_string):
  """Reverses a given string.

  Args:
    input_string: The string to be reversed.

  Returns:
    The reversed string.
  """
  return input_string[::-1]

if __name__ == "__main__":
  original_string = input("Enter a string: ")
  reversed_string = reverse_string(original_string)
  print(f"The reversed string is: {reversed_string}")