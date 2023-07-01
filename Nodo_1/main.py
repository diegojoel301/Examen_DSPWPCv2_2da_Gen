from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
import jwt
import sqlite3
from datetime import datetime, timedelta
import random
import string
import pickle
import os
import base64

secret = "nherwbf6723gr26t7gffe2t6"

def generar_id_plato(longitud=8):
    caracteres = string.ascii_letters + string.digits
    id_plato = ''.join(random.choice(caracteres) for _ in range(longitud))
    return id_plato

def create_jwt_token(username: str, admin: bool) -> str:
    payload = {

        "sub": "4242",
        "username": username,
        "admin": admin,
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

app = FastAPI()
bearer_scheme = HTTPBearer()
@app.get("/hello/{name}")
async def hello(name):
    return f"Bienvenido a tu examen {name}"

@app.post("/users/login")
async def login(request: Request):
    data = await request.json()
    data = dict(data)

    if not "username" in data.keys():
        return {"Error": "No especificaste el username"}
    if not "password" in data.keys():
        return {"Error": "No especificaste el password"}
    
    username = data["username"]
    password = data["password"]
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    query = "SELECT admin FROM User WHERE username = ? AND password = ?"

    cursor.execute(query, (username, password))

    salida = cursor.fetchone()
    print(salida)
    if salida != list() and salida != None:
        return {"Login Exitoso": "Te logeaste exitosamente al sistema", "auth_token": create_jwt_token(username, salida[0])}
    return {"Error": "Usuario o Contrasenia erronea"}

@app.post("/users/register")
async def login(request: Request):
    data = await request.json()
    data = dict(data)

    admin = True

    if not "username" in data.keys():
        return {"Error": "No especificaste el username"}
    if not "password" in data.keys():
        return {"Error": "No especificaste el password"}
    if not "email" in data.keys():
        return {"Error": "No especificaste el email"}
    if not "admin" in data.keys():
        admin = False

    username = data["username"]
    password = data["password"]
    email = data["email"]

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    query = "SELECT * FROM User WHERE username = ?"

    cursor.execute(query, (username, ))

    salida = cursor.fetchone()
    
    if salida != list() and salida != None:
        return {"Error": "Ya existe el usuario"}
    else:
        query = "INSERT INTO User VALUES(?, ?, ?, ?)"
        cursor.execute(query, (username, password, email, admin))
        conn.commit()
        return {"Exito": "Se creo exitosamente el usuario"}

@app.put('/users/change_password/{username}')
async def change_password(request: Request, username, authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token = authorization.credentials
        
        jwt.decode(token, secret, algorithms=["HS256"])

        data = await request.json()
        data = dict(data)

        if not "password" in data.keys():
            return {"Error": "No especificaste el password"}
        
        password = data["password"]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        query = f"UPDATE User SET password = '{password}' WHERE username = '{username}'"
        cursor.execute(query)
        conn.commit()
        conn.close()

        return {"message": f"Contraseña cambiada para el usuario {username}"}
    except:
        return {"message": "error"}
        #raise HTTPException(status_code=401, detail="Token JWT inválido")

@app.get('/users')
async def list_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    query = f"SELECT username, email FROM User";
    cursor.execute(query)
    res = cursor.fetchall()
    conn.close()

    output = list()

    for row in res:
        username, email = row
        output.append({
            'username': username,
            'email': email
        })

    return output

@app.get('/platos')
async def list_platos():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    query = "SELECT cod_plato, nombre_plato, descripcion, costo FROM Plato;"
    cursor.execute(query)
    res = cursor.fetchall()
    print(res)
    output = list()

    for row in res:
        cod_plato, nombre_plato, descripcion, costo = row
        output.append({
            'cod_plato': cod_plato,
            'nombre_plato': nombre_plato,
            'descripcion': descripcion,
            'costo': costo
        })

    return output

@app.post('/platos/add')
async def add_platos(request: Request, authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token = authorization.credentials
        decode_jwt = jwt.decode(token, secret, algorithms=["HS256"])
        
        print(decode_jwt)

        if decode_jwt["admin"] == True:

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            data = await request.json()
            data = dict(data)

            if not "nombre_plato" in data.keys():
                return {"Error": "No especificaste el Nombre del plato"}
            if not "descripcion" in data.keys():
                return {"Error": "No especificaste el descripcion"}
            if not "costo" in data.keys():
                return {"Error": "No especificaste el costo"}

            cursor.execute("INSERT INTO Plato VALUES(?, ?, ?, ?)", (generar_id_plato(longitud=8), data["nombre_plato"], data["descripcion"], data["costo"]))
            conn.commit()
            conn.close()
            return {"message": "Adicion Exitosa!"}
        else:
            return {"message": "No eres administrador para agregar platos"}
    except:
        return {"message": "error"}
    
@app.delete('/platos/delete/{id_plato}')
async def delete_platos(id_plato, authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token = authorization.credentials
        decode_jwt = jwt.decode(token, secret, algorithms=["HS256"])
        
        print(decode_jwt)

        if decode_jwt["admin"] == True:

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Plato Where cod_plato = ?", (id_plato, ))

            res = cursor.fetchone()
            object_encoded = base64.b64encode(pickle.dumps(res))

            cursor.execute("DELETE FROM Plato WHERE cod_plato = ?", (id_plato, ))
            conn.commit()
            conn.close()
            #return {"message": "Eliminacion Exitosa!"}
            print(object_encoded)
            #return RedirectResponse(f"/platos/create_backup/{object_encoded}", status_code=301)
            #raise HTTPException(status_code=303, detail="See Other", headers={"Location": f"/platos/create_backup/{object_encoded}"})
            return RedirectResponse(f"/platos/create_backup/{object_encoded.decode('UTF-8')}", status_code=307)
        else:
            return {"message": "No eres administrador para eliminar platos"}
    except:
        return {"message": "error"}

@app.delete('/platos/create_backup/{object_encoded}')
async def platos_create_backup(object_encoded, authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token = authorization.credentials
        decode_jwt = jwt.decode(token, secret, algorithms=["HS256"])

        if decode_jwt["admin"] == True:

            file_backup = open(f'./backup/backup_{generar_id_plato()}', 'wb')
            file_backup.write(object_encoded.encode())
            file_backup.close()
            return {"message": "Eliminacion y Backup Exitoso!"}
        else:
            return {"message": "Solo el administrador puede crear un backup"}
    except:
        return {"message": "error"}

@app.get('/platos/backup')
async def platos_backup():
    objects_list = list()

    archivos = os.listdir('./backup/')

    for archivo in archivos:
        ruta_archivo = os.path.join('./backup/', archivo)

        with open(ruta_archivo, 'rb') as f:

            object_tupla = pickle.loads(base64.b64decode(f.readline()))
        
        objects_list.append({
            'cod_plato': object_tupla[0],
            'nombre_plato': object_tupla[1],
            'descripcion': object_tupla[2],
            'costo': object_tupla[3]
        })
        
    return objects_list

@app.get('/platos/backup/delete_all')
async def platos_backup_delete_all(authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token = authorization.credentials
        decode_jwt = jwt.decode(token, secret, algorithms=["HS256"])

        if decode_jwt["admin"] == True:
            carpeta = "./backup/"
            archivos = os.listdir(carpeta)

            for archivo in archivos:
                ruta_archivo = os.path.join(carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
            return {"message": "Eliminacion de Backup Exitoso!"}
        else:
            return {"message": "Solo el administrador puede eliminar el backup"}
    except:
        return {"message": "error"}
