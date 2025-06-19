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

enum DiskState { ONLINE, BUSY, REBUILDING, FAILED };
struct DiskInfo {
    DiskState status = ONLINE;
    std::chrono::system_clock::time_point last_change = std::chrono::system_clock::now();
    std::string last_activity = "Idle";
};

std::vector<DiskInfo> disks(numDisks); // numDisks = 4
std::mutex disk_mutex;

// Verifica si un disco está encendido (responde en su puerto)
bool is_disk_alive(const std::string& host, int port) {
    httplib::Client cli(host, port);
    cli.set_connection_timeout(1, 0); // 1 segundo
    auto res = cli.Get("/ping");
    return res && res->status == 200;
}

// Actualiza el estado y actividad de un disco
void set_disk_status(int idx, DiskState new_status, const std::string& activity) {
    std::lock_guard<std::mutex> lock(disk_mutex);
    disks[idx].status = new_status;
    disks[idx].last_change = std::chrono::system_clock::now();
    disks[idx].last_activity = activity;
}

// Devuelve el tiempo desde el último cambio
std::string time_since(const std::chrono::system_clock::time_point& tp) {
    using namespace std::chrono;
    auto now = system_clock::now();
    auto secs = duration_cast<seconds>(now - tp).count();
    if (secs < 60) return std::to_string(secs) + " seconds ago";
    auto mins = secs / 60;
    return std::to_string(mins) + " minutes ago";
}

// Devuelve el JSON de estado de discos
json get_disk_status_json() {
    std::lock_guard<std::mutex> lock(disk_mutex);
    json disks_json = json::array();
    for (int i = 0; i < disks.size(); ++i) {
        std::string status_str;
        switch (disks[i].status) {
            case ONLINE: status_str = "ONLINE"; break;
            case BUSY: status_str = "BUSY"; break;
            case REBUILDING: status_str = "REBUILDING"; break;
            case FAILED: status_str = "FAILED"; break;
        }
        disks_json.push_back({
            {"name", "Disk D" + std::to_string(i+1)},
            {"status", status_str},
            {"activity", disks[i].last_activity + " (" + time_since(disks[i].last_change) + ")"}
        });
    }
    return {{"tag", "disk_status"}, {"disks", disks_json}};
}

// Refresca el estado de todos los discos antes de cada acción
void refresh_all_disks_status(DiskState during_action, const std::string& activity) {
    for (int i = 0; i < numDisks; ++i) {
        if (is_disk_alive(diskAddrs[i], diskPorts[i])) {
            set_disk_status(i, during_action, activity);
        } else {
            set_disk_status(i, FAILED, "No response");
        }
    }
}

// Refresca el estado de todos los discos después de cada acción
void refresh_all_disks_status_post(const std::string& activity) {
    for (int i = 0; i < numDisks; ++i) {
        if (is_disk_alive(diskAddrs[i], diskPorts[i])) {
            set_disk_status(i, ONLINE, activity);
        } else {
            set_disk_status(i, FAILED, "No response");
        }
    }
}

int main() {
    Server server;

    // Permitir uploads grandes (hasta 200 MiB)
    server.set_payload_max_length(200 * 1024 * 1024);

    // 1) Ping
    server.Get("/ping", [&](const Request& req, Response& res) {
        refresh_all_disks_status_post("Ping checked");
        json j = {{"estado", "activo"}, {"disk_status", get_disk_status_json()}};
        res.set_content(j.dump(), "application/json");
    });

    // 2) Upload RAID-5
    server.Post("/upload", [&](const Request& req, Response& res) {
        refresh_all_disks_status(BUSY, "Uploading");
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
                        for (int k = 0; k < 4; k++) {
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
                    for (int i = 0; i < 4; i++)
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
        refresh_all_disks_status_post("Upload complete");
        json j = { { "status", "OK" }, { "disk_status", get_disk_status_json() } };
        res.set_content(j.dump(), "application/json");
    });


    // 3) Download RAID-5
    server.Get("/download", [&](const Request& req, Response& res) {
        refresh_all_disks_status(BUSY, "Downloading");
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
    
        for (int s = 0; s < stripes; ++s) {
            // 1) Leer o reconstruir los numDisks bloques de la franja s
            std::vector<std::string> stripeData(numDisks);
            int missing = -1;
            int blkIdxOfMissing = -1;
            for (int d = 0; d < numDisks; ++d) {
                auto [diskID, blkIdx] = locs[s * numDisks + d];
                Client cli(diskAddrs[d].c_str(), diskPorts[d]);
                auto r = cli.Get(("/block?idx=" + std::to_string(blkIdx)).c_str());
                if (r && r->status == 200 && r->body.size() == (size_t)blkSize) {
                    stripeData[d] = r->body;
                } else {
                    missing = d;
                    blkIdxOfMissing = blkIdx;
                }
            }
            // Si faltó uno, reconstruirlo por XOR y además repararlo en el nodo
            if (missing >= 0) {
                // … reconstrucción de rec …
                std::string rec(blkSize, '\0');
                for (int d = 0; d < numDisks; ++d) {
                    if (d == missing) continue;
                    for (int i = 0; i < blkSize; ++i) {
                        rec[i] ^= stripeData[d][i];
                    }
                }
                stripeData[missing] = rec;
            
                // ——— DEBUG: mostramos información de la reparación ———
                std::cerr << "[REPAIR-DBG] stripe="        << s
                          << " missingDisk="              << missing
                          << " blkIdxOfMissing="         << blkIdxOfMissing
                          << " first4bytes(rec)="
                          << std::hex << std::setw(2) << std::setfill('0')
                          << (int)(unsigned char)rec[0]
                          << (int)(unsigned char)rec[1]
                          << (int)(unsigned char)rec[2]
                          << (int)(unsigned char)rec[3]
                          << "\n";
            
                // ——— READ-REPAIR: escribe el bloque reconstruido de vuelta ———
                Client repairCli(diskAddrs[missing].c_str(), diskPorts[missing]);
                repairCli.Post(
                    ("/block?idx=" + std::to_string(blkIdxOfMissing)).c_str(),
                    rec,
                    "application/octet-stream"
                );
                // ——— DEBUG: confirmación del POST de reparación ———
                std::cerr << "[REPAIR-DBG] POSTed repair to disk="
                          << missing
                          << " idx="        << blkIdxOfMissing
                          << "\n";
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
        refresh_all_disks_status_post("Download complete");
        json j = {{"status", "OK"}, {"disk_status", get_disk_status_json()}};
        res.set_content(output, "application/octet-stream");
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

    // 4) DELETE RAID-5 (limpia sólo los bloques de este archivo)
    server.Delete("/delete", [&](const Request& req, Response& res) {
        refresh_all_disks_status(BUSY, "Deleting");
        auto filename = req.get_param_value("name");
        // Busca los metadatos de este archivo
        auto itLoc = fileMap.find(filename);
        if (itLoc == fileMap.end()) {
            // Si no existe, devolvemos error 404
            json j = { { "error", "no existe el documento" } };
            res.status = 404;
            res.set_content(j.dump(), "application/json");
            return;
        }

        // Obtenemos la lista de (diskID, blockIdx) usados al subirlo
        const auto& locs = itLoc->second;
        // Preparar un bloque lleno de ceros
        std::string zeros(blkSize, '\0');

        // Debug: aviso de cuántos bloques vamos a borrar
        std::cerr << "[DELETE] borrando " << locs.size()
                << " bloques de '" << filename << "'\n";

        // Para cada bloque, lanzamos un POST de ceros al disco correspondiente
        for (auto [diskID, blockIdx] : locs) {
            std::cerr << "[DELETE] disk=" << diskID
                    << " blockIdx=" << blockIdx << "\n";
            Client cli(diskAddrs[diskID].c_str(), diskPorts[diskID]);
            cli.Post(
                ("/block?idx=" + std::to_string(blockIdx)).c_str(),
                zeros, "application/octet-stream"
            );
        }

        // Limpiar nuestros mapas de metadatos
        fileMap.erase(itLoc);
        fileSizeMap.erase(filename);

        // Respuesta OK
        refresh_all_disks_status_post("Delete complete");
        json j = {{"status", "deleted"}, {"disk_status", get_disk_status_json()}};
        res.set_content(j.dump(), "application/json");
    });


    // 7) Listar documentos
    server.Get("/list", [&](const Request& /*req*/, Response& res) {
        json j = json::array();
        for (auto& [name, locs] : fileMap) {
            json file_info;
            file_info["name"] = name;
            
            // Get file size from fileSizeMap
            auto sizeIt = fileSizeMap.find(name);
            if (sizeIt != fileSizeMap.end()) {
                size_t bytes = sizeIt->second;
                
                // Format file size nicely
                if (bytes < 1024) {
                    file_info["size"] = std::to_string(bytes) + " B";
                } else if (bytes < 1024 * 1024) {
                    file_info["size"] = std::to_string(bytes / 1024) + " KB";
                } else if (bytes < 1024 * 1024 * 1024) {
                    file_info["size"] = std::to_string(bytes / (1024 * 1024)) + " MB";
                } else {
                    file_info["size"] = std::to_string(bytes / (1024 * 1024 * 1024)) + " GB";
                }
                
                file_info["size_bytes"] = bytes;
            } else {
                file_info["size"] = "Unknown";
                file_info["size_bytes"] = 0;
            }
            
            // Add block count information
            file_info["blocks"] = locs.size();
            file_info["stripes"] = locs.size() / numDisks;
            
            j.push_back(file_info);
        }
        res.set_content(j.dump(), "application/json");
    });

    // 8) Reboot disk (placeholder - no hace nada por ahora)
    server.Post("/reboot", [&](const Request& req, Response& res) {
        auto diskName = req.get_param_value("disk");
        int idx = -1;
        for (int i = 0; i < numDisks; ++i) {
            if (diskName == "Disk D" + std::to_string(i+1)) idx = i;
        }
        if (idx >= 0) {
            set_disk_status(idx, REBUILDING, "Rebooting");
            // Simula reboot: stop/start contenedor (real: system call a docker-compose)
            std::this_thread::sleep_for(std::chrono::seconds(2)); // Simulación
            if (is_disk_alive(diskAddrs[idx], diskPorts[idx])) {
                set_disk_status(idx, ONLINE, "Reboot complete");
            } else {
                set_disk_status(idx, FAILED, "No response after reboot");
            }
            json j = {{"status", "accepted"}, {"disk_status", get_disk_status_json()}};
            res.set_content(j.dump(), "application/json");
        } else {
            json j = {{"status", "error"}, {"message", "Invalid disk"}, {"disk_status", get_disk_status_json()}};
            res.set_content(j.dump(), "application/json");
        }
    });

    server.Get("/disk-status", [&](const Request& req, Response& res) {
        json j = get_disk_status_json();
        res.set_content(j.dump(), "application/json");
    });

    std::cout << "Controller escuchando en puerto 8080..." << std::endl;
    server.listen("0.0.0.0", 8080);

    return 0;
}