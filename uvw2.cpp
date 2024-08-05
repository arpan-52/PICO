#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>

// Constants
const double PI = 3.141592653589793;
const double DEG2RAD = PI / 180.0;

// Struct to hold 3D coordinates
struct Vector3 {
    double x, y, z;
};

// Function to calculate Julian Date for a given date
double calculateJulianDate(int year, int month, int day) {
    if (month <= 2) {
        year -= 1;
        month += 12;
    }
    int A = year / 100;
    int B = 2 - A + A / 4;
    double JD = static_cast<int>(365.25 * (year + 4716))
              + static_cast<int>(30.6001 * (month + 1))
              + day + B - 1524.5;
    return JD;
}

// Function to calculate GST at 0h UT in degrees
double calculateGST0hUT(int year, int month, int day) {
    double JD = calculateJulianDate(year, month, day);
    double T = (JD - 2451545.0) / 36525.0;
    double GST_deg = 100.46061837 + 36000.770053608 * T + 0.000387933 * T * T - T * T * T / 38710000.0;
    GST_deg = fmod(GST_deg, 360.0);
    if (GST_deg < 0) GST_deg += 360.0;
    return GST_deg;
}

// Function to calculate LST in degrees
double calculateLST(double gstAt0hUT, double utHours, double longitude) {
    double gst = gstAt0hUT + utHours * (360.985647 / 24.0);
    double lst = gst + longitude;
    if (lst < 0) lst += 360.0;
    if (lst >= 360.0) lst -= 360.0;
    return lst;
}

// Function to calculate UVW coordinates
void calculateUVW(const Vector3& antenna1, const Vector3& antenna2, double ha, double dec, Vector3& uvw) {
    Vector3 baseline = { antenna2.x - antenna1.x, antenna2.y - antenna1.y, antenna2.z - antenna1.z };

    // Rotation matrices for HA and DEC
    double sinHA = sin(ha);
    double cosHA = cos(ha);
    double sinDec = sin(dec);
    double cosDec = cos(dec);

    uvw.x = -sinHA * baseline.x + cosHA * baseline.y;
    uvw.y = -sinDec * cosHA * baseline.x - sinDec * sinHA * baseline.y + cosDec * baseline.z;
    uvw.z = cosDec * cosHA * baseline.x + cosDec * sinHA * baseline.y + sinDec * baseline.z;
}

// Main function
int main() {
    Vector3 antennas[32] = {
        {1763985.93, 5770403.15, 2063520.86},
{1763992.23, 5770041.72, 2063500.55},
{1763978.98, 5769715.27, 2063540.90},
{1763927.78, 5769342.56, 2063674.49},
{1763927.97, 5769149.31, 2063664.33},
{1764058.10, 5769783.08, 2063294.31},
{1764050.23, 5769683.84, 2063320.32},
{1764109.78, 5769995.95, 2063140.57},
{1764027.59, 5769757.22, 2063389.25},
{1764170.33, 5769550.40, 2062953.41},
{1764081.47, 5769112.02, 2063219.34},
{1764188.26, 5769890.12, 2062905.36},
{1764347.65, 5769075.77, 2062422.98},
{1764186.35, 5769241.58, 2062912.27},
{1763630.80, 5772529.82, 2064494.57},
{1763271.42, 5774291.31, 2065473.36},
{1762941.39, 5777495.84, 2066444.19},
{1762801.02, 5779915.17, 2066884.10},
{1762406.93, 5781788.59, 2068084.03},
{1764921.97, 5770349.23, 2060734.97},
{1765431.89, 5769348.05, 2059261.74},
{1766163.61, 5770048.37, 2057135.94},
{1767051.93, 5770663.06, 2054561.40},
{1768571.81, 5769346.18, 2050158.42},
{1763777.63, 5768123.32, 2064132.22},
{1763496.64, 5766615.83, 2064960.29},
{1762987.52, 5764515.26, 2066440.01},
{1762245.07, 5762676.21, 2068608.43},
{1761273.29, 5761612.01, 2071358.04},
{1760877.46, 5758469.50, 2072457.16},
{1760876.87, 5758469.67, 2072457.16},
{1760876.87, 5758469.67, 2072457.16}
    };

    double latitude = 19.0; // Latitude of the array in degrees
    double startHour = 18.0; // Start of observation in IST (hours)
    double longitude = 74.0; // Observer's longitude in degrees
    double ra = 13.0 * 15.0; // Right Ascension in degrees (convert RA hours to degrees)
    double dec = 33.0; // Declination in degrees

    // Convert RA and DEC to radians for the calculations
    double raRad = degreesToRadians(ra);
    double decRad = degreesToRadians(dec);

    // Convert startHour from IST to UT
    double startHourUT = startHour - 5.5; // IST is UTC+5:30
    if (startHourUT < 0) startHourUT += 24.0; // Wrap around

    // Calculate GST at 0h UT for the given date
    double gstAt0hUT = calculateGST0hUT(2024, 8, 1);

    std::ofstream outputFile("uvw_coordinates.txt");
    if (!outputFile) {
        std::cerr << "Error opening file for writing." << std::endl;
        return 1;
    }

    double timeStep = 5.0; // seconds
    double observationDuration = 4.0; // total observation time in seconds
    int numSteps = static_cast<int>(observationDuration / timeStep);

    for (int step = 0; step <= numSteps; ++step) {
        double currentTime = step * timeStep;
        double utHours = startHourUT + currentTime / 3600.0; // Convert seconds to hours
        double lstDeg = calculateLST(gstAt0hUT, utHours, longitude);
        double haDeg = lstDeg - ra; // Hour angle in degrees
        double haRad = degreesToRadians(haDeg); // Convert to radians

        for (size_t i = 0; i < sizeof(antennas) / sizeof(Vector3); ++i) {
            for (size_t j = i + 1; j < sizeof(antennas) / sizeof(Vector3); ++j) {
                Vector3 uvw;
                calculateUVW(antennas[i], antennas[j], haRad, decRad, uvw);

                // Save UVW coordinates to file
                outputFile << uvw.x << " " << uvw.y << " " << uvw.z << "\n";
            }
        }
    }

    outputFile.close();
    std::cout << "UVW coordinates have been saved to uvw_coordinates.txt." << std::endl;
    return 0;
}
