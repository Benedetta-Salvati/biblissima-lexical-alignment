#!usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import sys
import csv

def read_csv(file):
    tabAnnotation = pd.read_csv(file, sep="\t", quoting=csv.QUOTE_NONE)
    print(tabAnnotation)
    return tabAnnotation
    

if __name__ == '__main__':
    tabAnnotation = read_csv(sys.argv[1])
    nom = os.path.basename(sys.argv[1]).split('.tsv')[0]
    tabConvert = pd.read_csv("../alignementReferentiels/bonnesVersions/conversionCattexUD.tsv", sep="\t")
    tabAnnotationBase = tabAnnotation[["form", "POS", "lemma"]]
    tabAnnotationBase["UD-POS"] = tabAnnotationBase["POS"]
    tabAnnotationBase["UD-feats"] = None
    for x in tabAnnotationBase.index:
    #print(x)
        POS = tabAnnotationBase["POS"][x]
        for y in tabConvert.index:        
            if POS == tabConvert["Cattex2009"][y]:
                POSUD = tabConvert["UD-pos"][y]
                featsUD = tabConvert["UD-feats"][y]
                tabAnnotationBase["UD-POS"][x] = POSUD
                tabAnnotationBase["UD-feats"][x] = featsUD
    tabAnnotationBase.to_csv(r'./'+nom+'-UD.csv', sep='\t', encoding='utf-8', header='true')
