from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

class PDF():
    def __init__(self,file_path):
        self.path = file_path      
        self.text = self.convert_pdf_to_txt(self.path)
    
    def convert_pdf_to_txt(self,path, pages=None):
        if not pages:
            pagenums = set()
        else:
            pagenums = set(pages)
        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)
    
        infile = open(path, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()
        output.close()
        return text

    def get_email(self):                
        email = []
                    
        index =  self.text.find('Zimbra') + 16
        char =  self.text[index]    
      
        while char != '\n':               
            char =  self.text[index]    
            email.append(char)
            index += 1 
    
        return ''.join(email)
        
    def get_mises(self):
        mises_label = ['Mise 1','Mise 2','Mise 3','Mise 4','Mise 5']
        mise_value = []
        
        for mise in mises_label:
            
            index =  self.text.find(mise) + 8    
            char =  self.text[index]    
            
            while char != '\n':     
                index += 1 
                char =  self.text[index]    
                mise_value.append(char)
                
        mises_usuario = []
        aux_mise = []
         
        for i in mise_value:
            if i == '\n':                          
                mise = ''.join(aux_mise)  
                if ',' in aux_mise:                    
                    mise = mise.replace(',','.')                                              
                mise = float(mise)
                mises_usuario.append(mise)
                aux_mise = []
                continue
            
            aux_mise.append(i)
        
        return mises_usuario
    
if __name__ == '__main__':
    
    pdf = PDF('S8_Questionarios\QuestionarioHelena.pdf')
    #mises = pdf.get_mises()
    pdf.get_email()
    


      
    
       