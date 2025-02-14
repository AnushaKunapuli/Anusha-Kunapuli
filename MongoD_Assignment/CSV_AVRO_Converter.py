import csv
import json


def generate_avro_schema(csv_file, record_name="Record"):
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Get the column names from the first row

    # Guess data types or set all as strings (you can modify to detect types if needed)
    fields = [{"name": col, "type": "string"} for col in headers]

    avro_schema = {
        "type": "record",
        "name": record_name,
        "fields": fields
    }

    return json.dumps(avro_schema, indent=4)


# Specify your CSV file path here
csv_file_path = 'delivery_trip_truck_data.csv'
avro_schema = generate_avro_schema(csv_file_path)

# Save schema to file or print it
print(avro_schema)

# Optionally write the schema to a file
with open('output_avro_schema.avsc', 'w') as f:
    f.write(avro_schema)
