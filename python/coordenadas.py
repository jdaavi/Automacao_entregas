import requests
from geopy.distance import geodesic
import numpy as np
import tkinter as tk
from tkinter import messagebox
import psycopg2


def conectar_banco():
    try:
        conexao = psycopg2.connect (
            host = 'datalake_menu.postgresql.dbaas.com.br',
            database = 'datalake_menu',
            user = 'datalake_menu',
            password = 'Acesso1!'
        )
        return conexao
    except Exception as e:
        print(f'Erro ao conectar ao banco: {e}')
        return None

def obter_ditancia_banco(endereco1, endereco2):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            query = """SELECT distancia FROM distancias WHERE endereco1 = %s AND endereco2 = %s"""
            cursor.execute(query, (endereco1, endereco2))
            conexao.commit()
        except Exception as e:
            print(f"Erro ao registrar no banco: {e}")
        finally:
            conexao.close()

def registrar_distancia_banco(endereco1, endereco2, distancia):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            # Inserindo a distância no banco
            query = """INSERT INTO distancias (endereco1, endereco2, distancia) VALUES (%s, %s, %s)"""
            cursor.execute(query, (endereco1, endereco2, distancia))
            conexao.commit()
        except Exception as e:
            print(f"Erro ao registrar no banco: {e}")
        finally:
            conexao.close()
        

def obter_coordenadas(endereco):
    url = f"https://nominatim.openstreetmap.org/search?q={endereco}&format=json"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    dados = response.json()
    
    if dados:
        return float(dados[0]['lat']), float(dados[0]['lon'])
    else:
        return None

def calcular_distancia(endereco1, endereco2):
    coordenadas1 = obter_coordenadas(endereco1)
    coordenadas2 = obter_coordenadas(endereco2)
    
    if coordenadas1 and coordenadas2:
        distancia = geodesic(coordenadas1, coordenadas2).kilometers
        return np.round(distancia, 2)
    else:
        return None

def classificar_area(distancia):
    areas_de_entrega = {
        "A": (0, 0.99),
        "B": (1, 1.99),
        "C": (2, 2.99),
        "D": (3, 3.99),
        "E": (4, 4.99),
        "F": (5, 5.99),
        "G": (6, 6.99),
        "H": (7, 7.99),
        "I": (8, 8.99),
        "J": (9, 9.99),
        "K": (10, 10.99),
    }
    
    for area, (min_km, max_km) in areas_de_entrega.items():
        if min_km <= distancia < max_km:
            return area
    
    return "Fora da área de entrega"

def calcular():
    endereco1 = entrada_partida.get()
    endereco2 = entrada_chegada.get()
    
    distancia = obter_ditancia_banco(endereco1, endereco2)

    if distancia is None:
        distancia = calcular_distancia(endereco1, endereco2)
        if distancia is None:
            registrar_distancia_banco(endereco1, endereco2, distancia)
        else:
            messagebox.showerror("Erro","Não foi possível obter a distãncia.")
            return
        


# Criando a interface gráfica
root = tk.Tk()
root.title("Áreas de entrega")
root.geometry("400x250")
root.configure(bg="#f0f0f0")

frame = tk.Frame(root, padx=10, pady=10, bg="#ffffff", relief=tk.RIDGE, borderwidth=3)
frame.pack(pady=20, padx=20)

tk.Label(frame, text="Endereço de Partida:", bg="#ffffff", font=("Arial", 10, "bold")).pack()
entrada_partida = tk.Entry(frame, width=50, relief=tk.GROOVE, borderwidth=2)
entrada_partida.pack(pady=5)

tk.Label(frame, text="Endereço de Chegada:", bg="#ffffff", font=("Arial", 10, "bold")).pack()
entrada_chegada = tk.Entry(frame, width=50, relief=tk.GROOVE, borderwidth=2)
entrada_chegada.pack(pady=5)

tk.Button(frame, text="Calcular", command=calcular, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", relief=tk.RAISED).pack(pady=10)

resultado = tk.StringVar()
tk.Label(frame, textvariable=resultado, font=("Arial", 12, "bold"), fg="blue", bg="#ffffff").pack()

root.mainloop()

