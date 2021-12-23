import pandas as pd
import sqlite3
import ast

columns = [f'Mise {i}' for i in range(1,6)] + [i for i in range(1,58)]
df = pd.DataFrame(columns = columns)

conn = sqlite3.connect("banco_de_dados.db")
cursor = conn.cursor()

cmd = "SELECT Mises from questionnaire_s8 ORDER BY ID ASC"
cursor.execute(cmd)

mises = cursor.fetchall()

cmd = "SELECT AF from questionnaire_s8 ORDER BY ID ASC"    
cursor.execute(cmd)

AFs = cursor.fetchall()

for i in range(len(mises)):

    disciplinas = ast.literal_eval(AFs[i][0])
    
    if len(disciplinas) < 57:
        missing = 57 - len(disciplinas)
        disciplinas += ['-' for i in range(missing)]
        
    row = pd.Series(ast.literal_eval(mises[i][0]) +  disciplinas, index=df.columns)   
    df = df.append(row, ignore_index=True)