#include <iostream>
#include <fstream>

int main() {
    std::ifstream inputFile("corr.dat", std::ios::binary);

    if (!inputFile.is_open()) {
        std::cerr << "Error opening file." << std::endl;
        return 1;
    }

    double value;
    while (inputFile.read(reinterpret_cast<char*>(&value), sizeof(double))) {
        std::cout << "Read double: " << value << std::endl;
    }

    inputFile.close();
    return 0;
}
