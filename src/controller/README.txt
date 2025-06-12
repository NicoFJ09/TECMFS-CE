Controller Node C++ implementation 

## Descripción

Este componente implementa un servidor HTTP en C++ utilizando `cpp-httplib` y `nlohmann/json`.  
El propósito actual es simular la interfaz de almacenamiento del Controller Node antes de integrar el RAID real.

## Requisitos

- Linux Ubuntu
- g++
- `cpp-httplib`
- `nlohmann/json`
- `curl` para pruebas

## Compilación

```bash
g++ -std=c++17 main.cpp -o servidor -lpthread
