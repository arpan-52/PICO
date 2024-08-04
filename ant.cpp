#include <iostream>
#include <cmath>
#include <vector>

// Constants
const double a = 6378137.0; // Semi-major axis in meters
const double f = 1.0 / 298.257223563; // Flattening
const double b = a * (1 - f); // Semi-minor axis in meters
const double DEG2RAD = M_PI / 180.0; // Conversion factor from degrees to radians

// Struct to hold 3D coordinates
struct Vector3 {
    double x, y, z;
};

// Function to convert geodetic coordinates to ECEF
Vector3 geodeticToECEF(double latitude, double longitude, double altitude) {
    // Convert latitude and longitude from degrees to radians
    double phi = latitude * DEG2RAD;
    double lambda = longitude * DEG2RAD;

    // Calculate eccentricity squared
    double e2 = (a * a - b * b) / (a * a);

    // Calculate the radius of curvature in the prime vertical
    double N = a / sqrt(1 - e2 * sin(phi) * sin(phi));

    // Compute ECEF coordinates
    Vector3 ecef;
    ecef.x = (N + altitude) * cos(phi) * cos(lambda);
    ecef.y = (N + altitude) * cos(phi) * sin(lambda);
    ecef.z = (b * b / (a * a) * N + altitude) * sin(phi);

    return ecef;
}

int main() {
    // Reference point coordinates
    double refLatitude = 19.0;
    double refLongitude = 73.0;
    double refAltitude = 588.0;

    // Calculate the ECEF coordinates of the reference point
    Vector3 refECEF = geodeticToECEF(refLatitude, refLongitude, refAltitude);

    // Antenna data (relative positions)
    std::vector<Vector3> relativeAntennas = {
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

    // Print the reference point ECEF coordinates
    std::cout << "Reference ECEF Coordinates: X = " << refECEF.x << ", Y = " << refECEF.y << ", Z = " << refECEF.z << std::endl;

    // Print the antenna ECEF coordinates in the same format
    std::cout << "Antenna ECEF Coordinates:" << std::endl;
    for (const auto& relPos : relativeAntennas) {
        Vector3 antennaECEF;
        antennaECEF.x = refECEF.x + relPos.x;
        antennaECEF.y = refECEF.y + relPos.y;
        antennaECEF.z = refECEF.z + relPos.z;

        std::cout << "{" << antennaECEF.x << ", " << antennaECEF.y << ", " << antennaECEF.z << "}," << std::endl;
    }

    return 0;
}
