FROM debian:bullseye

# Instala compilador y herramientas necesarias
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    curl \
    #ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crea directorio de trabajo
WORKDIR /app

# Copia todos los archivos del proyecto
COPY . .

# Crea el directorio de uploads si no existe
RUN mkdir -p /app/uploads

# Compila el proyecto
RUN make

# Expone el puerto del servidor
EXPOSE 8080

# Ejecuta el binario generado (servidor)
CMD ["./servidor"]
