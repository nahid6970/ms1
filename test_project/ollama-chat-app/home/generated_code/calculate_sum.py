# filename: calculate_sum.py

def calculate_sum(numbers):
  """Calculates the sum of a list of numbers.

  Args:
    numbers: A list of numbers (integers or floats).

  Returns:
    The sum of the numbers in the list.  Returns 0 if the list is empty.
  """
  if not numbers:
    return 0
  total = 0
  for number in numbers:
    total += number
  return total

if __name__ == "__main__":
  # Example usage
  my_list = [1, 2, 3, 4, 5]
  sum_result = calculate_sum(my_list)
  print(f"The sum of the list is: {sum_result}")

  empty_list = []
  empty_sum = calculate_sum(empty_list)
  print(f"The sum of the empty list is: {empty_sum}")