FROM debian:trixie-slim

# Instala compilador, make, Python3, pip, Flask y las cabeceras de OpenSSL
RUN apt-get update && apt-get install -y \
      g++ \
      make \
      curl \
      python3 \
      python3-pip \
      python3-flask \
      libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copia el proyecto al contenedor
COPY . .

# Da permiso de ejecución al Disk Node
RUN chmod +x src/controller/disk_nodes/simulated_disks/disk_*/disk_node.py

# Crea la carpeta uploads
RUN mkdir -p /app/uploads

# Compila tu servidor C++ dentro del contenedor
RUN make

# Expone todos los puertos que usas
EXPOSE 8080 8001 8002 8003 8004

# Por defecto arranca el Controller
CMD ["./servidor"]
