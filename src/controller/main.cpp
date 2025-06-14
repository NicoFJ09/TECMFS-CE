#include "httplib.h"
#include "json.hpp"
#include <map>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>

using namespace httplib;
using json = nlohmann::json;

// Configuración RAID-5
const int blkSize    = 4096;                           // Tamaño de bloque en bytes
const int numDisks   = 4;                              // Número de discos en el RAID
const int totalBlocks = 104857600 / blkSize;           // Ejemplo: 100 MiB / 4 KiB

std::vector<std::string> diskAddrs = { "disk1", "disk2", "disk3", "disk4" };
std::vector<int>         diskPorts = { 8001,      8002,      8003,      8004   };
// Metadatos: nombre de archivo -> lista de (diskId, blockIdx)
std::map<std::string, std::vector<std::pair<int,int>>> fileMap;
// Tamaño original de cada archivo
std::map<std::string, size_t> fileSizeMap;

int main() {
    Server server;

    // Permitir uploads grandes (hasta 200 MiB)
    server.set_payload_max_length(200 * 1024 * 1024);

    // 1) Ping
    server.Get("/ping", [](const Request&, Response& res) {
        json j = { { "estado", "activo" } };
        res.set_content(j.dump(), "application/json");
    });

    // 2) Upload RAID-5
    server.Post("/upload", [&](const Request& req, Response& res) {
        auto filename = req.get_param_value("name");
        auto data = req.body;
        // Guardar tamaño original
        fileSizeMap[filename] = data.size();

        int stripeSize       = numDisks - 1;
        int totalDataBlocks  = (data.size() + blkSize - 1) / blkSize;
        std::vector<std::pair<int,int>> locations;

        for (int b = 0; b < totalDataBlocks; b += stripeSize) {
            // Recolectar datos de la franja
            std::vector<std::string> stripe;
            for (int i = 0; i < stripeSize; ++i) {
                int blockIdx = b + i;
                if (blockIdx * blkSize < (int)data.size()) {
                    stripe.push_back(
                        data.substr(blockIdx * blkSize, blkSize)
                    );
                } else {
                    stripe.emplace_back(blkSize, '\0');
                }
            }
            // Calcular paridad XOR
            std::string parity(blkSize, '\0');
            for (auto& blk : stripe)
                for (int i = 0; i < blkSize; ++i)
                    parity[i] ^= blk[i];

            int stripeIdx  = b / stripeSize;
            int parityDisk = stripeIdx % numDisks;
            int dataIdx    = 0;
            for (int disk = 0; disk < numDisks; ++disk) {
                std::string payload =
                    (disk == parityDisk ? parity : stripe[dataIdx++]);
                int diskBlockIdx = stripeIdx;
                Client cli(diskAddrs[disk].c_str(), diskPorts[disk]);
                cli.Post(
                    ("/block?idx=" + std::to_string(diskBlockIdx)).c_str(),
                    payload, "application/octet-stream"
                );
                locations.emplace_back(disk, diskBlockIdx);
            }
        }

        fileMap[filename] = std::move(locations);
        json j = { { "status", "OK" } };
        res.set_content(j.dump(), "application/json");
    });

    // 3) Download RAID-5
    server.Get("/download", [&](const Request& req, Response& res) {
        auto filename = req.get_param_value("name");
        auto itLoc = fileMap.find(filename);
        auto itSz  = fileSizeMap.find(filename);
        if (itLoc == fileMap.end() || itSz == fileSizeMap.end()) {
            res.status = 404;
            return;
        }
        size_t origSize = itSz->second;
        const auto& locs = itLoc->second;
        int stripes = locs.size() / numDisks;

        std::string output;
        output.reserve(stripes * (numDisks - 1) * blkSize);

        // Para cada franja s = 0 … stripes-1
        for (int s = 0; s < stripes; ++s) {
            // 1) Leer o reconstruir los numDisks bloques de la franja s
            std::vector<std::string> stripeData(numDisks);
            int missing = -1;
            for (int d = 0; d < numDisks; ++d) {
                auto [diskID, blkIdx] = locs[s * numDisks + d];
                Client cli(diskAddrs[diskID].c_str(), diskPorts[diskID]);
                auto r = cli.Get(("/block?idx=" + std::to_string(blkIdx)).c_str());
                if (r && r->status == 200 && r->body.size() == (size_t)blkSize) {
                    stripeData[d] = r->body;
                } else {
                    missing = d;
                }
            }
            // Si faltó uno, reconstruirlo por XOR
            if (missing >= 0) {
                std::string rec(blkSize, '\0');
                for (int d = 0; d < numDisks; ++d) {
                    if (d == missing) continue;
                    for (int i = 0; i < blkSize; ++i) {
                        rec[i] ^= stripeData[d][i];
                    }
                }
                stripeData[missing] = rec;
            }
            // 2) Concatenar sólo los bloques de datos (omitir paridad)
            int parityDisk = s % numDisks;
            for (int d = 0; d < numDisks; ++d) {
                if (d == parityDisk) continue;
                output += stripeData[d];
            }
        }

        // 3) Truncar al tamaño original
        if (output.size() > origSize) {
            output.resize(origSize);
        }
        res.set_content(output, "application/octet-stream");
    });


    // 4) RAID status
    server.Get("/raid-status", [&](const Request&, Response& res) {
        json j;
        for (int disk = 0; disk < numDisks; ++disk) {
            json dj = json::array();
            Client cli(diskAddrs[disk].c_str(), diskPorts[disk]);
            for (int blk = 0; blk < totalBlocks; ++blk) {
                auto r = cli.Get(
                    ("/block?idx=" + std::to_string(blk)).c_str()
                );
                dj.push_back((r && r->status == 200) ? "OK" : "MISSING");
            }
            j[std::to_string(disk + 1)] = dj;
        }
        res.set_content(j.dump(), "application/json");
    });

    // 5) Servir interfaz web estática
    server.Get("/", [&](const Request&, Response& res) {
        std::ifstream ifs("src/web/index.html");
        std::stringstream ss;
        ss << ifs.rdbuf();
        res.set_content(ss.str(), "text/html");
    });

    std::cout << "Controller escuchando en puerto 8080..." << std::endl;
    server.listen("0.0.0.0", 8080);

    return 0;
}