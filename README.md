# Instrucciones de uso y comandos para el proyecto (Update 2.2)
# 1 Inicializacion del Docker:
# Bajar cualquier estado anterior
docker-compose down --volumes --remove-orphans
# Reconstruir todas las imagenes:
docker-compose build --no-cache
# Levantar el stack en segundo plano:
docker-compose up -d
# Comprobar que todos los servicios están “Up”
docker-compose ps
# ---------Pruebas de Salud de Servidores----------
# Ping al Controller
curl http://localhost:8080/ping
Debe devolver {"estado":"activo"}
# Leer el bloque 0 en cada Disk Node
    for p in 8001 8002 8003 8004; do
    curl -I http://localhost:$p/block?idx=0
    done
Todos deben responder HTTP/1.1 200 OK y Content-Length: 4096
# ---------Subida y Descarga de Archivos----------
# Upload de un PDF
curl -H "Content-Type: application/octet-stream" \
     --data-binary @docs/prueba.pdf \
     "http://localhost:8080/upload?name=prueba.pdf"
Debe responder {"status":"OK"}
# Download y comparación de hashes
curl "http://localhost:8080/download?name=prueba.pdf" \
     --output docs/prueba_rec.pdf
ls -l docs/prueba.pdf docs/prueba_rec.pdf
md5sum docs/prueba.pdf docs/prueba_rec.pdf
— Ambos ficheros deben tener el mismo tamaño y el mismo MD5.
# ---------Toleracia a Fallos----------
# Simular caída de un disco (por ejemplo disk2)
docker-compose stop disk2
# Volver a descargar
curl "http://localhost:8080/download?name=prueba.pdf" \
     --output docs/prueba_rec2.pdf
md5sum docs/prueba.pdf docs/prueba_rec2.pdf
— Debe seguir coincidiendo el MD5 aun con un nodo caído.
# Rearrancar el disco
docker-compose start disk2
# ---------Salud de Bloques----------
Obtener un estado rápido de los primeros 100 bloques
curl -s "http://localhost:8080/raid-status?max=100" | jq .
# ---------Eliminacio, listado de documentos----------
curl "http://localhost:8080/list" | jq .
curl -X DELETE "http://localhost:8080/delete?name=prueba.pdf" | jq .

