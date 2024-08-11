# def stitch_files(file_a, file_b, output_file, block_size=65536000):
#     # Open files for reading in binary mode
#     with open(file_a, 'rb') as fa, open(file_b, 'rb') as fb, open(output_file, 'wb') as fo:
#         block_num = 0  # Initialize block number
        
#         while True:
#             # Calculate the byte positions for the current block
#             start_pos = block_num * block_size
#             end_pos = start_pos + block_size
            
#             # Read the block from file_a
#             fa.seek(start_pos)
#             data_a = fa.read(block_size)
            
#             # Read the block from file_b
#             fb.seek(start_pos)
#             data_b = fb.read(block_size)
            
#             # Write the data to the output file
#             if data_a:
#                 fo.write(data_a)
#             if data_b:
#                 fo.write(data_b)
            
#             # If both data_a and data_b are empty, break the loop
#             if not data_a and not data_b:
#                 break
            
#             # Increment the block number
#             block_num += 1


# stitch_files('3c286_hfvisi_c13c14e2e3_phased_node1.raw','3c286_hfvisi_c13c14e2e3_phased_node2.raw','3c286.bin',block_size=65536000)

# import numpy as np

# def extract_binary_data(file_path, t1, t2, output_file_path):
#     """
#     Extracts data from a binary file between the given timestamps t1 and t2,
#     and writes the extracted data to a new binary file.

#     Parameters:
#     - file_path (str): Path to the input binary file.
#     - t1 (float): Starting time in milliseconds to extract data.
#     - t2 (float): Ending time in milliseconds to extract data.
#     - output_file_path (str): Path to the output binary file.
#     """
# #     # File parameters
# #     num_baselines = 10
# #     num_polarization_channels = 2
# #     num_components = 2  # Real and Imaginary
# #     num_channels = 4096

# #     # Each timestamp block size in half-floats
# #     half_floats_per_timestamp = num_baselines * num_polarization_channels * num_components * num_channels
# #     time_interval_ms = 1.3  # Time interval between timestamps in milliseconds

# #     # Define the data type for the half-float
# #     half_float_dtype = np.float16
    
# #     # Calculate the number of timestamps to skip for t1 and read up to t2
# #     skip_timestamps = int(t1 / time_interval_ms)
# #     num_timestamps_to_read = int((t2 - t1) / time_interval_ms)
    
# #     # Calculate byte offset for t1
# #     offset = skip_timestamps * half_floats_per_timestamp * 2  # each half-float is 2 bytes
    
# #     with open(file_path, 'rb') as file:
# #         # Seek to the starting point of t1
# #         file.seek(offset)
        
# #         # Read the required data between t1 and t2
# #         data = np.fromfile(file, dtype=half_float_dtype, count=num_timestamps_to_read * half_floats_per_timestamp)
        
# #         # Write the selected data to the output binary file
# #         with open(output_file_path, 'wb') as output_file:
# #             data.tofile(output_file)

# # # Example usage:
# # extract_binary_data('3c286.bin', 100, 1400, '1.3s.bin')
import numpy as np

# Constants
SPEED_OF_LIGHT = 299792458.0  # speed of light in meters per second

def degrees_to_radians(degrees):
    return degrees * np.pi / 180.0

def calculate_julian_date(year, month, day):
    if month <= 2:
        year -= 1
        month += 12
    A = np.floor(year / 100)
    B = 2 - A + np.floor(A / 4)
    JD = np.floor(365.25 * (year + 4716)) + np.floor(30.6001 * (month + 1)) + day + B - 1524.5
    return JD

def calculate_gst_0h_ut(year, month, day):
    JD = calculate_julian_date(year, month, day)
    T = (JD - 2451545.0) / 36525.0
    GST_deg = 100.46061837 + 36000.770053608 * T + 0.000387933 * T**2 - T**3 / 38710000.0
    GST_deg = np.mod(GST_deg, 360.0)
    if GST_deg < 0:
        GST_deg += 360.0
    return GST_deg

def calculate_lst(gst_at_0h_ut, ut_hours, longitude):
    gst = gst_at_0h_ut + ut_hours * (360.985647 / 24.0)
    lst = gst + longitude
    if lst < 0:
        lst += 360.0
    if lst >= 360.0:
        lst -= 360.0
    return lst

def calculate_uvw(antenna1, antenna2, ha_rad, dec_rad):
    baseline = np.subtract(antenna2, antenna1)
    sinHA = np.sin(ha_rad)
    cosHA = np.cos(ha_rad)
    sinDec = np.sin(dec_rad)
    cosDec = np.cos(dec_rad)
    u = -sinHA * baseline[0] + cosHA * baseline[1]
    v = -sinDec * cosHA * baseline[0] - sinDec * sinHA * baseline[1] + cosDec * baseline[2]
    w = cosDec * cosHA * baseline[0] + cosDec * sinHA * baseline[1] + sinDec * baseline[2]
    return np.array([u, v, w])

def calculate_and_save_uvw_with_wavelength(antennas, ra, dec, freq_low, freq_high, num_channels, start_ist, date_obs, duration_sec, time_resolution_sec):
    with open("uvw_wavelength_coordinates.txt", "w") as output_file:
        freq_step = (freq_high - freq_low) / (num_channels - 1)
        ra_rad = degrees_to_radians(ra)
        dec_rad = degrees_to_radians(dec)

        gst_at_0h_ut = calculate_gst_0h_ut(date_obs[0], date_obs[1], date_obs[2])
        print(gst_at_0h_ut)

        start_ut = start_ist - 5.5  # IST is UTC+5:30
        if start_ut < 0:
            start_ut += 24.0

        num_steps = int(duration_sec / time_resolution_sec)
        print(num_steps)

        for step in range(num_steps):
            current_time_sec = step * time_resolution_sec
            ut_hours = start_ut + current_time_sec / 3600.0
            lst_deg = calculate_lst(gst_at_0h_ut, ut_hours, 74.0)
            ha_deg = lst_deg - ra
            ha_rad = degrees_to_radians(ha_deg)
            print(lst_deg)
            print(ha_deg)

            for ch in range(num_channels):
                freq = freq_low + ch * freq_step
                wavelength = SPEED_OF_LIGHT / freq

                for i in range(len(antennas)):
                    for j in range(i + 1, len(antennas)):
                        uvw = calculate_uvw(antennas[i], antennas[j], ha_rad, dec_rad)
                        uvw_scaled = uvw / wavelength
                        output_file.write(f"{uvw_scaled[0]} {uvw_scaled[1]} {uvw_scaled[2]}\n")

    print("UVW coordinates with wavelengths have been saved to uvw_wavelength_coordinates.txt.")


# antennas = [
#     [1763985.93, 5770403.15, 2063520.86],
#     [1763992.23, 5770041.72, 2063500.55],
#     [1763978.98, 5769715.27, 2063540.90],
#     [1763927.78, 5769342.56, 2063674.49],
#     [1763927.97, 5769149.31, 2063664.33],
#     [1764058.10, 5769783.08, 2063294.31],
#     [1764050.23, 5769683.84, 2063320.32],
#     [1764109.78, 5769995.95, 2063140.57],
#     [1764027.59, 5769757.22, 2063389.25],
#     [1764170.33, 5769550.40, 2062953.41],
#     [1764081.47, 5769112.02, 2063219.34],
#     [1764188.26, 5769890.12, 2062905.36],
#     [1764347.65, 5769075.77, 2062422.98],
#     [1764186.35, 5769241.58, 2062912.27],
#     [1763630.80, 5772529.82, 2064494.57],
#     [1763271.42, 5774291.31, 2065473.36],
#     [1762941.39, 5777495.84, 2066444.19],
#     [1762801.02, 5779915.17, 2066884.10],
#     [1762406.93, 5781788.59, 2068084.03],
#     [1764921.97, 5770349.23, 2060734.97],
#     [1765431.89, 5769348.05, 2059261.74],
#     [1766163.61, 5770048.37, 2057135.94],
#     [1767051.93, 5770663.06, 2054561.40],
#     [1768571.81, 5769346.18, 2050158.42],
#     [1763777.63, 5768123.32, 2064132.22],
#     [1763496.64, 5766615.83, 2064960.29],
#     [1762987.52, 5764515.26, 2066440.01],
#     [1762245.07, 5762676.21, 2068608.43],
#     [1761273.29, 5761612.01, 2071358.04],
#     [1760877.46, 5758469.50, 2072457.16],
#     [1760876.87, 5758469.67, 2072457.16],
#     [1760876.87, 5758469.67, 2072457.16]
# ]



antennas = [
    [1764188.26, 5769890.12, 2062905.36],
    [1764347.65, 5769075.77, 2062422.98],
    [1764186.35, 5769241.58, 2062912.27],
    [1763630.80, 5772529.82, 2064494.57]
]



ra =  202.78453 # Convert RA from hms to decimal degrees
dec = 30.50916  # Convert DEC from dms to decimal degrees
freq_low = 550e6  # 550 MHz
freq_high = 750e6  # 750 MHz
num_channels = 4096
start_ist = 16.7725  # 16:46:21.00 IST converted to decimal hours
date_obs = [2024,8, 8]  # 8th August 2024
duration_sec = 1.3  # in s
time_resolution_sec = 1.3e-3  # 1.3 ms


def calculate_and_save_uvw(antennas, ra, dec, start_ist, date_obs, duration_sec, time_resolution_sec):
    with open("uvw_coordinates.txt", "w") as output_file:
        ra_rad = degrees_to_radians(ra)
        dec_rad = degrees_to_radians(dec)

        gst_at_0h_ut = calculate_gst_0h_ut(date_obs[0], date_obs[1], date_obs[2])

        start_ut = start_ist - 5.5  # IST is UTC+5:30
        if start_ut < 0:
            start_ut += 24.0

        num_steps = int(duration_sec / time_resolution_sec)

        for step in range(num_steps):
            current_time_sec = step * time_resolution_sec
            ut_hours = start_ut + current_time_sec / 3600.0
            lst_deg = calculate_lst(gst_at_0h_ut, ut_hours, 74.0)
            ha_deg = lst_deg - ra
            ha_rad = degrees_to_radians(ha_deg)

            for i in range(len(antennas)):
                for j in range(i + 1, len(antennas)):
                    uvw = calculate_uvw(antennas[i], antennas[j], ha_rad, dec_rad)
                    output_file.write(f"{uvw[0]},{uvw[1]},{uvw[2]}\n")

    print("UVW coordinates have been saved to uvw_coordinates.txt.")


calculate_and_save_uvw(antennas, ra, dec, start_ist, date_obs, duration_sec, time_resolution_sec)



# # import numpy as np

# # def read_and_sum_visibilities(file_path, skip_baselines=None):
# #     # Define constants
# #     num_bytes_per_complex = 4  # 16 bits real + 16 bits imaginary = 4 bytes
# #     num_channels = 4096
# #     num_baselines = 10
# #     num_polarizations = 2
# #     interval_data_size = num_baselines * num_polarizations * num_channels * num_bytes_per_complex

# #     # Initialize a list to store visibility data over time
# #     time_series_visibilities = []

# #     # Open the file in binary mode
# #     with open(file_path, "rb") as file:
# #         while True:
# #             # Read a block of data corresponding to one 1.3 ms interval
# #             data = file.read(interval_data_size)
            
# #             if not data:
# #                 break  # End of file
            
# #             # Initialize a dictionary to store summed visibilities for this time interval
# #             interval_visibilities = {}
            
# #             # Process each baseline in the interval data
# #             for baseline in range(1, num_baselines + 1):
# #                 if skip_baselines and baseline in skip_baselines:
# #                     # Skip this baseline if it's in the skip list
# #                     continue
                
# #                 # Initialize arrays to hold the summed real and imaginary parts for this baseline
# #                 summed_real = np.zeros(num_channels)
# #                 summed_imaginary = np.zeros(num_channels)
                
# #                 for polarization in range(1, num_polarizations + 1):
# #                     # Calculate the start and end positions for the current block
# #                     start_pos = (baseline - 1) * num_polarizations * num_channels * num_bytes_per_complex + \
# #                                 (polarization - 1) * num_channels * num_bytes_per_complex
# #                     end_pos = start_pos + num_channels * num_bytes_per_complex
                    
# #                     # Extract the data for the current baseline and polarization
# #                     block_data = data[start_pos:end_pos]
                    
# #                     # Convert the block data to a NumPy array of half-precision floats
# #                     block_array = np.frombuffer(block_data, dtype=np.float16).reshape((num_channels, 2))
                    
# #                     # Split the block array into real and imaginary parts
# #                     real_part = block_array[:, 0]
# #                     imaginary_part = block_array[:, 1]
                    
# #                     # Sum across the polarization channels
# #                     summed_real += real_part
# #                     summed_imaginary += imaginary_part
                
# #                 # Store the summed visibility data for this baseline and interval
# #                 interval_visibilities[baseline] = {
# #                     "real": summed_real,
# #                     "imaginary": summed_imaginary
# #                 }
            
# #             # Append the interval's visibility data to the time series list
# #             time_series_visibilities.append(interval_visibilities)
    
# #     return time_series_visibilities

# # # Example usage
# # file_path = '1.3s.bin'
# # skip_baselines = [1, 5, 8, 10]  # Example: skip baselines 1, 5, 8, 10
# # time_series_visibilities = read_and_sum_visibilities(file_path, skip_baselines)

# # # Optionally, print or process the time_series_visibilities
# # for idx, interval_vis in enumerate(time_series_visibilities):
# #     print(f"Time interval {idx+1}:")
# #     for baseline, vis_data in interval_vis.items():
# #         print(f"  Baseline {baseline} - Real part sum: {vis_data['real']}, Imaginary part sum: {vis_data['imaginary']}")



# import numpy as np
# import h5py
# import os

# def read_and_store_visibilities(file_path, uvw_file_path, output_hdf5_path, skip_baselines=None):
#     # Define constants
#     num_bytes_per_complex = 4  # 16 bits real + 16 bits imaginary = 4 bytes
#     num_channels = 4096
#     num_baselines = 10
#     num_polarizations = 2
#     interval_data_size = num_baselines * num_polarizations * num_channels * num_bytes_per_complex

#     # Calculate the number of valid baselines
#     valid_baselines = num_baselines - len(skip_baselines) if skip_baselines else num_baselines

#     # Calculate the number of time intervals in the visibility data file
#     total_file_size = os.path.getsize(file_path)
#     num_intervals = total_file_size // interval_data_size

#     # Read UVW coordinates from the file
#     uvw_data = np.loadtxt(uvw_file_path, delimiter=',')
#     uvw_num_rows = uvw_data.shape[0]

#     # Check if the length of UVW columns matches the expected size
#     expected_size = valid_baselines * num_intervals
#     if uvw_num_rows != expected_size:
#         raise ValueError(f"UVW data size {uvw_num_rows} does not match the expected size {expected_size}.")

#     # Open the HDF5 file to store the data
#     with h5py.File(output_hdf5_path, 'w') as hdf5_file:
#         # Create a dataset for the visibility data including baseline index, UVW, and channel data
#         dtype = np.dtype([('baseline_index', 'i4'),
#                           ('u', 'f8'), ('v', 'f8'), ('w', 'f8'),
#                           ('visibility_data', 'c8', (num_channels,))])
#         vis_dataset = hdf5_file.create_dataset("visibility_data", (expected_size,), dtype=dtype)

#         # Open the visibility file in binary mode
#         with open(file_path, "rb") as file:
#             data_index = 0  # Index to track position in the vis_dataset
#             while True:
#                 # Read a block of data corresponding to one 1.3 ms interval
#                 data = file.read(interval_data_size)

#                 if not data:
#                     break  # End of file

#                 # Process each baseline in the interval data
#                 for baseline in range(1, num_baselines + 1):
#                     if skip_baselines and baseline in skip_baselines:
#                         # Skip this baseline if it's in the skip list
#                         continue

#                     # Initialize arrays to hold the summed real and imaginary parts for this baseline
#                     summed_real = np.zeros(num_channels)
#                     summed_imaginary = np.zeros(num_channels)

#                     for polarization in range(1, num_polarizations + 1):
#                         # Calculate the start and end positions for the current block
#                         start_pos = (baseline - 1) * num_polarizations * num_channels * num_bytes_per_complex + \
#                                     (polarization - 1) * num_channels * num_bytes_per_complex
#                         end_pos = start_pos + num_channels * num_bytes_per_complex

#                         # Extract the data for the current baseline and polarization
#                         block_data = data[start_pos:end_pos]

#                         # Convert the block data to a NumPy array of half-precision floats
#                         block_array = np.frombuffer(block_data, dtype=np.float16).reshape((num_channels, 2))

#                         # Split the block array into real and imaginary parts
#                         real_part = block_array[:, 0]
#                         imaginary_part = block_array[:, 1]

#                         # Sum across the polarization channels
#                         summed_real += real_part
#                         summed_imaginary += imaginary_part

#                     # Pack real and imaginary parts as a complex number
#                     complex_visibilities = summed_real + 1j * summed_imaginary

#                     # Get the corresponding UVW coordinates for this baseline
#                     u, v, w = uvw_data[data_index]

#                     # Store the baseline index, UVW, and visibility data into the HDF5 dataset
#                     vis_dataset[data_index] = (baseline, u, v, w, complex_visibilities)
#                     data_index += 1

# # Example usage
# file_path = '1.3s.bin'
# uvw_file_path = 'uvw_coordinates.txt'
# output_hdf5_path = 'output_data.h5'
# skip_baselines = [1, 5, 8, 10]  # Example: skip baselines 1, 5, 8, 10
# read_and_store_visibilities(file_path, uvw_file_path, output_hdf5_path, skip_baselines)
