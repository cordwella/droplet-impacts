from file_list import file_list


csv_filename = "C:/Users/acor102/Documents/ferrofluids/alex_summary_record_values.csv" # noqa


with open(csv_filename, 'w') as f:
    for file in file_list:
        if 'alex' in file:
            if 'Dec' in file:
                continue
            f.write(file)
            f.write(",\n")
