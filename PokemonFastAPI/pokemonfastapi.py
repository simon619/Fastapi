from fastapi import FastAPI, Path, HTTPException, status
from typing import Optional
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
import random


db = mysql.connector.connect(host="localhost", user="root", password="pwroot", database="PokemonDB")
mycursor = db.cursor()

app = FastAPI()

class PokemonClass(BaseModel):
    name: str
    pk_type: str
    fast_move: str
    charged_move: str
    weight_in_kg: float

class TrainerClass(BaseModel):
    trainer_name: str
    age: int
    team: str

class PokemonUpdate(BaseModel):
    name: Optional[str] = None
    pk_type: Optional[str] = None
    fast_move: Optional[str] = None
    charged_move: Optional[str] = None
    weight_in_kg: Optional[float] = None

class TrainerUpdate(BaseModel):
    trainer_name: Optional[str] = None
    age: Optional[int] = None
    team: Optional[str] = None
    pk_id: Optional[int] = None
        
def pk_result(pk_list):
    result = {}
    for i in range(len(pk_list)):
        result[pk_list[i][5]] = [pk_list[i][1], pk_list[i][2], pk_list[i][3], pk_list[i][4], pk_list[i][6]]
    return result

def tr_result(tr_list):
    result = {}
    for i in range(len(tr_list)):
        result[tr_list[i][3]] = [tr_list[i][0], tr_list[i][1], tr_list[i][2], tr_list[i][4]]
    return result

@app.get("/get-all-pokemons")
def all_pokemons():
    mycursor.execute("SELECT * FROM pokemon")
    pk_info = mycursor.fetchall()
    result = pk_result(pk_info)
    return result

@app.get("/get-all-trainers")
def all_trainers():
    mycursor.execute("SELECT * FROM trainer")
    tr_info = mycursor.fetchall()
    result = tr_result(tr_info)
    return result

@app.get("/get-pokemon-by-name")
def by_pokemon_name(name: str = Path(None, description="Name A Pokemon")):
    mycursor.execute("SELECT * FROM pokemon WHERE name = %s", (name,))
    pk_info = mycursor.fetchall()
    result = pk_result(pk_info)
    return result

@app.get("/get-trainer-by-name")
def by_trainer_name(name: str = Path(None, description="Name A Trainer")):
    mycursor.execute("SELECT * FROM trainer WHERE trainer_name = %s", (name,))
    tr_info = mycursor.fetchall()
    result = tr_result(tr_info)
    return result

@app.get("/get-pokemon-by-info")
def by_pokemon_name_and_id(*, name: Optional[str] = None, id = int):
    if name and id:
        result = {}
        mycursor.execute("SELECT * FROM pokemon WHERE name = %s AND id = %s", (name, id))
        pk_info = mycursor.fetchall()
        result[pk_info[0][5]] = [pk_info[0][0], pk_info[0][1], pk_info[0][2], pk_info[0][3], pk_info[0][4], pk_info[0][6]]
        return result

    elif not name:
        mycursor.execute("SELECT * FROM pokemon WHERE id = %s", (id,))
        pk_info = mycursor.fetchall()
        result = pk_result(pk_info)
        return result

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@app.get("/get-trainer-by-info")
def by_trainer_name_and_id(*, name: Optional[str] = None, id = int):
    if name and id:
        result = {}
        mycursor.execute("SELECT * FROM trainer WHERE trainer_name = %s AND tainer_id = %s", (name, id))
        tr_info = mycursor.fetchall()
        result[tr_info[0][3]] = [tr_info[0][0], tr_info[0][1], tr_info[0][2], tr_info[0][4]]
        return result

    elif not name:
        mycursor.execute("SELECT * FROM pokemon WHERE tainer_id = %s", (id,))
        tr_info = mycursor.fetchall()
        result = tr_result(tr_info)
        return result

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@app.post("/insert-pokemon")
def insert_a_pokemon(pk: PokemonClass):
    mycursor.execute("INSERT INTO pokemon (name, type, fast_move, charged_move, created, weight_in_kg) VALUES (%s, %s, %s, %s, %s, %s)", (pk.name, pk.pk_type, pk.fast_move, pk.charged_move, datetime.now(), pk.weight_in_kg))
    db.commit()

    result = {}
    mycursor.execute("SELECT * FROM pokemon WHERE id = (SELECT COUNT(id) FROM pokemon)")
    pk_info = mycursor.fetchall()
    result[pk_info[0][5]] = [pk_info[0][0], pk_info[0][1], pk_info[0][2], pk_info[0][3], pk_info[0][4], pk_info[0][6]]
    return result

@app.post("/insert-trainer")
def insert_a_trainer(tr: TrainerClass):
    mycursor.execute("SELECT COUNT(id) FROM pokemon")
    temp = mycursor.fetchall()
    number_of_pokemons = temp[0][0]

    mycursor.execute("INSERT INTO trainer (trainer_name, age, team, pk_id) VALUES (%s, %s, %s, %s)", (tr.trainer_name, tr.age, tr.team, random.randint(1, number_of_pokemons + 1)))
    db.commit()

    result = {}
    mycursor.execute("SELECT * FROM trainer WHERE tainer_id = (SELECT COUNT(tainer_id) FROM trainer)")
    tr_info = mycursor.fetchall()
    result[tr_info[0][3]] = [tr_info[0][0], tr_info[0][1], tr_info[0][2], tr_info[0][4]]
    return result

@app.put("/update-pokemon/{id}")
def update_a_pokemon(id: int, pk: PokemonUpdate):
    mycursor.execute("SELECT EXISTS(SELECT * FROM pokemon WHERE id = %s)", (id,))
    pk_info = mycursor.fetchall()
    if pk_info[0][0]:
        if pk.name != None:
            mycursor.execute("UPDATE pokemon SET name = %s WHERE id = %s", (pk.name, id))
        
        if pk.pk_type != None:
            mycursor.execute("UPDATE pokemon SET type = %s WHERE id = %s", (pk.pk_type, id))
        
        if pk.fast_move != None:
            mycursor.execute("UPDATE pokemon SET fast_move = %s WHERE id = %s", (pk.fast_move, id))
        
        if pk.charged_move != None:
            mycursor.execute("UPDATE pokemon SET charged_move = %s WHERE id = %s", (pk.charged_move, id))
        
        if pk.weight_in_kg != None:
            mycursor.execute("UPDATE pokemon SET weight_in_kg = %s WHERE id = %s", (pk.weight_in_kg, id))
        db.commit()
        
        result = {}
        mycursor.execute("SELECT * FROM pokemon WHERE id = %s", (id,))
        pk_info = mycursor.fetchall()
        result[pk_info[0][5]] = [pk_info[0][0], pk_info[0][1], pk_info[0][2], pk_info[0][3], pk_info[0][4], pk_info[0][6]]
        return result
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.put("/update-trainer/{id}")
def update_a_trainer(id: int, tr: TrainerUpdate):
    mycursor.execute("SELECT EXISTS(SELECT * FROM trainer WHERE tainer_id = %s)", (id,))
    tr_info = mycursor.fetchall()
    if tr_info[0][0]:
        if tr.trainer_name != None:
            mycursor.execute("UPDATE trainer SET trainer_name = %s WHERE tainer_id = %s", (tr.trainer_name, id))

        if tr.age != None:
            mycursor.execute("UPDATE trainer SET age = %s WHERE tainer_id = %s", (tr.age, id))
        
        if tr.team != None:
            mycursor.execute("UPDATE trainer SET team = %s WHERE tainer_id = %s", (tr.team, id))
        
        if tr.pk_id != None:
            mycursor.execute("SELECT COUNT(id) FROM pokemon")
            temp = mycursor.fetchall()
            number_of_pokemons = temp[0][0]
            if not 0 < int(tr.pk_id) < number_of_pokemons + 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            else:
                mycursor.execute("UPDATE trainer SET pk_id = %s WHERE tainer_id = %s", (tr.pk_id, id))
        db.commit()

        result = {}
        mycursor.execute("SELECT * FROM trainer WHERE tainer_id = %s", (id,))
        tr_info = mycursor.fetchall()
        result[tr_info[0][3]] = [tr_info[0][0], tr_info[0][1], tr_info[0][2], tr_info[0][4]]
        return result

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
@app.delete("/delete-trainer")
def delete_a_trainer(id: int):
    mycursor.execute("SELECT EXISTS(SELECT * FROM trainer WHERE tainer_id = %s)", (id,))
    pk_info = mycursor.fetchall()
    if pk_info[0][0]:
        mycursor.execute("DELETE FROM trainer WHERE tainer_id = %s", (id,))
        db.commit()
        return {'Data': 'Data Has Been Deleted'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)