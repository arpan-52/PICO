import numpy as np
import h5py
import os


def stitch_files(file_a, file_b, output_file, block_size=65536000):
    # Open files for reading in binary mode
    with open(file_a, 'rb') as fa, open(file_b, 'rb') as fb, open(output_file, 'wb') as fo:
        block_num = 0  # Initialize block number
        
        while True:
            # Calculate the byte positions for the current block
            start_pos = block_num * block_size
            end_pos = start_pos + block_size
            
            # Read the block from file_a
            fa.seek(start_pos)
            data_a = fa.read(block_size)
            
            # Read the block from file_b
            fb.seek(start_pos)
            data_b = fb.read(block_size)
            
            # Write the data to the output file
            if data_a:
                fo.write(data_a)
            if data_b:
                fo.write(data_b)
            
            # If both data_a and data_b are empty, break the loop
            if not data_a and not data_b:
                break
            
            # Increment the block number
            block_num += 1


########################>>>>>>>>>>>>>########################

def extract_binary_data(file_path, t1, t2, output_file_path):
    """
    Extracts data from a binary file between the given timestamps t1 and t2,
    and writes the extracted data to a new binary file.

    Parameters:
    - file_path (str): Path to the input binary file.
    - t1 (float): Starting time in milliseconds to extract data.
    - t2 (float): Ending time in milliseconds to extract data.
    - output_file_path (str): Path to the output binary file.
    """
    # File parameters
    num_baselines = 10
    num_polarization_channels = 2
    num_components = 2  # Real and Imaginary
    num_channels = 4096

    # Each timestamp block size in half-floats
    half_floats_per_timestamp = num_baselines * num_polarization_channels * num_components * num_channels
    time_interval_ms = 1.3  # Time interval between timestamps in milliseconds

    # Define the data type for the half-float
    half_float_dtype = np.float16
    
    # Calculate the number of timestamps to skip for t1 and read up to t2
    skip_timestamps = int(t1 / time_interval_ms)
    num_timestamps_to_read = int((t2 - t1) / time_interval_ms)
    
    # Calculate byte offset for t1
    offset = skip_timestamps * half_floats_per_timestamp * 2  # each half-float is 2 bytes
    
    with open(file_path, 'rb') as file:
        # Seek to the starting point of t1
        file.seek(offset)
        
        # Read the required data between t1 and t2
        data = np.fromfile(file, dtype=half_float_dtype, count=num_timestamps_to_read * half_floats_per_timestamp)
        
        # Write the selected data to the output binary file
        with open(output_file_path, 'wb') as output_file:
            data.tofile(output_file)

# Example usage:
# extract_binary_data('your_file.bin', 100, 200, 'selected_data.bin')




def read_and_store_visibilities(file_path, uvw_file_path, output_hdf5_path, skip_baselines=None):
    # Define constants
    num_bytes_per_complex = 4  # 16 bits real + 16 bits imaginary = 4 bytes
    num_channels = 4096
    num_baselines = 10
    num_polarizations = 2
    interval_data_size = num_baselines * num_polarizations * num_channels * num_bytes_per_complex

    # Calculate the number of valid baselines
    valid_baselines = num_baselines - len(skip_baselines) if skip_baselines else num_baselines

    # Calculate the number of time intervals in the visibility data file
    total_file_size = os.path.getsize(file_path)
    num_intervals = total_file_size // interval_data_size

    # Read UVW coordinates from the file
    uvw_data = np.loadtxt(uvw_file_path, delimiter=',')
    uvw_num_rows = uvw_data.shape[0]

    # Check if the length of UVW columns matches the expected size
    expected_size = valid_baselines * num_intervals
    if uvw_num_rows != expected_size:
        raise ValueError(f"UVW data size {uvw_num_rows} does not match the expected size {expected_size}.")

    # Open the HDF5 file to store the data
    with h5py.File(output_hdf5_path, 'w') as hdf5_file:
        # Create a dataset for the visibility data including baseline index, UVW, and channel data
        dtype = np.dtype([('baseline_index', 'i4'),
                          ('u', 'f8'), ('v', 'f8'), ('w', 'f8'),
                          ('visibility_data', 'c8', (num_channels,))])
        vis_dataset = hdf5_file.create_dataset("visibility_data", (expected_size,), dtype=dtype)

        # Open the visibility file in binary mode
        with open(file_path, "rb") as file:
            data_index = 0  # Index to track position in the vis_dataset
            while True:
                # Read a block of data corresponding to one 1.3 ms interval
                data = file.read(interval_data_size)

                if not data:
                    break  # End of file

                # Process each baseline in the interval data
                for baseline in range(1, num_baselines + 1):
                    if skip_baselines and baseline in skip_baselines:
                        # Skip this baseline if it's in the skip list
                        continue

                    # Initialize arrays to hold the summed real and imaginary parts for this baseline
                    summed_real = np.zeros(num_channels)
                    summed_imaginary = np.zeros(num_channels)

                    for polarization in range(1, num_polarizations + 1):
                        # Calculate the start and end positions for the current block
                        start_pos = (baseline - 1) * num_polarizations * num_channels * num_bytes_per_complex + \
                                    (polarization - 1) * num_channels * num_bytes_per_complex
                        end_pos = start_pos + num_channels * num_bytes_per_complex

                        # Extract the data for the current baseline and polarization
                        block_data = data[start_pos:end_pos]

                        # Convert the block data to a NumPy array of half-precision floats
                        block_array = np.frombuffer(block_data, dtype=np.float16).reshape((num_channels, 2))

                        # Split the block array into real and imaginary parts
                        real_part = block_array[:, 0]
                        imaginary_part = block_array[:, 1]

                        # Sum across the polarization channels
                        summed_real += real_part
                        summed_imaginary += imaginary_part

                    # Pack real and imaginary parts as a complex number
                    complex_visibilities = summed_real + 1j * summed_imaginary

                    # Get the corresponding UVW coordinates for this baseline
                    u, v, w = uvw_data[data_index]

                    # Store the baseline index, UVW, and visibility data into the HDF5 dataset
                    vis_dataset[data_index] = (baseline, u, v, w, complex_visibilities)
                    data_index += 1

# Example usage
file_path = '1.3s.bin'
uvw_file_path = 'uvw_coordinates.txt'
output_hdf5_path = 'output_data.h5'
skip_baselines = [1, 5, 8, 10]  # Example: skip baselines 1, 5, 8, 10
read_and_store_visibilities(file_path, uvw_file_path, output_hdf5_path, skip_baselines)
