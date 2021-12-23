import sqlite3

class BDD():
    def __init__(self,file='banco_de_dados.db'):
        self.base = file
        self.conn = sqlite3.connect(self.base)
        self.cursor = self.conn.cursor()
        
    def adicionar_dados(self,email,mises,AF):        
           
        cmd = "SELECT ID FROM questionnaire_s8 WHERE email='{}'".format(email)
        self.cursor.execute(cmd)
        
        ID = self.cursor.fetchone()
        
        if ID == None:          
            cmd = "INSERT INTO questionnaire_s8(Email,Mises,AF) VALUES(?,?,?)"
            self.cursor.execute(cmd,(email,mises,AF))
            ID = self.cursor.lastrowid
            self.conn.commit()   
            
            return ID[0]
        else:
            s = 'Email '+str(email)+' já cadastrado com a ID ' + str(ID[0])
            print(s)            
            
            return ID[0]
    
if __name__ == '__main__':
    
    bdd = BDD()
    bdd.adicionar_dados('Player1','[1,2,3]','teste')
    
        

        
