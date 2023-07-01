CREATE TABLE User(
    username VARCHAR(50),
    password VARCHAR(50),
    email VARCHAR(50),
    admin INTEGER,
    PRIMARY KEY(username)
);

CREATE TABLE Plato(
    cod_plato VARCHAR(50),
    nombre_plato VARCHAR(50),
    descripcion VARCHAR(255),
    costo INTEGER,
    PRIMARY KEY(cod_plato)
);

INSERT INTO Plato VALUES ('plt1', 'Pasta a la Carbonada', 'Fideo con carne', 200);
INSERT INTO Plato VALUES ('plt2', 'Tacos al Pastor', 'Tacos con carne de cerdo', 50);
INSERT INTO Plato VALUES ('plt3', 'Totopos', 'Trozos de tortilla de maiz', 50);
INSERT INTO Plato VALUES ('plt4', 'Tamales', 'Masa de maiz rellena de alguna carne', 60);
INSERT INTO User VALUES ('admin', 'ashfewbfvwhefew', 'admin@dspwpcv2.local', 1)