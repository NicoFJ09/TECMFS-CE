# Variables
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Isrc/include
LDLIBS = -lpthread
SRC = src/controller/main.cpp
TARGET = servidor

# Regla principal
all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDLIBS)

clean:
	rm -f $(TARGET)
