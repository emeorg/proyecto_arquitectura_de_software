# proyecto_arquitectura_de_software

Descripción
------------
Repositorio de ejemplo para el proyecto de arquitectura de software. Contiene la estructura sugerida de carpetas, documentación y ejemplos de comandos para ejecutar y probar la aplicación. Ajusta las rutas y comandos según el lenguaje y herramientas reales del proyecto.

Estructura de carpetas
-------------------------------------------
```
└── 📁proyecto_arquitectura_de_software
    └── 📁cliente
        ├── cliente.py
        ├── Dockerfile
    └── 📁servidor
        ├── Dockerfile
        ├── servidor.py
    ├── docker-compose.yml
    └── README.md
```

Cómo ejecutar
-------------------------------
1) Clonar y entrar al proyecto:
    ```bash
    git clone https://github.com/emeorg/proyecto_arquitectura_de_software.git
    cd proyecto_arquitectura_de_software
    ```

2) Ejecutar docker compose
    ```bash
    docker compose up --build
    ```

3) Ingresar al cliente
    - En una terminal nueva ejecutar:
        ```bash
        docker exec -it cliente python cliente.py
        ```