#include <iostream>
#include <unordered_map>
#include <fstream>
#include "include/httplib.h"
#include "include/json.hpp"

using namespace httplib;
using json = nlohmann::json;

std::unordered_map<std::string, std::string> archivosMap;

int main() {
    Server server;

    // POST /upload - soporte multipart/form-data
    server.Post("/upload", [](const Request& req, Response& res) {
        const auto& files = req.files;
        auto it = files.find("file");

        if (it != files.end()) {
            const auto& archivo = it->second;
            std::string nombre = archivo.filename;
            std::string contenido = archivo.content;

            std::string ruta = "./uploads/" + nombre;
            std::ofstream ofs(ruta, std::ios::binary);
            ofs << contenido;
            ofs.close();

            archivosMap[nombre] = ruta;

            std::cout << "[INFO] Archivo recibido: " << nombre << std::endl;
            std::cout << "[INFO] Guardado en: " << ruta << "\n" << std::endl;

            json respuesta = {{"mensaje", "Archivo recibido exitosamente"}, {"ruta", ruta}};
            res.set_content(respuesta.dump(), "application/json");
        } else {
            std::cout << "[ERROR] No se envió archivo con la clave 'file'\n" << std::endl;
            res.status = 400;
            res.set_content("{\"error\":\"Archivo no enviado con clave 'file'\"}", "application/json");
        }
    });

    // GET / (sirve index.html desde /src/web/)
    server.Get("/", [](const Request&, Response& res) {
        std::ifstream file("../web/index.html"); // Ajuste correcto de ruta
        if (file.is_open()) {
            std::string contenido((std::istreambuf_iterator<char>(file)),
                                   std::istreambuf_iterator<char>());
            res.set_content(contenido, "text/html");
            std::cout << "[INFO] index.html servido correctamente\n" << std::endl;
        } else {
            res.status = 404;
            res.set_content("index.html no encontrado", "text/plain");
            std::cout << "[ERROR] No se encontró index.html\n" << std::endl;
        }
    });

    // GET /download
    server.Get("/download", [](const Request& req, Response& res) {
        if (req.has_param("nombre")) {
            std::string nombre = req.get_param_value("nombre");

            std::cout << "[INFO] Solicitud de descarga para: " << nombre << std::endl;

            if (archivosMap.find(nombre) != archivosMap.end()) {
                json respuesta = {{"ruta", archivosMap[nombre]}};
                res.set_content(respuesta.dump(), "application/json");
                std::cout << "[INFO] Archivo encontrado: " << archivosMap[nombre] << "\n" << std::endl;
            } else {
                res.status = 404;
                res.set_content("{\"error\":\"Archivo no encontrado\"}", "application/json");
                std::cout << "[ERROR] Archivo no encontrado: " << nombre << "\n" << std::endl;
            }
        } else {
            res.status = 400;
            res.set_content("{\"error\":\"Falta parámetro 'nombre'\"}", "application/json");
            std::cout << "[ERROR] Falta parámetro 'nombre' en /download\n" << std::endl;
        }
    });

    // GET /search
    server.Get("/search", [](const Request& req, Response& res) {
        if (req.has_param("nombre")) {
            std::string nombre = req.get_param_value("nombre");
            bool existe = archivosMap.find(nombre) != archivosMap.end();
            json respuesta = {{"existe", existe}};
            res.set_content(respuesta.dump(), "application/json");

            std::cout << "[INFO] Búsqueda de archivo: " << nombre 
                      << " -> " << (existe ? "Existe" : "No existe") << "\n" << std::endl;
        } else {
            res.status = 400;
            res.set_content("{\"error\":\"Falta parámetro 'nombre'\"}", "application/json");
            std::cout << "[ERROR] Falta parámetro 'nombre' en /search\n" << std::endl;
        }
    });

    // DELETE /delete
    server.Delete("/delete", [](const Request& req, Response& res) {
        if (req.has_param("nombre")) {
            std::string nombre = req.get_param_value("nombre");

            std::cout << "[INFO] Eliminando archivo: " << nombre << std::endl;

            if (archivosMap.erase(nombre)) {
                res.set_content("{\"mensaje\":\"Archivo eliminado\"}", "application/json");
                std::cout << "[INFO] Archivo eliminado correctamente\n" << std::endl;
            } else {
                res.status = 404;
                res.set_content("{\"error\":\"Archivo no encontrado\"}", "application/json");
                std::cout << "[ERROR] No se encontró el archivo para eliminar: " << nombre << "\n" << std::endl;
            }
        } else {
            res.status = 400;
            res.set_content("{\"error\":\"Falta parámetro 'nombre'\"}", "application/json");
            std::cout << "[ERROR] Falta parámetro 'nombre' en /delete\n" << std::endl;
        }
    });

    // GET /status
    server.Get("/status", [](const Request&, Response& res) {
        json estado;
        for (const auto& par : archivosMap)
            estado[par.first] = par.second;

        res.set_content(estado.dump(4), "application/json");
        std::cout << "[INFO] Estado actual solicitado\n" << std::endl;
    });

    // GET /ping
    server.Get("/ping", [](const Request&, Response& res) {
        res.set_content("{\"estado\":\"activo\"}", "application/json");
        std::cout << "[INFO] Ping recibido\n" << std::endl;
    });

    std::cout << "[INFO] Servidor corriendo en http://localhost:8080\n" << std::endl;
    server.listen("0.0.0.0", 8080);
    return 0;
}
