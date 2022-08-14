import fitz
# used for extracting Text from Images
import pytesseract
import glob
# import re
import os
# used for image processing and loading
from PIL import Image
import re
from dateutil import parser
import csv
from tqdm import tqdm


#pytesseract.pytesseract.tesseract_cmd =r'C:/Program Files/Tesseract-OCR/tesseract.exe'


class PDF_PARSER():
    # Category 1: Provided Methods
    def __init__(self, pth):
        self.pth = pth+'/'
        self.main()
    def load_files(self, path):
        # make a list of all pdf files in given path
        return glob.glob(path + "/*.pdf")
    
    def GET_TEXT(self, path):
        doc = fitz.open(path)
        for i in range(doc.page_count):
            if not os.path.exists('Reports'):
                os.mkdir('Reports')
            # loading pdf page by page
            page = doc.load_page(i)
            # convert each page to pixel amp
            pix = page.get_pixmap()
            output = 'Reports'+'/'+ str(i)+'.png'
            # save image to images directory by image name
            pix.save(output)
        Text = []
        filelist = os.listdir('Reports/')
        filelist = sorted(filelist,key=lambda x: int(os.path.splitext(x)[0])) 
        for Pth in filelist:
            pth = 'Reports'+'/'+Pth
            img = Image.open(pth)
            new_size = tuple(4*x for x in img.size)
            img = img.resize(new_size, Image.ANTIALIAS)
            # d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='deu')
            text = pytesseract.image_to_string(img, lang='deu', config='--psm 4 --psm 6')
            if 'Lage:' in text:     
                s = text.partition('Lage:')
                st ='Lage:' + s[2]
                for e in st.rsplit('\n')[:-2]:
                    Text.append(e)
            else:
                s = text.partition('Bodenschätzung')[2]
                for e in s.rsplit('\n')[:-2]:
                    Text.append(e)
        return Text
    
    def check_date(self, s):
        date_ = ''    
        try:
            res = parser.parse(s, fuzzy=True)
            return res
        except:
            return date_
    
    
    def TEXT_CLEAN(self, path):
        Text = self.GET_TEXT(path)
        DIC = {}
        if Text != []:
            Text = [e for e in Text if e!= '']  
            Text_str = ',, '.join(Text)
            Text_lst = Text_str.split('Lage:')
            for str_ in Text_lst:
                LAGE_EIG = str_.partition(', ')
                LAGE = LAGE_EIG[0]
                LAGE = LAGE.replace(',', '')
                LAGE = LAGE.replace('.', '')
                LAGE = LAGE.replace('|ee|', '')
                EIG  = LAGE_EIG[2] 
                EIG_LST = ''
                if 'Eigentümer:' in EIG:
                    EIG = EIG.partition('Eigentümer:')[2]
                    EIG_LST = EIG.split('Eigentümer')
                    DIC.update({LAGE: EIG_LST})
                elif 'Eigentümer.' in EIG:
                    EIG = EIG.partition('Eigentümer.')[2]
                    EIG_LST = EIG.split('Eigentümer')
                    DIC.update({LAGE: EIG_LST})
                  
            dic = {}
            for L,E in zip(DIC.keys(), DIC.values()):
                EIG = []
                for e in E:
                    if 'Buchung' in e:
                        if e.partition('Buchung')[0].startswith(' '):
                            EIG.append(e.partition('Buchung')[0].lstrip())
                        elif e.partition('Buchung')[0].startswith(': '):
                            EIG.append(e.partition('Buchung')[0].replace(': ', ''))
                        elif e.partition('Buchung')[0].startswith('. '):
                            EIG.append(e.partition('Buchung')[0].replace('. ', ''))
                    else:
                        if e.startswith(' '):
                            EIG.append(e.lstrip())
                        elif e.startswith(': '):
                            EIG.append(e.replace(': ', ''))
                        elif e.startswith('. '):
                            EIG.append(e.replace('. ', ''))
                eig = []
                for E in EIG:
                     D1 = E[0]
                     pat = ', '+D1
                     st = E[1:].split(pat)
                     for s in st:
                         if s.startswith('.'):
                             eig.append(s[2:])
                         else:
                             eig.append(s[1:])
                dic.update({L:eig}) 
        return dic
    
    def GET_INFO(self, path): 
       DIC = self.TEXT_CLEAN(path)
       dic = []
       try:    
           for keys, vals in zip(DIC.keys(), DIC.values()):
               for v in vals:
                   V = v.split(',,')
                   if len(V) > 2:
                       for e, add in enumerate(V):
                           result = re.findall(r'(\d{5})',add)
                           if result != []:
                               address = V[e-1].lstrip()
                               post_code, city = re.split(' ', V[e][V[e].index(result[0]):], 1)
                               V = [s for s in V[:e-1] if self.check_date(s) == '']
                               if V != []:
                                   FN = ''
                                   SN = ''
                                   comp = ''
                                   if len(V) == 1:
                                       if ', ' in V[0]:
                                           FN, SN = re.split(', ', V[0], 1)
                                       else:
                                           regex = re.compile('[@_!#$%^&*()<>?/\|}{~:.]') 
                                           
                                           # Pass the string in search  
                                           # method of regex object.     
                                           if(regex.search(V[0]) == None):
                                               comp = V[0]
                                           else:
                                               comp = ''
                                   elif len(V) > 1:
                                       for el in V:
                                           if ', ' in el:
                                               FN, SN = re.split(', ', el, 1)
                                           else:
                                               regex = re.compile('[@_!#$%^&*()<>?/\|}{~:.]') 
                                               
                                               # Pass the string in search  
                                               # method of regex object.     
                                               if(regex.search(el) == None):
                                                   comp = el
                                               else:
                                                   comp = ''
                                   d = [keys, comp, FN, SN, address, post_code, city]
                                   dic.append(d)
                               else:
                                   d = [keys, '', '', '', address, post_code, city]
                                   dic.append(d)
           return dic
       except:
           return dic                           
    def main(self):
        hdr = ['House', 'Firma', 'Eigentümer Vorname', 'Eigentümer Nachname', 'Adresse', 'Postleitzahl', 'Stadt']
        path = self.pth
        dir_ = self.load_files(path)
        with open('Result.csv', 'w', newline = '') as output_csv:
            # initialize rows writer
            csv_writer = csv.writer(output_csv)
            # write headers to the file
            csv_writer.writerow(hdr)
            for PTH in tqdm(dir_):
                os.system('rm -rf Reports/*')
                Data = self.GET_INFO(PTH)
                if Data != []:
                    csv_writer.writerows(Data)
        return
                
   
    

    
    
   
    
