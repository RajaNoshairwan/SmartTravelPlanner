import json

# Test data
test_data = {
    "test": "data",
    "number": 42
}

# Try to write to a file
try:
    with open('test.json', 'w') as f:
        json.dump(test_data, f)
    print("Successfully wrote to test.json")
except Exception as e:
    print(f"Error writing to file: {e}")

# Try to write to the notebook file
try:
    with open('travel_planner.ipynb', 'w') as f:
        json.dump(test_data, f)
    print("Successfully wrote to travel_planner.ipynb")
except Exception as e:
    print(f"Error writing to notebook: {e}") 