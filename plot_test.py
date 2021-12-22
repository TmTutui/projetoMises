#%%
from typing import KeysView
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pylab import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages
import pickle
import sqlite3
import ast
# Create your connection.


file = open("Dicionario.pkl", "rb")
dicionario = pickle.load(file)

#%%
cnx = sqlite3.connect('banco_de_dados.db')
df = pd.read_sql_query("SELECT * FROM questionnaire_s8", cnx)
#df = pd.read_csv('basedados.csv')



#%%
dict_AF = {}
for user in df['ID']: #Mudar o 9 aqui para a quantidade de dados
    aux = ast.literal_eval(df['AF'][user-1]) #
    for position in range(len(aux)):
        if aux[position] in dict_AF:
            dict_AF[aux[position]].append(position+1)
        else: 
            dict_AF[aux[position]]=[position+1]
        #dict_AF[df.iloc[student,position]] =  [position]
keys = []
for key, value in dict_AF.items():
    keys.append(key)
    
#%% PLot e save dos histogramas das materias

with PdfPages('histogramas.pdf') as pdf:
    for materia in keys:
        #commutes = pd.Series(dict_AF[materia])
        plt.figure(figsize=(17,10))
        loc, labels = plt.yticks()
        locx, labelsx = plt.xticks()
        plt.yticks(np.arange(0, max(loc), step=1))
        #commutes.plot.hist(grid=True, bins=57, rwidth=0.9,color='#607c8e', align = 'mid')
        plt.xticks(np.arange(1, 57, step=1))
        plt.hist(dict_AF[materia], bins=57, align = 'left')
        #ya = axes.get_yaxis()
        #ya.set_major_locator(MaxNLocator(integer=True))
        plt.title(dicionario[materia], fontsize= 20)
        plt.xlabel('Position', fontsize= 20)
        plt.ylabel('Quantité de personnes', fontsize= 20)
        plt.grid(axis='y', alpha=0.75)
        pdf.savefig()

# %%
