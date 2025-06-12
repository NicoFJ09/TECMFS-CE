# Variables
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -lpthread
SRC = main.cpp
TARGET = servidor

# Regla principal
all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)
