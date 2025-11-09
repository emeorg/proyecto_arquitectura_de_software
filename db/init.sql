CREATE TABLE Generos (
    GeneroID SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Fabricantes (
    FabricanteID SERIAL PRIMARY KEY,
    Fabricante VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Consolas (
    ConsolaID SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL UNIQUE,
    FabricanteID INT,
    FOREIGN KEY (FabricanteID) REFERENCES Fabricantes(FabricanteID)
);

CREATE TABLE Proveedores (
    ProveedorID SERIAL PRIMARY KEY,
    NombreProveedor VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE Juegos (
    JuegoID SERIAL PRIMARY KEY,
    Titulo VARCHAR(255) NOT NULL,
    GeneroID INT,
    ProveedorID INT,
    Clasificacion VARCHAR(10),
    Lanzamiento NUMERIC(4),

    FOREIGN KEY (GeneroID) REFERENCES Generos(GeneroID),
    FOREIGN KEY (ProveedorID) REFERENCES Proveedores(ProveedorID)
);

CREATE TABLE Clientes (
    ClienteID SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Apellido VARCHAR(100),
    Email VARCHAR(255) UNIQUE,
    Telefono VARCHAR(20),
    FechaRegistro DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE Productos (
    ProductoID SERIAL PRIMARY KEY,
    JuegoID INT NOT NULL,
    ConsolaID INT NOT NULL,
    Formato VARCHAR(10) NOT NULL,
    Condicion VARCHAR(10) NOT NULL,
    PrecioVenta NUMERIC(10) NOT NULL,
    Stock INT NOT NULL DEFAULT 0,
    SKU VARCHAR(100) UNIQUE,
    CostoAdquisicion NUMERIC(10),

    FOREIGN KEY (JuegoID) REFERENCES Juegos(JuegoID),
    FOREIGN KEY (ConsolaID) REFERENCES Consolas(ConsolaID),
    
    CHECK (Formato IN ('Fisico', 'Digital')),
    CHECK (Condicion IN ('Nuevo', 'Usado')),
    CHECK (NOT (Formato = 'Digital' AND Condicion = 'Usado'))
);

CREATE TABLE Ventas (
    VentaID SERIAL PRIMARY KEY,
    ClienteID INT, 
    FechaVenta TIMESTAMP DEFAULT (NOW()),
    TotalVenta NUMERIC(12) NOT NULL,
    MetodoPago VARCHAR(50),
    
    FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID)
);

CREATE TABLE DetalleVenta (
    DetalleVentaID SERIAL PRIMARY KEY,
    VentaID INT NOT NULL,
    ProductoID INT NOT NULL,
    Cantidad INT NOT NULL DEFAULT 1,
    PrecioUnitarioVenta NUMERIC(10) NOT NULL,
    
    FOREIGN KEY (VentaID) REFERENCES Ventas(VentaID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID),
    CHECK (Cantidad > 0)
);

CREATE TABLE Compras (
    CompraID SERIAL PRIMARY KEY,
    ProveedorID INT,
    FechaCompra DATE DEFAULT (CURRENT_DATE),
    TotalCompra NUMERIC(12),

    FOREIGN KEY (ProveedorID) REFERENCES Proveedores(ProveedorID)
);

CREATE TABLE DetalleCompra (
    DetalleCompraID SERIAL PRIMARY KEY,
    CompraID INT NOT NULL,
    ProductoID INT NOT NULL,
    Cantidad INT NOT NULL DEFAULT 1,
    CostoUnitario NUMERIC(10) NOT NULL,

    FOREIGN KEY (CompraID) REFERENCES Compras(CompraID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID),
    CHECK (Cantidad > 0)
);

INSERT INTO Generos (Nombre) VALUES
('Disparos en primera persona'), -- ID: 1
('Disparos en tercera persona'), -- ID: 2
('Hack and slash'), -- ID: 3
('Arcade y ritmo'), -- ID: 4
('Juegos de plataforma y corredores'), -- ID: 5
('Matamarcianos'), -- ID: 6
('Lucha y artes marciales'), -- ID: 7
('Objetos ocultos'), -- ID: 8
('Casuales'), -- ID: 9
('Metroidvania'), -- ID: 10
('Puzles'), -- ID: 11
('Rol de aventuras'), -- ID: 12
('Novelas visuales'), -- ID: 13
('Buena trama'), -- ID: 14
('Rol y acción'), -- ID: 15
('Rol, táctica y estrategia'), -- ID: 16
('Rol japonés'), -- ID: 17
('Roguelikes y roguelites'), -- ID: 18
('Rol por turnos'), -- ID: 19
('En grupo'), -- ID: 20
('Simuladores de construcción y automatización'), -- ID: 21
('Simuladores de aficiones y trabajos'), -- ID: 22
('Simuladores de citas'), -- ID: 23
('Simuladores de agricultura y fabricación'), -- ID: 24
('Simuladores de espacio y vuelo'), -- ID: 25
('Simuladores de vida e inmersivos'), -- ID: 26
('Simuladores de sandbox y de física'), -- ID: 27
('Estrategia en tiempo real'), -- ID: 28
('Brutalismo'), -- ID: 29
('Defensa de torres'), -- ID: 30
('De cartas y tablero'), -- ID: 31
('Juegos de ciudades y asentamientos'), -- ID: 32
('Gran estrategia y 4X'), -- ID: 33
('Estrategia militar'), -- ID: 34
('Simulación'), -- ID: 35
('Carreras'), -- ID: 36
('Simulador de carreras'), -- ID: 37
('Pesca y caza'), -- ID: 38
('Deportes de equipo'), -- ID: 39
('Deportes individuales'), -- ID: 40
('Deportes'), -- ID: 41
('Terror'), -- ID: 42
('Ciencia ficción y ciberpunk'), -- ID: 43
('Espacio'), -- ID: 44
('Mundo abierto'), -- ID: 45
('Anime'), -- ID: 46
('Supervivencia'), -- ID: 47
('Detectives y misterio'), -- ID: 48
('Plataformas'), -- ID: 49
('Shooter'), -- ID: 50
('Party Game'); -- ID: 51

INSERT INTO Fabricantes (Fabricante) VALUES
('Magnavox'), -- ID: 1
('Atari'), -- ID: 2
('Mattel Electronics'), -- ID: 3
('Coleco'), -- ID: 4
('Nintendo'), -- ID: 5
('Sega'), -- ID: 6
('Sony'), -- ID: 7
('Microsoft'), -- ID: 8
('NEC'), -- ID: 9
('SNK'), -- ID: 10
('The 3DO Company'), -- ID: 11
('Nokia'), -- ID: 12
('Valve'), -- ID: 13
('Asus'), -- ID: 14
('Panic'); -- ID: 15

INSERT INTO Consolas (Nombre, FabricanteID) VALUES
-- Pioneras y Clásicas (Atari, Magnavox, etc.)
('Magnavox Odyssey', 1), -- ID: 1
('Atari 2600', 2), -- ID: 2
('Intellivision', 3), -- ID: 3
('ColecoVision', 4), -- ID: 4
('Atari 5200', 2), -- ID: 5
('Atari 7800', 2), -- ID: 6
('Atari Lynx', 2), -- ID: 7
('Atari Jaguar', 2), -- ID: 8

-- Nintendo (Sobremesa)
('Nintendo Entertainment System (NES)', 5), -- ID: 9
('Super Nintendo Entertainment System (SNES)', 5), -- ID: 10
('Nintendo 64', 5), -- ID: 11
('Nintendo GameCube', 5), -- ID: 12
('Wii', 5), -- ID: 13
('Wii U', 5), -- ID: 14
('Nintendo Switch', 5), -- ID: 15

-- Nintendo (Portátiles)
('Game & Watch', 5), -- ID: 16
('Game Boy', 5), -- ID: 17
('Game Boy Color', 5), -- ID: 18
('Virtual Boy', 5), -- ID: 19
('Game Boy Advance', 5), -- ID: 20
('Game Boy Advance SP', 5), -- ID: 21
('Nintendo DS', 5), -- ID: 22
('Nintendo DS Lite', 5), -- ID: 23
('Nintendo DSi', 5), -- ID: 24
('Nintendo 3DS', 5), -- ID: 25
('Nintendo 2DS', 5), -- ID: 26
('New Nintendo 3DS', 5), -- ID: 27
('Nintendo Switch Lite', 5), -- ID: 28

-- SEGA
('SG-1000', 6), -- ID: 29
('Sega Master System', 6), -- ID: 30
('Sega Genesis (Mega Drive)', 6), -- ID: 31
('Sega Game Gear', 6), -- ID: 32
('Sega CD', 6), -- ID: 33
('Sega 32X', 6), -- ID: 34
('Sega Saturn', 6), -- ID: 35
('Sega Dreamcast', 6), -- ID: 36

-- Sony (PlayStation)
('PlayStation (PS1)', 7), -- ID: 37
('PlayStation 2 (PS2)', 7), -- ID: 38
('PlayStation 3 (PS3)', 7), -- ID: 39
('PlayStation 4 (PS4)', 7), -- ID: 40
('PlayStation 5 (PS5)', 7), -- ID: 41

-- Sony (Portátiles)
('PlayStation Portable (PSP)', 7), -- ID: 42
('PlayStation Vita', 7), -- ID: 43

-- Microsoft (Xbox)
('Xbox', 8), -- ID: 44
('Xbox 360', 8), -- ID: 45
('Xbox One', 8), -- ID: 46
('Xbox Series S', 8), -- ID: 47
('Xbox Series X', 8), -- ID: 48

-- Otras (NEC, SNK, 3DO, etc.)
('TurboGrafx-16 (PC Engine)', 9), -- ID: 49
('Neo Geo AES', 10), -- ID: 50
('Neo Geo CD', 10), -- ID: 51
('Neo Geo Pocket', 10), -- ID: 52
('Neo Geo Pocket Color', 10), -- ID: 53
('3DO Interactive Multiplayer', 11), -- ID: 54
('N-Gage', 12), -- ID: 55

-- Modernas (PC Handhelds)
('Steam Deck', 13), -- ID: 56
('Asus ROG Ally', 14), -- ID: 57
('Playdate', 15); -- ID: 58

INSERT INTO Proveedores (NombreProveedor) VALUES
-- Gigantes y Propietarios de Plataformas
('Nintendo'),
('Sony Interactive Entertainment'),
('Microsoft (Xbox Game Studios)'),
('Valve Corporation'),
('Epic Games'),

-- Grandes Editoras (Publishers) Globales
('Electronic Arts (EA)'),
('Activision'),
('Blizzard Entertainment'),
('Ubisoft'),
('Take-Two Interactive'),
('Warner Bros. Games'),
('Disney Interactive'),
('505 Games'),

-- Grandes de Japón
('Square Enix'),
('Capcom'),
('Sega'),
('Bandai Namco Entertainment'),
('Konami'),
('Koei Tecmo'),
('Atlus'),
('FromSoftware'),

-- Importantes de Europa y América
('CD Projekt Red'),
('Paradox Interactive'),
('Focus Entertainment'),
('Embracer Group'),
('THQ Nordic'),
('Gearbox Software'),
('Larian Studios'),

-- Principales Desarrolladores (Developers)
('Rockstar Games'),
('Naughty Dog'),
('Insomniac Games'),
('Santa Monica Studio'),
('Bethesda Game Studios'),
('id Software'),
('BioWare'),
('Remedy Entertainment'),
('PlatinumGames'),
('Obsidian Entertainment'),
('Riot Games'),

-- Editoras de Nicho e Indie
('Devolver Digital'),
('Annapurna Interactive'),
('Team17'),
('Curve Games'),
('Raw Fury'),
('Private Division'),

-- Compañías Históricas (Algunas aún activas)
('Atari'),
('Midway Games'),
('LucasArts'),
('Sierra Entertainment'),
('Acclaim Entertainment'),
('Psygnosis'),
('SNK');

INSERT INTO Juegos (Titulo, GeneroID, ProveedorID, Clasificacion, Lanzamiento) VALUES
('Donkey Kong',4,1,NULL,1981),
('Donkey Kong Jr.',4,1,NULL,1982),
('Mario Bros.',4,1,NULL,1983),
('Punch-Out!!',7,1,NULL,1984),
('Super Mario Bros.',49,1,'E',1985),
('Duck Hunt',50,1,'E',1985),
('Excitebike', 36, 1, 'E', 1985),
('Ice Climber',49,1,'E',1985),
('Metroid', 10, 1, 'E', 1987),
('The Legend of Zelda', 12, 1, 'E', 1987),
('Mike Tyson''s Punch-Out!!',7,1,'E',1987),
('Super Mario Bros. 2',49,1,'E',1988),
('Zelda II: The Adventure of Link', 12, 1, 'E', 1988),
('Tetris', 11, 1, 'E', 1989),
('Super Mario Bros. 3',49,1,'E',1990),
('Dr. Mario', 11, 1, 'E', 1990),
('Super Mario World',49,1,'E',1991),
('F-Zero', 36, 1, 'E', 1991),
('Super Mario Kart', 36, 1, 'E', 1992),
('The Legend of Zelda: A Link to the Past', 12, 1, 'E', 1992),
('Kirby''s Dream Land',49,1,'E',1992),
('Star Fox',50,1,'E',1993),
('Super Metroid', 10, 1, 'E', 1994),
('Donkey Kong Country',49,1,'E',1994),
('Super Mario World 2: Yoshi''s Island',49,1,'E',1995),
('EarthBound', 17, 1, 'T', 1995),
('Super Mario 64',49,1,'E',1996),
('Wave Race 64', 36, 1, 'E', 1996),
('Mario Kart 64', 36, 1, 'E', 1997),
('Star Fox 64',50,1,'E',1997),
('The Legend of Zelda: Ocarina of Time', 12, 1, 'E', 1998),
('Pokémon Edición Roja', 17, 1, 'E', 1998),
('Mario Party', 51, 1, 'E', 1999),
('Super Smash Bros.',7,1,'E',1999),
('Pokémon Snap', 35, 1, 'E', 1999),
('Donkey Kong 64',49,1,'E',1999),
('The Legend of Zelda: Majora''s Mask', 12, 1, 'E', 2000),
('Paper Mario', 17, 1, 'E', 2001),
('Luigi''s Mansion', 12, 1, 'E', 2001),
('Super Smash Bros. Melee',7,1,'T',2001),
('Animal Crossing: Población: ¡en aumento!', 35, 1, 'E', 2002),
('Metroid Prime', 12, 1, 'T', 2002),
('Super Mario Sunshine',49,1,'E',2002),
('The Legend of Zelda: The Wind Waker', 12, 1, 'E', 2003),
('Mario Kart: Double Dash!!', 36, 1, 'E', 2003),
('Animal Crossing: Wild World', 35, 1, 'E', 2005),
('Nintendogs: Teckel y Compañía', 35, 1, 'E', 2005),
('The Legend of Zelda: Twilight Princess', 12, 1, 'T', 2006),
('Luigi''s Mansion 3', 12, 1, 'E', 2019),
('Pokémon Espada y Pokémon Escudo', 17, 1, 'E', 2019),
('Animal Crossing: New Horizons', 35, 1, 'E', 2020),
('Paper Mario: The Origami King', 17, 1, 'E', 2020),
('Hyrule Warriors: La era del Cataclismo', 3, 1, 'T', 2020),
('Super Mario 3D World + Bowser''s Fury', 49, 1, 'E', 2021),
('Metroid Dread', 10, 1, 'T', 2021),
('Mario Party Superstars', 51, 1, 'E', 2021);

INSERT INTO Productos (JuegoID, ConsolaID, Formato, Condicion, PrecioVenta, Stock, SKU, CostoAdquisicion) VALUES
(5, 9, 'Fisico', 'Usado', 15000, 3, 'NES-SMB-F-USD', 7000),
(17, 10, 'Fisico', 'Usado', 25000, 5, 'SNES-SMW-F-USD', 12000),
(27, 11, 'Fisico', 'Usado', 30000, 2, 'N64-SM64-F-USD', 15000),
(31, 11, 'Fisico', 'Usado', 35000, 4, 'N64-ZELDA-F-USD', 18000),
(40, 12, 'Fisico', 'Usado', 40000, 1, 'GCN-SSBM-F-USD', 22000),
(45, 13, 'Fisico', 'Usado', 45000, 2, 'WII-ZELDA-F-USD', 25000),
(48, 14, 'Fisico', 'Usado', 50000, 3, 'WIU-ACNH-F-USD', 30000),
(55, 15, 'Fisico', 'Usado', 60000, 1, 'NSW-MPSS-F-USD', 35000),

-- Physical Versions
(49, 15, 'Fisico', 'Nuevo', 49990, 15, 'NSW-LM3-F-NVO', 35000),
(51, 15, 'Fisico', 'Nuevo', 54990, 25, 'NSW-ACNH-F-NVO', 38000),
(54, 15, 'Fisico', 'Nuevo', 45000, 10, 'NSW-MDREAD-F-NVO', 30000),
(55, 15, 'Fisico', 'Nuevo', 49990, 12, 'NSW-MPSS-F-NVO', 35000),
(17, 10, 'Fisico', 'Nuevo', 25000, 8, 'SNES-SMW-F-NVO', 15000),
(27, 11, 'Fisico', 'Nuevo', 30000, 6, 'N64-SM64-F-NVO', 18000),
(31, 11, 'Fisico', 'Nuevo', 35000, 7, 'N64-ZELDA-F-NVO', 20000),
(40, 12, 'Fisico', 'Nuevo', 40000, 5, 'GCN-SSBM-F-NVO', 25000),
(45, 13, 'Fisico', 'Nuevo', 45000, 4, 'WII-ZELDA-F-NVO', 28000),
(1, 13, 'Fisico', 'Nuevo', 50000, 6, 'WIU-ACNH-F-NVO', 32000),

-- Digital Versions
(49, 15, 'Digital', 'Nuevo', 49990, 999, 'NSW-LM3-D-NVO', 34000),
(51, 15, 'Digital', 'Nuevo', 54990, 999, 'NSW-ACNH-D-NVO', 37000),
(54, 15, 'Digital', 'Nuevo', 45000, 999, 'NSW-MDREAD-D-NVO', 29000),
(55, 15, 'Digital', 'Nuevo', 49990, 999, 'NSW-MPSS-D-NVO', 34000);

INSERT INTO Clientes (Nombre, Apellido, Email, Telefono, FechaRegistro) VALUES
('Michelle', 'Ramírez', 'michelle.ramirez@mail.udp.cl', 900000001, '2024-01-15'),
('Samuel', 'Vasquez', 'Samuel.vasquez@mail.udp.cl', 900000002, '2024-03-22'),
('Alex', 'Bravo', 'alex.bravo@mail.udp.cl', 900000003, '2024-06-2'),
('Diego', 'Escobar', 'diego.escobar@mail.udp.cl', 900000004, '2024-08-10');