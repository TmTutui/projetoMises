from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import re
import os
import json
import requests
import pandas as pd


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
        email_pos = re.search('[a-z|.|-]+@ecl[0-9][0-9].ec-(\n)*lyon.fr', pdf.text)
        end = email_pos.span()[-1]
        start = email_pos.span()[0]

        email = pdf.text[start:end]

        return email
        
    def get_mises(self):
        mises_label = ['Mise 1','Mise 2','Mise 3','Mise 4','Mise 5']
        mises_usuario = []
        
        for mise_text in mises_label:
            mise_value = ''

            index =  self.text.find(mise_text) + 9   
            char =  self.text[index]

            while (char != ' ' and char != '\n'):       
                mise_value += char
                index += 1
                char =  self.text[index]  

            if ',' in mise_value:                    
                mise_value = mise_value.replace(',','.')                                              
            mise_value = float(mise_value)

            mises_usuario.append(mise_value)
        
        return mises_usuario

    def get_subjects(self):
        pos1 = re.search('aléatoirement.', pdf.text)
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
        return subject_dict


def getTextOCR(file_path: str) -> str:
    """
        Use OCR API to return text of image in pdf file/format

        ## PARAMS:
            - file_path: string

        ## Returns:
            - result of API call in string
    """
    UserName =  'PETERBANANINHA005'
    LicenseCode = 'D360C2A3-0877-42BB-9C97-3B550933A647'

    # Extract text with English language by default
    RequestUrl = "http://www.ocrwebservice.com/restservices/processDocument?language=french&gettext=true&outputformat=txt"

    with open(file, 'rb') as image_file:
        image_data = image_file.read()
        
    r = requests.post(RequestUrl, data=image_data, auth=(UserName, LicenseCode))

    if r.status_code == 401:
        # Please provide valid username and license code
        print("Unauthorized request")
        exit()

    # Decode Output response
    jobj = json.loads(r.content)

    ocrError = str(jobj["ErrorMessage"])

    if ocrError != '':
            #Error occurs during recognition
            print ("Recognition Error: " + ocrError)
            exit()

    return str(jobj["OCRText"][0])


if __name__ == '__main__':
    os.chdir(os.getcwd() + '/pdfs')  # folder with all pdfs

    columns = ['Email'] +  [f'Mise {i}' for i in range(1,6)] + [i for i in range(1,58)]
    df = pd.DataFrame(columns = columns)

    for file in os.listdir(os.getcwd()):
        path = os.getcwd() + '/' + file
        pdf = PDF(path)

        if len(pdf.text) < 100:
            print('Using OCR API to read PDF')
            continue
            pdf.text = getTextOCR(path)

        print(file)
        email = pdf.get_email()
        mises = pdf.get_mises()
        subjects = [value for value in pdf.get_subjects().values()]

        if len(subjects) < 57:
            missing = 57 - len(subjects)
            subjects += ['-' for i in range(missing)]

        row = pd.Series([email] + mises +  subjects, index=df.columns)
        df = df.append(row, ignore_index=True)
