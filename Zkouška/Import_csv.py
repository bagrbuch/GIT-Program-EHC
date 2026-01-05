import os
from datetime import datetime, timedelta
import csv

#-----------------------------------Main program for import and spliting data------------------------------------------------

def find_and_trim_csv(file_path, output_path, chunk_size=2000, sub_chunk_size=500, expand_size=500, small_chunk_size=100, threshold=0.1, diff_threshold=0.015):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    try:
        # Load the entire file and adjust it according to the requirements
        print(f"Importing file {file_path}...")  # Display import message
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            header = next(reader)  # Read the header row

            rows = []
            for row in reader:
                rows.append(row)

        # Step 1: Find the first zero and remove all rows before it
        found_zero = False
        trimmed_rows = []
        for row in rows:
            try:
                value = float(row[1])
                if value == 0 and not found_zero:
                    found_zero = True
                if found_zero:
                    trimmed_rows.append(row)
            except (ValueError, IndexError):
                print(f"Skipping invalid row: {row}")

        # Step 2: Check the first 20 rows to ensure there's only one zero at the beginning
        while True:
            zero_indices = []
            # Check the first 20 rows for zeros
            for i, row in enumerate(trimmed_rows[:20]):  # Only consider the first 20 rows
                try:
                    value = float(row[1])
                    if value == 0:
                        zero_indices.append(i)
                except (ValueError, IndexError):
                    print(f"Skipping invalid row: {row}")

            # If there is not exactly one zero at the beginning in the first 20 rows
            if len(zero_indices) > 1 or (len(zero_indices) == 1 and zero_indices[0] != 0):
                # Last found zero
                last_zero_index = zero_indices[-1] if zero_indices else 0
                # Remove all rows before the last found zero
                trimmed_rows = trimmed_rows[last_zero_index:]
            else:
                break  # If only one zero is at the beginning of the first 20 rows, exit

        # Step 3: Remove the first zero and find the second minimum
        trimmed_rows_without_first_zero = trimmed_rows[1:]  # Remove the first zero
        second_min_index = None
        min_value = float('inf')  # Set to maximum value

        for i, row in enumerate(trimmed_rows_without_first_zero):
            try:
                value = float(row[1])
                if value < min_value:
                    min_value = value
                    second_min_index = i
            except (ValueError, IndexError):
                print(f"Skipping invalid row: {row}")

        # If the second minimum is found, remove all rows after it
        if second_min_index is not None:
            # Include the first zero since we already removed it
            final_trimmed_rows = trimmed_rows[:1] + trimmed_rows_without_first_zero[:second_min_index + 1]
        else:
            final_trimmed_rows = trimmed_rows  # If no second minimum found, keep original state

        # Save the final trimmed file
        if final_trimmed_rows:
            with open(output_path, mode='w', encoding='utf-8', newline='') as output_file:
                writer = csv.writer(output_file, delimiter=';')
                writer.writerow(header)  # Write the header
                writer.writerows(final_trimmed_rows)  # Write the final trimmed rows

            print(f"Final trimmed file saved: {output_path}\n")

            # After successful saving, call the function find_and_export_split
            time_difference = get_relative_time_difference("CA")
            found_row = find_row_by_time_difference("ZK_trimmed.csv", time_difference)
            
            split_file_by_row("ZK_trimmed.csv", found_row)

            #find_and_split(output_path, chunk_size, sub_chunk_size, expand_size, small_chunk_size, threshold, diff_threshold)
        else:
            print("No rows were trimmed.")

    except Exception as e:
        print(f"Error while reading or writing the file: {e}")


#----------------------------------Finding time by data from potenciostat-----------------------------------------

def get_relative_time_difference(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter='\t')
            header = next(reader)
            rows = [row for row in reader]

        if len(rows) < 2:
            print("Not at least two rows.")
            return None

        first_time = float(rows[0][0])
        last_time = float(rows[-1][0])

        time_difference_sec = last_time - first_time+1
        print(f"Time of compression: {time_difference_sec:.0f} (s)\n")
        return time_difference_sec

    except Exception as e:
        print(f"Error of loading data {e}")
        return None

#-----------------------------Finding number of row in data from database----------------------------------------------

def find_row_by_time_difference(input_file_path, target_seconds):

    try:
        with open(input_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            header = next(reader)
            
            rows = [row for row in reader if len(row) > 1]

        first_row = rows[0]
        reference_time_str = first_row[0]
        reference_time = datetime.strptime(reference_time_str, "%d.%m.%Y %H:%M:%S")
        
        target_time = reference_time + timedelta(seconds=target_seconds)
        
        for i, row in enumerate(rows):
            row_time_str = row[0]
            row_time = datetime.strptime(row_time_str, "%d.%m.%Y %H:%M:%S")
            
            if row_time >= target_time:
                i=i+1
                print(f"Founded time: {row_time} represent time: {target_time} found on row {i} .")
                print(f"Founded row: {row}\n")
                return i

        print("There is not time, that will represent time of compression")
        return None

    except Exception as e:
        print(f"Error with import of data: {e}")
        return None

#--------------------------------------Spliting data from databese by row number---------------------------------------------

def split_file_by_row(input_file_path, row_number):
    if not os.path.exists(input_file_path):
        print(f"File {input_file_path} not found.")
        return

    try:
        with open(input_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            header = next(reader)
            rows = [row for row in reader]

        if row_number < 1 or row_number > len(rows):
            print(f"Row number {row_number} is not valid. The file contains {len(rows)} rows.")
            return

        compression_rows = rows[:row_number]
        diffusion_rows = rows[row_number:]

        with open('compression.csv', mode='w', encoding='utf-8', newline='') as compression_file:
            writer = csv.writer(compression_file, delimiter=';')
            writer.writerow(header)
            writer.writerows(compression_rows)

        with open('diffusion.csv', mode='w', encoding='utf-8', newline='') as diffusion_file:
            writer = csv.writer(diffusion_file, delimiter=';')
            writer.writerow(header)
            writer.writerows(diffusion_rows[:-50])

        print(f"Compression started: {compression_rows[0][0]}")
        print(f"Compression ended {compression_rows[-1][0]}")
        print(f"Diffusion ended: {diffusion_rows[-1][0]}")

    except Exception as e:
        print(f"Error while processing the file: {e}")


#----------------------------------------------------Spliting data without data from potenciostat----------------------------------------------------------------------

def find_and_split(input_file_path, chunk_size=2000, sub_chunk_size=500, expand_size=500, small_chunk_size=100, threshold=0.1, diff_threshold=0.015):
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
                            print(f"Compression started: {compression_rows[0][0]}")
                            with open('compression.csv', mode='w', newline='', encoding='utf-8') as compression_file:
                                writer = csv.writer(compression_file, delimiter=';')
                                writer.writerow(header)
                                writer.writerows(compression_rows)

                            print(f"Compression ended {compression_rows[-1][0]}")

                            with open('diffusion.csv', mode='w', newline='', encoding='utf-8') as diffusion_file:
                                writer = csv.writer(diffusion_file, delimiter=';')
                                writer.writerow(header)
                                writer.writerows(diffusion_rows)

                            print(f"Diffusion ended: {diffusion_rows[-1][0]}")

                            return

            return

    except Exception as e:
        return

#------------------------------------------------------------------------------

# find_and_split_by_time("pressure_data.csv", "03.12.2024 12:15:45")
find_and_trim_csv("ZK.csv", "ZK_trimmed.csv", chunk_size=2000, sub_chunk_size=500, expand_size=500, small_chunk_size=100, threshold=0.1, diff_threshold=0.015)
