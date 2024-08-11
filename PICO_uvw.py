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


antennas = [
    [1763985.93, 5770403.15, 2063520.86],
    [1763992.23, 5770041.72, 2063500.55],
    [1763978.98, 5769715.27, 2063540.90],
    [1763927.78, 5769342.56, 2063674.49],
    [1763927.97, 5769149.31, 2063664.33],
    [1764058.10, 5769783.08, 2063294.31],
    [1764050.23, 5769683.84, 2063320.32],
    [1764109.78, 5769995.95, 2063140.57],
    [1764027.59, 5769757.22, 2063389.25],
    [1764170.33, 5769550.40, 2062953.41],
    [1764081.47, 5769112.02, 2063219.34],
    [1764188.26, 5769890.12, 2062905.36],
    [1764347.65, 5769075.77, 2062422.98],
    [1764186.35, 5769241.58, 2062912.27],
    [1763630.80, 5772529.82, 2064494.57],
    [1763271.42, 5774291.31, 2065473.36],
    [1762941.39, 5777495.84, 2066444.19],
    [1762801.02, 5779915.17, 2066884.10],
    [1762406.93, 5781788.59, 2068084.03],
    [1764921.97, 5770349.23, 2060734.97],
    [1765431.89, 5769348.05, 2059261.74],
    [1766163.61, 5770048.37, 2057135.94],
    [1767051.93, 5770663.06, 2054561.40],
    [1768571.81, 5769346.18, 2050158.42],
    [1763777.63, 5768123.32, 2064132.22],
    [1763496.64, 5766615.83, 2064960.29],
    [1762987.52, 5764515.26, 2066440.01],
    [1762245.07, 5762676.21, 2068608.43],
    [1761273.29, 5761612.01, 2071358.04],
    [1760877.46, 5758469.50, 2072457.16],
    [1760876.87, 5758469.67, 2072457.16],
    [1760876.87, 5758469.67, 2072457.16]
]


ra =  24*15 # Convert RA from hms to decimal degrees
dec = -54  # Convert DEC from dms to decimal degrees
freq_low = 550e6  # 550 MHz
freq_high = 750e6  # 750 MHz
num_channels = 4096
start_ist = 16.7725  # 16:46:21.00 IST converted to decimal hours
date_obs = [2024, 1, 8]  # 8th August 2024
duration_sec = 0.1  # 100 ms
time_resolution_sec = 1.3e-3  # 1.3 ms

# calculate_and_save_uvw_with_wavelength(antennas, ra, dec, freq_low, freq_high, num_channels, start_ist, date_obs, duration_sec, time_resolution_sec)


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
