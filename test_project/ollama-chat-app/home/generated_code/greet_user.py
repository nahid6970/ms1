# filename: greet_user.py

def greet(name):
  """Greets the user by name.

  Args:
    name: The user's name (string).

  Returns:
    A greeting string.
  """
  return f"Hello, {name}!"

if __name__ == "__main__":
  user_name = input("Enter your name: ")
  greeting_message = greet(user_name)
  print(greeting_message)