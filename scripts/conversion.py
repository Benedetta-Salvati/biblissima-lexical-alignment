## script de conversion des fichiers annotés en TL/Cattex en UD

import pandas as pd
import os
import sys
import csv
from bs4 import BeautifulSoup
import re

tabConvert = pd.read_csv("../alignementReferentiels/bonnesVersions/conversionCattexUD-POS.tsv", sep="\t")
tabConvert

tabAnnotation = pd.read_csv("../OF3C-main/tsv/LemmaPos/Chrestien_Erec3_posBFM_aligne.tsv", sep="\t",quoting=csv.QUOTE_NONE)

nom = os.path.basename("Chrestien_Erec3_posBFM_aligne.tsv").split('.tsv')[0]

tabAnnotationBase = tabAnnotation[["form", "POS", "lemma"]]
tabAnnotationBase

tabAnnotationBase["UD-POS"] = tabAnnotationBase["POS"]
tabAnnotationBase["UD-feats"] = None
tabAnnotationBase['lemma-DMF'] = None

"""
##POS
for x in tabAnnotationBase.index:
    print(x)
    POS = tabAnnotationBase["POS"][x]
    print(POS)
    #if list(tabConvert[tabConvert.isin([POS])].stack())[0]:
    if not(tabConvert[tabConvert.isin([POS])].stack().empty):
        idx = tabConvert[tabConvert.isin([POS])].stack().index[0][0]
        POSUD = tabConvert["UD-pos"][idx]
        print(POSUD)
        featsUD = tabConvert["UD-feats"][idx]
        tabAnnotationBase["UD-POS"][x] = POSUD
        tabAnnotationBase["UD-feats"][x] = featsUD
    else :
            tabAnnotationBase["UD-POS"][x] = 'pas de catégorie définie'
            print('not found')
"""

## lemma
with open('../DMF_DICT_2024-05-29/DICT_2024-05-29-corr.xml', 'r', encoding = "ISO-8859-1") as f:
    data = f.read()

bs_data = BeautifulSoup(data, 'xml')

art = bs_data.find_all('ART')

df_lemmes = pd.DataFrame(columns=['TL', 'DMF', 'GD', 'GDC', 'AND', 'DECT'])

# production du tableau d'équivalence des lemmes à partir du XML
for i in art:
    
    GD_list = []
    TL_list = []
    GDC_list = []
    DECT_list = []
    AND_list = []
    
    if i.find_all('TL') or i.find_all('GD') or i.find_all('GDC') or i.find_all('AND') or i.find_all('DECT'):

        if i.find_all('LEM'):
            for k in i.find_all('LEM'):
                DMF_elem = k.get_text()
        else:
            DMF_elem = ''

        if i.find_all('TL.RENVOI'):
            TL_elem = ''.join( [l.get_text() for l in i.find_all('TL.RENVOI')])
            TL_list.append(TL_elem)
        elif i.find_all('TL'):
            for j in i.find_all('TL'):
                #print(j)
                if j.find_all('SLEMME'):
                    for l in j.find_all('SLEMME'):
                    #TL_elem = ''.join([sl.get_text() for sl in j.find_all('SLEMME')])
                        TL_elem = l.get_text()
                        #print(TL_elem)
                        TL_list.append(TL_elem)
                elif j.find_all('SLEMMEVSPE'):
                    for l in j.find_all('SLEMMEVSPE'):
                    #TL_elem = ''.join([sl.get_text() for sl in j.find_all('SLEMME')])
                        TL_elem = l.get_text()
                                                #print(TL_elem)
                        TL_list.append(TL_elem)
                else:
                    #TL_elem = ''.join([l.get_text() for l in i.find_all('TL')])
                    for l in j.find_all('LEMME'):
                        TL_elem = l.get_text()
                        TL_list.append(TL_elem) 
        else:
            TL_elem = ''

        if i.find_all('GD'):
            for j in i.find_all('GD'):
                for l in j.find_all('LEMME'):
                    GD_elem = l.get_text()
                    GD_list.append(GD_elem)
        else:
            GD_elem = ''
            
        if i.find_all('GDC'):
            #GDC_elem = ''.join([l.get_text() for l in i.find_all('GDC')])
            for j in i.find_all('GDC'):
                for l in j.find_all('LEMME'):
                    GDC_elem = l.get_text()
                    GDC_list.append(GDC_elem)
        else:
        	            GDC_elem = ''
            
        if i.find_all('AND'):
            #AND_elem = ''.join([l.get_text() for l in i.find_all('AND')])
            for j in i.find_all('AND'):
                for l in j.find_all('LEMME'):
                    AND_elem = l.get_text()
                    AND_list.append(AND_elem)
                for l in j.find_all('LEMMEAND'):
                    AND_elem = l.get_text()
                    AND_list.append(AND_elem)
        else:
            AND_elem = ''
            
        if i.find_all('DECT'):
            #DECT_elem = ''.join([l.get_text() for l in i.find_all('DECT')])
            for j in i.find_all('DECT'):
                for l in j.find_all('LEMME'):
                    DECT_elem = l.get_text()
                    DECT_list.append(DECT_elem)
        else:
            DECT_elem = ''
            
        if (len(GD_list) == 1 or GD_elem == '') and (len(GDC_list) == 1 or GDC_elem == '') and (len(TL_list) == 1 or TL_elem == '') and (len(AND_list) == 1 or AND_elem == '') and (len(DECT_list) == 1 or DECT_elem == '') :
            equiv = {'TL' : TL_elem, 'DMF' : DMF_elem, 'GD' : GD_elem, 'GDC' : GDC_elem, 'AND' : AND_elem, 'DECT' : DECT_elem}
            df_lemmes.loc[len(df_lemmes)] = equiv
            
        else :
            if len(GD_list) > 1:
                for i in range(len(GD_list)):
                    print(i)
                    GD_elem = GD_list[i]
                    #print(GD_elem)
                    equiv = {'TL' : TL_elem, 'DMF' : DMF_elem, 'GD' : GD_elem, 'GDC' : GDC_elem, 'AND' : AND_elem, 'DECT' : DECT_elem}
                    df_lemmes.loc[len(df_lemmes)] = equiv
                    
            if len(GDC_list) > 1:
                for i in range(len(GDC_list)):
                    print(i)
                    GDC_elem = GDC_list[i]
                    #print(GDC_elem)
                    equiv = {'TL' : TL_elem, 'DMF' : DMF_elem, 'GD' : GD_elem, 'GDC' : GDC_elem, 'AND' : AND_elem, 'DECT' : DECT_elem}
                    df_lemmes.loc[len(df_lemmes)] = equiv

            if len(TL_list) > 1:
                for i in range(len(TL_list)):
                    #print(i)
                    TL_elem = TL_list[i]
                    #print(TL_elem)
                    equiv = {'TL' : TL_elem, 'DMF' : DMF_elem, 'GD' : GD_elem, 'GDC' : GDC_elem, 'AND' : AND_elem, 'DECT' : DECT_elem}
                    df_lemmes.loc[len(df_lemmes)] = equiv

            if len(AND_list) > 1:
                for i in range(len(AND_list)):
                    #print(i)
                    AND_elem = AND_list[i]
                    #print(AND_elem)
                    equiv = {'TL' : TL_elem, 'DMF' : DMF_elem, 'GD' : GD_elem, 'GDC' : GDC_elem, 'AND' : AND_elem, 'DECT' : DECT_elem}
                    df_lemmes.loc[len(df_lemmes)] = equiv
                    
            if len(DECT_list) > 1:
                for i in range(len(DECT_list)):
                    #print(i)
                    DECT_elem = DECT_list[i]
                    #print(DECT_elem)
                    equiv = {'TL' : TL_elem, 'DMF' : DMF_elem, 'GD' : GD_elem, 'GDC' : GDC_elem, 'AND' : AND_elem, 'DECT' : DECT_elem}
                    df_lemmes.loc[len(df_lemmes)] = equiv

        
        
    else:
        pass


df_lemmes.to_csv(r'../data_df_lemmes.tsv', sep='\t', encoding='utf-8', header='true')