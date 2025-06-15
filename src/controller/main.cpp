#include "httplib.h"
#include "json.hpp"
#include <map>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <openssl/md5.h>
#include <sstream>
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
            // ——— Recolectar datos de la franja y rellenar a blkSize ———
            std::vector<std::string> stripe;
            stripe.reserve(stripeSize);
        
            for (int i = 0; i < stripeSize; ++i) {
                int blockIdx = b + i;
                size_t offset = static_cast<size_t>(blockIdx) * blkSize;
        
                if (offset < data.size()) {
                    size_t avail = std::min((size_t)blkSize, data.size() - offset);
        
                    // Extraemos el chunk parcial
                    std::string chunk = data.substr(offset, avail);
        
                    // ——— DEBUG: muestra hashpfx del fragmento antes de rellenar ———
                    {
                        unsigned char d2[16];
                        // calcula MD5 sobre los 'avail' bytes
                        MD5(reinterpret_cast<const unsigned char*>(chunk.data()),
                            avail, d2);
        
                        std::ostringstream tmp;
                        for (int k = 0; k < 4; ++k) {
                            tmp
                              << std::hex << std::setw(2) << std::setfill('0')
                              << static_cast<int>(d2[k]);
                        }
        
                        std::cerr
                          << "[CHUNK-DBG] stripe=" << (b/stripeSize)
                          << " i="      << i
                          << " offset=" << offset
                          << " avail="  << avail
                          << " hashpfx="<< tmp.str()
                          << "\n";
                    }
                    // —————————————————————————————————————————————————————————
        
                    // Rellena el resto a blkSize y guarda
                    chunk.append(blkSize - avail, '\0');
                    stripe.push_back(std::move(chunk));
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
                // Calculamos de nuevo cuál bloque de datos concreto estamos enviando
                int dataPos = (disk < parityDisk) ? disk : (disk - 1);
                int blockIdx = b + dataPos;
            
                // Seleccionamos payload: paridad o bloque de datos
                std::string payload =
                    (disk == parityDisk ? parity : stripe[dataPos]);
                int diskBlockIdx = stripeIdx;
            
                // ✱ DEBUG: imprimimos stripeIdx, disk, blockIdx real y MD5 del payload
                {
                    unsigned char digest[16];
                    MD5((unsigned char*)payload.data(), blkSize, digest);
                    std::ostringstream md5str;
                    for (int i = 0; i < 4; ++i)
                        md5str << std::hex << std::setw(2) << std::setfill('0')
                               << (int)digest[i];
                    std::cerr << "[UPLOAD-DBG] stripe=" << stripeIdx
                              << " disk="   << disk
                              << " blockIdx="<< blockIdx
                              << " md5pfx="  << md5str.str()
                              << "\n";
                }
            
                // Enviamos al disk node
                Client cli(diskAddrs[disk].c_str(), diskPorts[disk]);
                cli.Post(
                    ("/block?idx=" + std::to_string(diskBlockIdx)).c_str(),
                    payload, "application/octet-stream"
                );
                locations.emplace_back(disk, diskBlockIdx);
            }
            
            
        }
        
        std::cerr << "[DEBUG] total stripes=" << (locations.size()/numDisks)
        << " total blocks=" << locations.size() << "\n";
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

        // Construimos el buffer crudo completo
        std::vector<char> buffer;
        buffer.reserve(stripes * (numDisks - 1) * blkSize);

        for (int s = 0; s < stripes; ++s) {
            std::vector<std::string> stripeData(numDisks);
            int missing = -1;
            // 1) Leer o reconstruir cada bloque
            for (int d = 0; d < numDisks; ++d) {
                auto [diskID, blkIdx] = locs[s * numDisks + d];
                Client cli(diskAddrs[diskID].c_str(), diskPorts[diskID]);
                auto r = cli.Get(("/block?idx=" + std::to_string(blkIdx)).c_str());
                if (r && r->status == 200 && r->body.size() == (size_t)blkSize) {
                    stripeData[diskID] = r->body;
                } else {
                    missing = diskID;
                }
            }
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
            // 2) Añadimos los bloques de datos (omitir paridad) directamente al buffer
            int parityDisk = s % numDisks;
            for (int d = 0; d < numDisks; ++d) {
                if (d == parityDisk) continue;
                const auto& blk = stripeData[d];
                buffer.insert(buffer.end(), blk.begin(), blk.end());
            }
        }

        // 3) Truncar a tamaño original si nos pasamos
        if (buffer.size() > origSize) {
            buffer.resize(origSize);
        }

        // 4) Enviar exactamente origSize bytes de datos crudos
        res.set_content(buffer.data(), buffer.size(), "application/octet-stream");
    });


    // 4) RAID status
    server.Get("/raid-status", [&](const Request& req, Response& res) {
        int maxBlocks = req.has_param("max")
                      ? std::stoi(req.get_param_value("max"))
                      : totalBlocks;
    
        json j;
        for (int disk = 0; disk < numDisks; ++disk) {
            json dj = json::array();
            Client cli(diskAddrs[disk], diskPorts[disk]);
            for (int blk = 0; blk < maxBlocks; ++blk) {
                auto r = cli.Get("/block?idx=" + std::to_string(blk));
                dj.push_back((r && r->status == 200) ? "OK" : "MISSING");
            }
            j[std::to_string(disk+1)] = dj;
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

    // 6) Eliminar un documento
    server.Delete("/delete", [&](const Request& req, Response& res) {
        auto filename = req.get_param_value("name");
        auto itLoc = fileMap.find(filename);
        auto itSz  = fileSizeMap.find(filename);
        if (itLoc == fileMap.end() || itSz == fileSizeMap.end()) {
            res.status = 404;
            json j = { { "error", "no existe el documento" } };
            res.set_content(j.dump(), "application/json");
            return;
        }
    
        // 1) Prepara un bloque de ceros
        std::string zeroBlk(blkSize, '\0');
    
        // 2) Para cada bloque en locations, envía ceros
        for (auto [diskID, stripeIdx] : itLoc->second) {
            Client cli(diskAddrs[diskID].c_str(), diskPorts[diskID]);
            // Ignoramos la respuesta; queremos sobreescribir
            cli.Post(
              ("/block?idx=" + std::to_string(stripeIdx)).c_str(),
              zeroBlk, "application/octet-stream"
            );
        }
    
        // 3) Borra los metadatos
        fileMap.erase(itLoc);
        fileSizeMap.erase(itSz);
    
        json j = { { "status", "deleted" } };
        res.set_content(j.dump(), "application/json");
    });
    

    // 7) Listar documentos
    server.Get("/list", [&](const Request& /*req*/, Response& res) {
        json j = json::array();
        for (auto& [name, locs] : fileMap) {
            j.push_back(name);
        }
        res.set_content(j.dump(), "application/json");
    });


    std::cout << "Controller escuchando en puerto 8080..." << std::endl;
    server.listen("0.0.0.0", 8080);

    return 0;
}