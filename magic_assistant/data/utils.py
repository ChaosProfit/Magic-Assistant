import pyarrow.parquet as pq

def to_json(input_file_path: str, output_file_path: str):
    table = pq.read_table(input_file_path)
    df = table.to_pandas()
    json_data = df.to_json(orient='records', lines=True)
    with open(output_file_path, 'w') as f:
        f.write(json_data)

if __name__ == "__main__":
    import sys
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    to_json(input_file_path, output_file_path)