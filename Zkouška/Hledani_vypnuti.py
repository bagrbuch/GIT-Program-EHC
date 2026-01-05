import csv
import os

def find_and_export_split(input_file_path, chunk_size=2000, sub_chunk_size=500, expand_size=500, small_chunk_size=100, threshold=0.1, diff_threshold=0.015):
    # Step 1: Check if the file exists
    if not os.path.exists(input_file_path):
        return

    try:
        # Step 2: Read the file in chunks
        with open(input_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            header = next(reader)
            
            rows = []
            for row in reader:
                rows.append(row)
            
            # Step 3: Remove the last row if it contains zero
            if rows[-1][1] == "0":
                rows = rows[:-1]

            # Step 4: Find the maximum value and its index
            max_value = None
            max_index = None
            for i, row in enumerate(rows):
                try:
                    current_value = float(row[1])
                    if max_value is None or current_value > max_value:
                        max_value = current_value
                        max_index = i
                except (ValueError, IndexError):
                    continue
            
            if max_index is None:
                return

            # Step 5: Process chunks after the maximum value
            for i in range(max_index + 1, len(rows), chunk_size):
                chunk = rows[i:i + chunk_size]
                if len(chunk) > chunk_size:
                    chunk = chunk[:-1]

                first_value = float(chunk[0][1])
                last_value = float(chunk[-1][1])

                # Step 6: Check if the difference exceeds the threshold
                difference = abs(last_value - first_value)
                if difference > threshold:
                    # Step 7: Process sub-chunks of 500 rows
                    for j in range(0, len(chunk), sub_chunk_size):
                        sub_chunk = chunk[j:j + sub_chunk_size]
                        if len(sub_chunk) > sub_chunk_size:
                            sub_chunk = sub_chunk[:-1]

                        first_value_sub = float(sub_chunk[0][1])
                        last_value_sub = float(sub_chunk[-1][1])

                        difference_sub = abs(last_value_sub - first_value_sub)

                    # Step 8: Expand the chunk by 500 rows
                    expanded_chunk_start = max(i - expand_size, 0)
                    expanded_chunk = rows[expanded_chunk_start:i + len(chunk)]

                    # Step 9: Process sub-chunks of 100 rows
                    differences = []
                    for j in range(0, len(expanded_chunk), small_chunk_size):
                        small_sub_chunk = expanded_chunk[j:j + small_chunk_size]
                        if len(small_sub_chunk) > small_chunk_size:
                            small_sub_chunk = small_sub_chunk[:-1]

                        first_value_small = float(small_sub_chunk[0][1])
                        last_value_small = float(small_sub_chunk[-1][1])

                        difference_small = abs(last_value_small - first_value_small)

                        differences.append(difference_small)

                    # Step 10: Look for two consecutive differences greater than the threshold
                    for k in range(1, len(differences)):
                        if differences[k-1] > diff_threshold and differences[k] > diff_threshold:
                            row_number = expanded_chunk_start + k * small_chunk_size - 100

                            # Step 11: Split the file into compression and diffusion
                            compression_rows = rows[:row_number]
                            diffusion_rows = rows[row_number:]

                            # Step 12: Save the data into new files
                            with open('compression.csv', mode='w', newline='', encoding='utf-8') as compression_file:
                                writer = csv.writer(compression_file, delimiter=';')
                                writer.writerow(header)
                                writer.writerows(compression_rows)

                            with open('diffusion.csv', mode='w', newline='', encoding='utf-8') as diffusion_file:
                                writer = csv.writer(diffusion_file, delimiter=';')
                                writer.writerow(header)
                                writer.writerows(diffusion_rows)

                            return

            return

    except Exception as e:
        return

# Example usage:
find_and_export_split("ZK_trimmed.csv", chunk_size=2000, sub_chunk_size=500, expand_size=500, small_chunk_size=100, threshold=0.1, diff_threshold=0.015)
