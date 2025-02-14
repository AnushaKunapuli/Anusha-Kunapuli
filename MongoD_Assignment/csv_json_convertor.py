import csv
import json


def infer_type(value):
    """
    Infer the JSON data type of a value from the CSV file.
    """
    try:
        int(value)
        return "integer"
    except ValueError:
        try:
            float(value)
            return "number"
        except ValueError:
            if value.lower() == "true" or value.lower() == "false":
                return "boolean"
            else:
                return "string"


def csv_to_json_schema(csv_file):
    """
    Convert CSV data to a basic JSON Schema.
    """
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {}

    schema = {
        "title": "CSV to JSON Schema",
        "type": "object",
        "properties": {}
    }

    # Loop through headers to generate properties
    for field in reader.fieldnames:
        # Infer data type from the first non-empty row
        for row in rows:
            if row[field]:
                field_type = infer_type(row[field])
                break
        else:
            field_type = "string"  # Default to string if all rows are empty

        schema["properties"][field] = {
            "type": field_type
        }

    return schema


# Convert the CSV to JSON Schema
csv_file_path = 'delivery_trip_truck_data.csv'  # Path to your CSV file
json_schema = csv_to_json_schema(csv_file_path)

# Save the JSON Schema to a file
with open('json_schema_output.json', 'w') as f:
    json.dump(json_schema, f, indent=4)

print(json.dumps(json_schema, indent=4))  # Print the schema
