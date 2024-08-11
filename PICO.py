import numpy as np
from datetime import datetime 

from PICO_functions import configure_logger, calculate_and_save_uvw_with_wavelength

filename ='corr.dat'
DM = 100

# start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# science_log = 'PICO_{}.log'.format(start_time)
# # Configure the science logger
# logger = configure_logger('logger', science_log)
# logger.info("Started Operation ......")
# logger.info(f"Reading the {filename}")
# logger.info(f"Dedispersing it with DM {DM}")


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



ra = 13.0 * 15.0  # Right Ascension in degrees
dec = 33.0        # Declination in degrees
freq_low = 550e6    # Low frequency in Hz
freq_high = 650e6   # High frequency in Hz
num_channels = 4096 # Number of frequency channels

start_time = 0 #in IST
obs_date = (2024, 8, 1)


# Read the file....

calculate_and_save_uvw_with_wavelength(antennas, ra, dec, freq_low, freq_high, num_channels)



