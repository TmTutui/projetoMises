from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import re
import shutil,os
from os.path import isfile,join
import pytesseract 
import pdf2image
import pickle
from bdd import BDD

pytesseract.pytesseract.tesseract_cmd = r'C:/Users/Tiago/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

class PDF():
    def __init__(self,file_path):
        self.path = file_path
        self.bdd = BDD()  
        self.flag_OCR = False
        #Tentativa de leitura convencional
        self.text = self.convert_pdf_to_txt(self.path)   
        
        #Caso haja falha na leitura, tentativa por OCR e levanta a flag
        if len(self.text) < 100:
            self.flag_OCR = True            
            self.text =self.convert_pdf_to_txt_OCR(self.path)
            self.text = '\n'.join(self.text)
          
    def enviar_dados_para_BDD(self):
        
        mises = str(self.read_mises())
        email = self.read_email()
        AF,flag_error,disciplina_error = self.read_subjects()
        
        ID = self.bdd.adicionar_dados(email, mises, str(AF))
        
        if flag_error:
            s = "\n[!] Problema com o código da AF '" + str(disciplina_error) 
            s += "' do arquivo " + str(self.path) + ' de ID ' + str(ID) 
            print(s)
        
        if self.flag_OCR:     
            s = '\nChecar os dados de ' + str(self.path) + ' de ID ' + str(ID)
            print(s)
            shutil.copy(self.path, 'pdfs\Problemáticos')
        
    
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
            
    def convert_pdf_to_txt_OCR(self,path): 
        pages = pdf2image.convert_from_path(pdf_path=path, poppler_path='poppler-21.11.0/Library/bin',dpi=200)
        content = []     
            
        for page in pages:
            content.append(pytesseract.image_to_string(page, lang='fra')) 
            
        return content

    def read_email(self): 
        email = re.search('[a-z|.|-]+@ecl[0-9][0-9].ec-(\n)*lyon.fr', self.text)    
        return email.group(0)            
                           
    def read_mises(self):          
        def convert_mises_in_lt_values(lt_mises):
            mises_values = []
            for mise in lt_mises:
                aux_mises = mise[mise.index(':')+1:]
                
                if "," in aux_mises:
                    aux_mises = aux_mises.replace(',','.') 
                
                mises_values.append(float(aux_mises))
            
            return mises_values            
        
        mises = re.findall('Mise [1-5] : [0-9]+[,|.]*[0-9]*', self.text)    
        
        return convert_mises_in_lt_values(mises)
                        
    def read_subjects(self):            
        pos1 = re.search('aléatoirement.', self.text)
        text_choices = pdf.text[pos1.span()[-1]:]

        separator = ' '
        if '\xa0\xa0\xa0' in text_choices:
            separator = '\xa0'

        tst_list = []
        subject_dict = {}
        all_selected = True  # did the person select all subjects? 

        for i in range(1,57):
            try:
                init = re.search(f'{separator}{i} - ', text_choices).span()[0]  # init of subject
            except:
                separator = '\n'
                init = re.search(f'{separator}{i} - ', text_choices).span()[0]  # init of subject
            try: 
                end = re.search(f'{separator}{i+1} - ', text_choices).span()[0]  # end of subject
            except:
                all_selected = False
                break  # if the person has not put all

            subject = text_choices[init : end]
            subject = subject.split('https')[0].replace('\n', '').strip()  # remove zimbra link and line breaks
            tst_list.append(subject)

            subject_dict[i] = subject.split(f'{i} - ', 1)[1]

        if all_selected:
            i += 1

        subject = text_choices[end:].split('https', 1)[0]# .replace('\n', '').split('\n', 1)[0].strip()
        tst_list.append(subject)
        subject_dict[i] = subject.split(f'{i} - ')[1].split('\n', 1)[0].replace('\n', '').strip()
        
        return self.convert_subjects_in_keys(subject_dict)

    def convert_subjects_in_keys(self,d):            
        def get_key(val,my_dict):
            for key, value in my_dict.items():
                 if val == value:
                     return key
        flag_error = False    
        disciplina_error = []
        
        file = open("Dicionario.pkl", "rb")
        dicionario = pickle.load(file)                  
      
        for key,value in d.items():
            pos = re.search(' - [A-Z]-', value)
            disciplina = value[:pos.span()[-1]-5]
            
            codigo = get_key(disciplina,dicionario)
            
            if codigo == None:
                flag_error = True
                disciplina_error.append(disciplina)
                
            d[key] = codigo
                
        return list(d.values()),flag_error,disciplina_error

if __name__ == '__main__':                       

    files = [f for f in os.listdir('pdfs') if isfile(join('pdfs', f))]
    
    for file in files:        
        path =  'pdfs/' + file    
        pdf = PDF(path)
        pdf.enviar_dados_para_BDD()
        
        
               

    
    
     