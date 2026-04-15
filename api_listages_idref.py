#!/usr/bin/env python
# coding: utf-8

# Listages des autorités IdRef SLSP : Pablo Iriarte, UNIGE, 2024 et 2025
# Dernière modification : 23.03.2026
import requests
import datetime
from lxml import etree
import xml.etree.ElementTree as ET
import os
import io
import re
import unicodedata
import sys

# Code RCR de votre instituion sur IdRef
# UNIGE : 
# mon_rcr = '991401102'
mon_rcr = 'votre_rcr_ici'

# email pour l'envoi des notifications de recap
email_recap = 'votre_email_ici@votre_institution.ch'
emailbodytxt = ''

print(' ')
print('*******************************************************')
print(' ')
print('Début du processus : ' + str(datetime.datetime.now()))

# date du jour-1
today = datetime.datetime.now() 
yesterday = today - datetime.timedelta(days = 1) 
madate1 = yesterday.strftime('%Y-%m-%d')
madate2 = yesterday.strftime('%Y%m%d')

# fichiers OK et erreur
myfilein_ok = 'xml/results/ok/' + madate2 + '.txt'
myfilein_error = 'xml/results/errors/' + madate2 + '.txt'

# test du fichier OK pour la deuxième tentative
tentative = 1
if os.path.isfile(myfilein_ok):
    # fichier OK trouvé : pas besoin de refaire l'import
    print('Fichier OK trouvé pour ' + madate2)
    print('Fin du processus : ' + str(datetime.datetime.now()))
    sys.exit()
else:
    # fichier OK pas trouvé : on continue
    # test du fichier d'erreur pour savoir si on est à la première ou 2ème tentative
    if os.path.isfile(myfilein_error):
        # fichier d'erreur existe
        tentative = 2
    else:
        # pas de fichier d'erreur -> on enregistre un
        with io.open(myfilein_error, 'w', encoding='utf8') as f:
            f.write('Fichier temporaire - import idRef du ' + madate1)
        f.close() 

print('Tentative : ' + str(tentative))
# Imports
# print('Date : ' + madate1)
headers = {'accept': 'application/xml'}
myfilein_c = 'xml/results/creations/' + madate2 + '.xml'
myfilein_m = 'xml/results/modifications/' + madate2 + '.xml'

# export du fichier des créations
mytimeout = 60
try:
    idref_c = requests.get('https://www.idref.fr/Sru/Solr?wt=xml&version=2.2&start=&rows=1000&indent=on&fl=ppn_z,dateetat_dt&q=rcrcre_z:' + mon_rcr + '+AND+dateetat_dt:[' + madate1 + 'T00:00:00Z%20TO%20' + madate1 + 'T23:59:59Z]', headers=headers, timeout=mytimeout)
except idref_c.Timeout as err:
    print('Req créations | ERREUR : TIMEOUT')
else:           
    if (idref_c.status_code == 200):
        print('Req créations OK')
        with io.open(myfilein_c, 'w', encoding='utf8') as f:
            f.write(idref_c.text)
        f.close() 

# export du fichier des modifs
try:
    idref_m = requests.get('https://www.idref.fr/Sru/Solr?wt=xml&version=2.2&start=&rows=1000&indent=on&fl=ppn_z,datemod_z&q=rcrmod_z:' + mon_rcr + '+AND+datemod_z:' + madate2 + '*', headers=headers, timeout=mytimeout)
except idref_m.Timeout as err:
    print('Req modifications | ERREUR : TIMEOUT')
else:
    if (idref_m.status_code == 200):
        print('Req modifications OK')
        with io.open(myfilein_m, 'w', encoding='utf8') as f:
            f.write(idref_m.text) 
        f.close()

# parsing des réponses et extraction des IDs
ids_all_c = []
ids_all_m = []
ids_all_e = []

# Parse XML
root_c = etree.parse(myfilein_c)
root_m = etree.parse(myfilein_m)

# valeurs initiales
results_c = 0
results_m = 0
results_e = 0
import_erreur = ''

# extraction des ids
results_c_found = root_c.find("./result").attrib['numFound']
results_m_found = root_m.find("./result").attrib['numFound']

# ajout des ids
# créations
for i in range(len(root_c.findall("./result/doc"))):
    i = i + 1
    # print(i)
    if len(root_c.findall("./result/doc")) == 1 :
        ids_all_c.append(root_c.find("./result/doc/str[@name='ppn_z']").text)
    else :
        ids_all_c.append(root_c.find("./result/doc[" + str(i) + "]/str[@name='ppn_z']").text)
# modifs
for j in range(len(root_m.findall("./result/doc"))):
    j = j + 1
    if len(root_m.findall("./result/doc")) == 1 :
        ids_all_m.append(root_m.find("./result/doc/str[@name='ppn_z']").text)
    else :
        ids_all_m.append(root_m.find("./result/doc[" + str(j) + "]/str[@name='ppn_z']").text)    

# ids_all : ajout des deux listes
ids_all = ids_all_c + ids_all_m
seen = set()
uniq = []

for x in ids_all:
    if x not in seen:
        uniq.append(x)
        seen.add(x)
# print('IDs uniques : ' + str(len(uniq)))
# print('IDs doublons : ' + str(len(ids_all) - len(uniq)))

# boucle pour les ids
if len(uniq) > 0 :
    for idrefid in uniq :
        # print(idrefid)
        myfileout_c = 'xml/records/creations/' + madate2 + '_' + idrefid + '.xml'
        myfileout_m = 'xml/records/modifications/' + madate2 + '_' + idrefid + '.xml'
        url = 'https://www.idref.fr/' + idrefid + '.xml'
        try:
            idrefxml = requests.get(url, headers=headers, timeout=mytimeout)
        except requests.Timeout as err:
            print(idrefid + ' | ERREUR 1 : TIMEOUT')
            ids_all_e.append(idrefid)
        else:           
            if (idrefxml.status_code == 200):
                root = ET.fromstring(idrefxml.text)
                # test de la 004 pour séparer les notices créés
                if (root.find("./controlfield[@tag='004']").text == madate2) :
                    # print (x['#text'] + ' : date OK')
                    # date OK: export du fichier des créations
                    results_c = results_c + 1
                    with io.open(myfileout_c, 'w', encoding='utf8') as f:
                        f.write(idrefxml.text) 
                    f.close()
                else :
                    results_m = results_m + 1
                    # export du fichier des modifs
                    with io.open(myfileout_m, 'w', encoding='utf8') as f:
                        f.write(idrefxml.text) 
                    f.close()
            else :
                print(idrefid + ' | ERREUR 1 : REQUEST STATUS ' + str(idrefxml.status_code))
    
    # boucle pour rattraper les erreurs
    for idrefid2 in ids_all_e :
        # print(idrefid2)
        myfileout_c = 'xml/records/creations/' + madate2 + '_' + idrefid2 + '.xml'
        myfileout_m = 'xml/records/modifications/' + madate2 + '_' + idrefid2 + '.xml'
        url = 'https://www.idref.fr/' + idrefid2 + '.xml'
        try:
            idrefxml = requests.get(url, headers=headers, timeout=mytimeout)
        except requests.Timeout as err:
            print(idrefid2 + ' | ERREUR 2 : TIMEOUT')
            results_e = results_e + 1
            import_erreur = import_erreur + '    - ' + idrefid2 + '\n'
        else:           
            if (idrefxml.status_code == 200):
                print(idrefid2 + ' | Rattrapage : OK')
                root = ET.fromstring(idrefxml.text)
                # test de la 004 pour séparer les notices créés
                if (root.find("./controlfield[@tag='004']").text == madate2) :
                    # print (x['#text'] + ' : date OK')
                    # date OK: export du fichier des créations
                    results_c = results_c + 1
                    with io.open(myfileout_c, 'w', encoding='utf8') as f:
                        f.write(idrefxml.text) 
                    f.close()
                else :
                    results_m = results_m + 1
                    # export du fichier des modifs
                    with io.open(myfileout_m, 'w', encoding='utf8') as f:
                        f.write(idrefxml.text) 
                    f.close()
            else :
                print(idrefid2 + ' | ERREUR 2 : REQUEST STATUS ' + str(idrefxml.status_code))
                results_e = results_e + 1
                import_erreur = import_erreur + '    - ' + idrefid2 + '\n'


# Tests sur tous les champs 
def test1(texte, myzone):
    # parenthèses (U+0028 et U+0029) ()
    erreur1 = ''
    if (('(' in texte) & (')' not in texte)) :
        erreur1 = erreur1 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de ( différent du nombre de ) [TEST#AA]\n'
        texte = texte.replace('(', '£S£(£E£')
    if ((')' in texte) & ('(' not in texte)) :
        erreur1 = erreur1 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de ( différent du nombre de ) [TEST#AB]\n'
        texte = texte.replace(')', '£S£)£E£')
    if ((erreur1 == '') & (texte.count('(') != texte.count(')'))):
        erreur1 = erreur1 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de ( différent du nombre de ) [TEST#AC]\n'
        texte = texte.replace('(', '£S£(£E£')
        texte = texte.replace(')', '£S£)£E£')
    
    # crochets (005B et 005D) []
    erreur2 = ''
    if (('[' in texte) & (']' not in texte)) :
        erreur2 = erreur2 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de [ différent du nombre de ] [TEST#AD]\n'
        texte = texte.replace('[', '£S£[£E£')
    if ((']' in texte) & ('[' not in texte)) :
        erreur2 = erreur2 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de [ différent du nombre de ] [TEST#AE]\n'
        texte = texte.replace(']', '£S£]£E£')
    if ((erreur2 == '') & (texte.count('[') != texte.count(']'))):
        erreur2 = erreur2 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de [ différent du nombre de ] [TEST#AF]\n'
        texte = texte.replace('[', '£S£[£E£')
        texte = texte.replace(']', '£S£]£E£')
    
    # guillemet (0022) ""
    erreur3 = ''
    if (texte.count('"') % 2 != 0):
        erreur3 = erreur3 + 'Champ ' + myzone + ' - Test sur les caractères: nombre de " impair [TEST#AG]\n'
        texte = texte.replace('"', '£S£"£E£')
        
    # Caractères illégaux invisibles
    # (0009) tabulation
    erreur4 = ''
    if ('	' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (0009) tabulation [TEST#AH]\n'
        texte = texte.replace('	', '£S£&nbsp;&nbsp;£E£')
    # (200E) marque gauche à droite
    if (u'\u200E' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (200E) marque gauche à droite [TEST#AI]\n'
        texte = texte.replace(u'\u200E', '£S£&nbsp;&nbsp;£E£')
    # (200F) marque droite à gauche
    if (u'\u200F' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (200F) marque droite à gauche [TEST#AJ]\n'
        texte = texte.replace(u'\u200F', '£S£&nbsp;&nbsp;£E£')
    # (202A) bloc gauche à droite
    if (u'\u202A' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (202A) bloc gauche à droite [TEST#AK]\n'
        texte = texte.replace(u'\u202A', '£S£&nbsp;&nbsp;£E£')
    # (202B) bloc droite à gauche
    if (u'\u202B' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (202B) bloc droite à gauche [TEST#AL]\n'
        texte = texte.replace(u'\u202B', '£S£&nbsp;&nbsp;£E£')
    # (202C) marque PDF
    if (u'\u202C' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (202C) marque PDF [TEST#AM]\n'
        texte = texte.replace(u'\u202C', '£S£&nbsp;&nbsp;£E£')
    # (0098) Start Of String
    if (u'\u0098' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (0098) marque début de chaîne [TEST#AN]\n'
        texte = texte.replace(u'\u202C', '£S£&nbsp;&nbsp;£E£')
    # (009C) String Terminator
    if (u'\u009C' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères invisibles: Merci de supprimer (009C) marque fin de chaîne [TEST#AO]\n'
        texte = texte.replace(u'\u202C', '£S£&nbsp;&nbsp;£E£')
    
    # Caractères illégaux à remplacer: , ,  (2014) tiret cadratin
    # (2019) apostrophe
    if (u'\u2019' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères illégaux: Merci de remplacer l\'apostrophe ’ par la touche correspondante du clavier [TEST#AP]\n'
        texte = texte.replace(u'\u2019', u'£S£\u2019£E£')
    # (2026) point de suspension
    if (u'\u2026' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères illégaux: Merci de remplacer le point de suspension … par la touche correspondante du clavier [TEST#AQ]\n'
        texte = texte.replace(u'\u2026', u'£S£\u2026£E£')
    # (2013) tiret demi-cadratin
    if (u'\u2013' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères illégaux: Merci de remplacer le tiret demi-cadratin – par la touche correspondante du clavier [TEST#AR]\n'
        texte = texte.replace(u'\u2013', u'£S£\u2013£E£')
    # (2014) tiret cadratin
    if (u'\u2014' in texte) :
        erreur4 = erreur4 + 'Champ ' + myzone + ' - Caractères illégaux: Merci de remplacer le tiret cadratin — par la touche correspondante du clavier [TEST#AS]\n'
        texte = texte.replace(u'\u2014', u'£S£\u2014£E£')
        
    # espaces en trop au début et à la fin sauf pour la 103
    erreur5 = ''
    if (myzone != '103'):
        if (texte.endswith(' ')):
            erreur5 = erreur5 + 'Champ ' + myzone + ': Merci de supprimer l\'espace à la fin du champ [TEST#AT]\n'
            texte = texte + '£S£&nbsp;£E£'
        if (texte.startswith(' ')):
            erreur5 = erreur5 + 'Champ ' + myzone + ': Merci de supprimer l\'espace au début du champ [TEST#AU]\n'
            texte = '£S£&nbsp;£E£' + texte
    # double espace sauf pour la zone 100 et 103
    if ((myzone != '100') & (myzone != '103')):
        if ('  ' in texte):
            erreur5 = erreur5 + 'Champ ' + myzone + ': Merci de corriger l\'espace à double [TEST#AV]\n'
            texte = texte.replace('  ', '£S£&nbsp;&nbsp;£E£')
    # espace avant la virgule
    if (' ,' in texte):
        erreur5 = erreur5 + 'Champ ' + myzone + ': Merci de corriger l\'espace avant la virgule [TEST#AW]\n'
        texte = texte.replace(' ,', '£S£&nbsp;,£E£')
        
    # doubles << >>
    erreur6 = ''
    if ('<<' in texte):
        erreur6 = erreur6 + 'Champ ' + myzone + ': Merci de supprimer les << [TEST#AX]\n'
        texte = texte.replace('<<', '£S£<<£E£')
    if ('>>' in texte):
        erreur6 = erreur6 + 'Champ ' + myzone + ': Merci de supprimer les >> [TEST#AY]\n'
        texte = texte.replace('>>', '£S£>>£E£')
        
        
        
    # concat errors
    erreur_all = erreur1 + erreur2 + erreur3 + erreur4 + erreur5 + erreur6
    return texte, erreur_all


# In[5]:


# Tests sur la 035
def test035(fmy035_a, fmy035_2):
    erreur035 = ''
    match = re.match(r'A[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$', fmy035_a)
    if match is None:
        # pas d'ID RERO -> $2 ne doit pas être RERO
        if (fmy035_2 == 'RERO'):
            erreur035 = erreur035 + 'Champ 035: Le champ n\'a pas le bon format $a A[9 chiffres] $2 RERO [TEST#EJ]\n'
        # test de "RERO" en $a
        if (fmy035_a == 'RERO'):
            erreur035 = erreur035 + 'Champ 035: Le champ n\'a pas le bon format $a A[9 chiffres] $2 RERO [TEST#EJ]\n'
    else:
        # $a correspond à un ID RERO -> $2 doit être "RERO"
        if (fmy035_2 != 'RERO'):
            erreur035 = erreur035 + 'Champ 035: Le champ n\'a pas le bon format $a A[9 chiffres] $2 RERO [TEST#EJ]\n'
    # end
    return erreur035


# In[6]:


# Tests sur la 103
def test103(texte):
    erreur103 = ''
    # le XML ajoute un espace avant le ? à supprimer
    texte = texte.replace(' ?', '?')
    # Ne contient que des chiffres ou des X (19XX ou 198X $a et/ou $b) 
    # Champ 103: Merci de corriger en X majuscule
    if ('x' in texte):
        erreur103 = erreur103 + 'Champ 103: Merci de corriger en X majuscule [TEST#AZ]\n'
    # Pas de tiret, pas de point mais ? est correct ($a et/ou $b)
    # tiret au début pour les dates avant JC admis
    # Champ 103: Il ne doit pas y avoir de ponctuation
    if ('.' in texte):
        erreur103 = erreur103 + 'Champ 103: Si on ne connaît pas la date précise, on remplace les chiffres par des X [TEST#BA]\n'
    if (texte[0] == '-'):
        texte2 = texte[1:]
    else:
        texte2 = texte
    if ('-' in texte2):
        erreur103 = erreur103 + 'Champ 103: Si on ne connaît pas la date précise, on remplace les chiffres par des X [TEST#BA]\n'
    match = re.match(r'( )?([0-9X\?\-]+( )?)$', texte)
    if match is None:
        erreur103 = erreur103 + 'Champ 103: seulement chiffres, X ou ? admis [TEST#BB]\n'
    # Une date complète s'indique AAAAMMJJ
    # Champ 103: Date à vérifier, le mois ne peut aller au-delà de 12, le jour au-delà de 31
    match2 = re.match(r'([1-2][0-9][0-9][0-9][0-9][0-9][0-9][0-9])$', texte)
    if match2 is not None:
        myyear = int(texte[0:4])
        mymonth = int(texte[4:6])
        myday = int(texte[6:8])
        if ((mymonth > 12) | (myday > 31)):
            erreur103 = erreur103 + 'Champ 103: Date à vérifier, le mois ne peut aller au-delà de 12, le jour au-delà de 31 [TEST#BC]\n'
    if (erreur103 != ''):
        texte = '££S££' + texte + '££E££'
    # end
    return texte, erreur103


# In[7]:


# Tests sur la 200
def test200(texte, mysubfieldcode200, fmy200_1, fmy200_2, fnb_200a, fnb_200b, fmy103a, fmy103b, fmy200_fs):
    erreur200 = ''
    fmy103a = fmy103a.strip()
    fmy103b = fmy103b.strip()
    # Si deuxième indicateur 1 il faut $a et $b
    if ((mysubfieldcode200 == 'a') & (fmy200_2 == '1') & (fnb_200b == 0)):
        erreur200 = erreur200 + 'Champ 200: Il manque le sous-champ $b prénom ou corriger « Nom entré au prénom ou dans l\'ordre direct » [TEST#BD]\n'
    # Si deuxième indicateur 0 il n’y a que $a
    if ((mysubfieldcode200 == 'b') & (fmy200_2 == '0') & (fnb_200b > 0)):
        erreur200 = erreur200 + 'Champ 200: Seul le sous-champ $a est autorisé ou corriger « Nom entré au patronyme » [TEST#BE]\n'
    # 200 $a ne doit pas y avoir de virgule
    if ((mysubfieldcode200 == 'a') & (',' in texte)):
        erreur200 = erreur200 + 'Champ 200: Le sous-champ $a ne doit pas contenir de virgule [TEST#BF]\n'
    # 200$b prénom : selon les règles Idref, mettre un espace entre les initiales 
    if (mysubfieldcode200 == 'b'):
        match1 = re.match(r'.*[\S]\.[\S]\.', texte)
        if match1 is not None:
            erreur200 = erreur200 + 'Champ 200: Merci de rajouter un espace entre les initiales [TEST#BG]\n'
        # 200$b prénom : Point après une initiale 
        match2 = re.match(r'.*[A-Z]$', texte)
        if match2 is not None:
            erreur200 = erreur200 + 'Champ 200: Une initiale doit se terminer par un point [TEST#BH]\n'
        # 200$b On me met pas d’espace entre des initiales séparées par un –
        match3 = re.match(r'.*[A-Z]\. - [A-Z]\.', texte)
        if match3 is not None:
            erreur200 = erreur200 + 'Champ 200: Merci de supprimer l\'espace en trop entre l\'initiale et le tiret [TEST#BI]\n'
        # 200$b le sous champ $b ne doit pas contenir de virgule
        if (',' in texte):
            erreur200 = erreur200 + 'Champ 200: le sous champ $b ne doit pas contenir de virgule [TEST#BJ]\n'
    # 200$c qualificatif : minuscule en début de champ
    if (mysubfieldcode200 == 'c'):
        match4 = re.match(r'^( )?[A-Z].*', texte)
        if match4 is not None:
            erreur200 = erreur200 + 'Champ 200: Le sous-champ $c doit généralement commencer par une minuscule [TEST#BK]\n'
    # 200 $f pas d'espace avant et après le tiret
    if (mysubfieldcode200 == 'f'):
        # Si le sous-champ $f est différent dans les 200  
        if (len(fmy200_fs) > 1 & len(set(fmy200_fs)) > 1):
            erreur200 = erreur200 + 'Champ 200: Le sous-champ $f doit être identique sur les différents champs 200 [TEST#EI]\n'
        if (' - ' in texte):
            erreur200 = erreur200 + 'Champ 200: Il ne doit pas y avoir d\'espace avant et après le tiret dans le sous-champ $f [TEST#BL]\n'
        # Si champ 103 19XX sous-champ $f 19..-…. 
        if ((fmy103a == '19XX') & (fmy103b == '') & (texte != '19..-....')):
            erreur200 = erreur200 + 'Champ 200: Le sous-champ $f doit être 19..-.... Ne pas tenir compte du message si la date est incertaine et qu\'il y a un point d\'interrogation en $f [TEST#BM]\n'
        # Si le sous-champ $f 19..-…., champ 103 doit être 19XX  
        if ((fmy103a != '19XX') & (texte == '19..')):
            erreur200 = erreur200 + 'Champ 103:  Le champ 103 doit être 19XX [TEST#BN]\n'
        # Si le champ 103 $a et $b, le sous-champ $f 1924-1994
        fmy103a2 = fmy103a.replace(' ?', '?')
        fmy103a2 = fmy103a2.replace('X', '.')
        fmy103b2 = fmy103b.replace(' ?', '?')
        fmy103b2 = fmy103b2.replace('X', '.')
        if (fmy103b == ''):
            fmy103b2 = '....'
        if ((texte != (fmy103a2 + '-' + fmy103b2)) & (texte != (fmy103a2[0:4] + '-' + fmy103b2[0:4])) & (texte != (fmy103a2[0:4] + '-' + fmy103b2)) & (texte != (fmy103a2 + '-' + fmy103b2[0:4]))):
            erreur200 = erreur200 + 'Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa, ou il manque en $f .... (4 points) Ne pas tenir compte du message si la date est incertaine et qu\'il y a un point d\'interrogation en $f [TEST#BQ]\n'
        # else:
            # Si champ 103 1987, le sous-champ $f 1987-…. (si 103 = 4 chiffres, sous-champ $f = 4 chiffres-….) 
            # Si le champ 103 1933? ou 1933 ?, sous-champ $f 1933?-….
            # match5 = re.match(r'[1-2][0-9][0-9][0-9]\?', fmy103a)
            # match5a = re.match(r'[1-2][0-9][0-9][0-9] \?', fmy103a)
            # if (((match5 is not None) | (match5a is not None)) & (fmy103b == '') & (texte != (fmy103a + '-....'))):
            #     erreur200 = erreur200 + 'Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa [TEST#BO]\n'      
            # elif ((match5 is not None) | (match5a is not None)) & (fmy103b != '') & (texte != (fmy103a[0:4] + '?-' + fmy103b[0:4]))):
            #     erreur200 = erreur200 + 'Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa [TEST#BO]\n'
            # Si le champ 103 a plus que l'année, ex 19980211
            # match5b = re.match(r'[1-2][0-9][0-9][0-9]+$', fmy103a)
            # if ((match5b is not None) & (fmy103b == '') & (texte != (fmy103a[0:4] + '-....'))):
            #     erreur200 = erreur200 + 'Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa [TEST#BP]\n'
            # elif ((match5b is not None) & (fmy103b != '') & (texte != (fmy103a[0:4] + '-' + fmy103b[0:4]))):
            #     erreur200 = erreur200 + 'Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa [TEST#BP]\n'
    # 200 $a, $b, $c et $f : Le champ ne doit pas contenir de parenthèses
    if ((mysubfieldcode200 == 'a') | (mysubfieldcode200 == 'b') | (mysubfieldcode200 == 'c') | (mysubfieldcode200 == 'f')):
        if (('(' in texte) | (')' in texte)):
            erreur200 = erreur200 + 'Champ 200: Le sous-champ $' + mysubfieldcode200 + ' ne doit pas contenir de parenthèses [TEST#EL]\n'
    # end
    if (erreur200 != ''):
        texte = '££S££' + texte + '££E££'
    return texte, erreur200


# In[8]:


# Tests sur la 400
def test400(texte, mysubfieldcode400, fmy400_1, fmy400_2, fnb_400a, fnb_400b, fmy103a, fmy103b):
    erreur400 = ''
    fmy103a = fmy103a.strip()
    fmy103b = fmy103b.strip()
    # Si deuxième indicateur 1 il faut $a et $b
    # if ((mysubfieldcode400 == 'a') & (fmy400_2 == '1') & (fnb_400b == 0)):
    #    erreur400 = erreur400 + 'Champ 400: Il manque le sous-champ $b prénom ou corriger « Nom entré au prénom ou dans l\'ordre direct »\n'
    # Si deuxième indicateur 0 il n’y a que $a
    # if ((mysubfieldcode400 == 'b') & (fmy400_2 == '0') & (fnb_400b > 0)):
    #    erreur400 = erreur400 + 'Champ 400: Seul le sous-champ $a est autorisé ou corriger « Nom entré au patronyme »\n'
    # 400 $a ne doit pas y avoir de virgule
    if ((mysubfieldcode400 == 'a') & (',' in texte)):
        erreur400 = erreur400 + 'Champ 400: Le sous-champ $a ne doit pas contenir de virgule [TEST#BT]\n'
    # 400$b prénom : selon les règles Idref, mettre un espace entre les initiales 
    if (mysubfieldcode400 == 'b'):
        match1 = re.match(r'.*[A-Z]\.[A-Z]\.', texte)
        if match1 is not None:
            erreur400 = erreur400 + 'Champ 400: Merci de rajouter un espace entre les initiales [TEST#BU]\n'
        # 400$b prénom : Point après une initiale 
        match2 = re.match(r'.*[A-Z]$', texte)
        if match2 is not None:
            erreur400 = erreur400 + 'Champ 400:  Une initiale doit se terminer par un point [TEST#BV]\n'
        # 400$b On me met pas d’espace entre des initiales séparées par un –
        match3 = re.match(r'.*[A-Z]\. - [A-Z]\.', texte)
        if match3 is not None:
            erreur400 = erreur400 + 'Champ 400: Merci de supprimer l\'espace en trop entre l\'initiale et le tiret [TEST#BW]\n'
        # 400$b le sous champ $b ne doit pas contenir de virgule
        if (',' in texte):
            erreur400 = erreur400 + 'Champ 400: le sous champ $b ne doit pas contenir de virgule [TEST#BX]\n'
    # 400$c qualificatif : minuscule en début de champ
    if (mysubfieldcode400 == 'c'):
        erreur400 = erreur400 + 'Champ 400: La forme rejetée ne contient généralement pas de qualificatif (sous-champ $c) [TEST#BY]\n'
        match4 = re.match(r'^( )?[A-Z].*', texte)
        if match4 is not None:
            erreur400 = erreur400 + 'Champ 400: Le sous-champ $c doit généralement commencer par une minuscule [TEST#BZ]\n'
    # 400 $f Pas de sous-champs $f
    if (mysubfieldcode400 == 'f'):
        erreur400 = erreur400 + 'Champ 400: La forme rejetée ne doit pas contenir de dates de vie (sous-champ $f) [TEST#CA]\n'
    # 400 $a, $b, $c et $f : Le champ ne doit pas contenir de parenthèses
    if ((mysubfieldcode400 == 'a') | (mysubfieldcode400 == 'b') | (mysubfieldcode400 == 'c') | (mysubfieldcode400 == 'f')):
        if (('(' in texte) | (')' in texte)):
            erreur400 = erreur400 + 'Champ 400: Le sous-champ $' + mysubfieldcode400 + ' ne doit pas contenir de parenthèses [TEST#EL]\n'
    # end
    if (erreur400 != ''):
        texte = '££S££' + texte + '££E££'
    return texte, erreur400


# In[9]:


# Tests sur la 700
def test700(texte, mysubfieldcode700, fmy700_1, fmy700_2, fnb_700a, fnb_700b, fmy103a, fmy103b):
    erreur700 = ''
    fmy103a = fmy103a.strip()
    fmy103b = fmy103b.strip()
    # Si deuxième indicateur 1 il faut $a et $b
    if ((mysubfieldcode700 == 'a') & (fmy700_2 == '1') & (fnb_700b == 0)):
        erreur700 = erreur700 + 'Champ 700: Il manque le sous-champ $b prénom ou corriger « Nom entré au prénom ou dans l\'ordre direct » [TEST#CD]\n'
    # Si deuxième indicateur 0 il n’y a que $a
    if ((mysubfieldcode700 == 'b') & (fmy700_2 == '0') & (fnb_700b > 0)):
        erreur700 = erreur700 + 'Champ 700: Seul le sous-champ $a est autorisé ou corriger « Nom entré au patronyme » [TEST#CE]\n'
    # 700 $a ne doit pas y avoir de virgule
    if ((mysubfieldcode700 == 'a') & (',' in texte)):
        erreur700 = erreur700 + 'Champ 700: Le sous-champ $a ne doit pas contenir de virgule [TEST#CF]\n'
    # 700$b prénom : selon les règles Idref, mettre un espace entre les initiales 
    if (mysubfieldcode700 == 'b'):
        match1 = re.match(r'.*[A-Z]\.[A-Z]\.', texte)
        if match1 is not None:
            erreur700 = erreur700 + 'Champ 700: Merci de rajouter un espace entre les initiales [TEST#CG]\n'
        # 700$b prénom : Point après une initiale 
        match2 = re.match(r'.*[A-Z]$', texte)
        if match2 is not None:
            erreur700 = erreur700 + 'Champ 700: Une initiale doit se terminer par un point [TEST#CH]\n'
        # 700$b On me met pas d’espace entre des initiales séparées par un –
        match3 = re.match(r'.*[A-Z]\. - [A-Z]\.', texte)
        if match3 is not None:
            erreur700 = erreur700 + 'Champ 700: Merci de supprimer l\'espace en trop entre l\'initiale et le tiret [TEST#CI]\n'
        # 700$b le sous champ $b ne doit pas contenir de virgule
        if (',' in texte):
            erreur700 = erreur700 + 'Champ 700: le sous champ $b ne doit pas contenir de virgule [TEST#CJ]\n'
    # 700$c qualificatif : minuscule en début de champ
    if (mysubfieldcode700 == 'c'):
        match4 = re.match(r'^( )?[A-Z].*', texte)
        if match4 is not None:
            erreur700 = erreur700 + 'Champ 700: Le sous-champ $c doit généralement commencer par une minuscule [TEST#CK]\n'
    # 700 $f pas d'espace avant et après le tiret
    if (mysubfieldcode700 == 'f'):
        if (' - ' in texte):
            erreur700 = erreur700 + 'Champ 700: Il ne doit pas y avoir d\'espace avant et après le tiret dans le sous-champ $f [TEST#CL]\n'
    # 700 $a, $b, $c et $f : Le champ ne doit pas contenir de parenthèses
    if ((mysubfieldcode700 == 'a') | (mysubfieldcode700 == 'b') | (mysubfieldcode700 == 'c') | (mysubfieldcode700 == 'f')):
        if (('(' in texte) | (')' in texte)):
            erreur700 = erreur700 + 'Champ 700: Le sous-champ $' + mysubfieldcode700 + ' ne doit pas contenir de parenthèses [TEST#EL]\n'
    # end
    if (erreur700 != ''):
        texte = '££S££' + texte + '££E££'
    return texte, erreur700


# In[10]:


# Tests sur la 810 
def test810(texte):
    erreur810 = ''
    # 810 $a avec lien il faut : , aaaa-mm-jj
    if ('http' in texte):
        match = re.match(r'.*, ([1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])', texte)
        if match is None:
            erreur810 = erreur810 + 'Champ 810: Il manque la date de consultation ou la date de consultation doit être aaaa-mm-jj [TEST#CO]\n'
            texte = re.sub(', ([^,]+)$', ', £S£\\1£E£', texte)
        match = re.match(r'.*, ([1-2][0-9][0-9][0-9] - [0-9][0-9] - [0-9][0-9])', texte)
        if match is not None:
            erreur810 = erreur810 + 'Champ 810: Il n\'y a pas d\'espace avant et après le tiret dans la date de consultation [TEST#CP]\n'
            texte = re.sub(', ([^,]+)$', ', £S£\\1£E£', texte)
        # Champ 810: Le lien VIAF doit correspondre à une bibliothèque précise, il commence par http://viaf.org/processed/
        if ('viaf.org/viaf' in texte):
            erreur810 = erreur810 + 'Champ 810: Le lien VIAF doit correspondre à une bibliothèque précise, il commence par http://viaf.org/processed/ [TEST#CQ]\n'
            texte = texte.replace('viaf.org/viaf', '£S£viaf.org/viaf£E£')
        # Champ 810: La source doit être mentionnée sous la forme : VIAF - Bibliothèque source - http://viaf.org/processed...., aaaa-mm-jj
        if ('viaf.org' in texte):
            match = re.match(r'VIAF - ([A-zÀ-ú0-9-\' ]+) - .*', texte)
            if match is None:
                erreur810 = erreur810 + 'Champ 810: La source doit être mentionnée sous la forme : VIAF - Bibliothèque source - http://viaf.org/processed..., aaaa-mm-jj [TEST#CR]\n'
                texte = '££S££' + texte + '££E££'
        # else :
            # match = re.match(r'([A-zÀ-ú0-9-\'\(\)\:\;\,\. ]+) - http.*', texte)
            # if match is None:
                # erreur810 = erreur810 + 'Champ 810: Le lien doit être précédé du nom de la source\n'
    else :
        # Un champ minimum obligatoire avec sous-champ $a : ……., aaaa
        # 810 $a sans lien il faut : , aaaa
        # Champ 810: Il manque la date de publication
        match = re.match(r'.*, ([\[\)A-Z ]+)?([1-2][0-9]{3})([\]\) ])?', texte)
        if match is None:
            erreur810 = erreur810 + 'Champ 810: La date de publication est-elle bien présente ou la ponctuation avant la date est erronée ? [TEST#CS]\n'
            texte = re.sub(', ([^,]+)$', ', £S£\\1£E£', texte)
        # Champ 810 $a : La source ne doit pas contenir de point final
        if (texte.endswith('.')):
            erreur810 = erreur810 + 'Champ 810: La source ne doit pas contenir de point final [TEST#CT]\n'
            texte = texte[0:-1] + '£S£.£E£'
    # Champ 810 $a : pas de |c |b  ou $$b $$c (pas de codification)
    if (('|b' in texte) | ('|c' in texte) | ('$$b' in texte) | ('$$c' in texte)):
        erreur810 = erreur810 + 'Champ 810: La source ne doit pas contenir de codification [TEST#CU]\n'
        texte = texte.replace('|b', '£S£|b£E£')
        texte = texte.replace('|c', '£S£|c£E£')
        texte = texte.replace('$$b', '£S£$$b£E£')
        texte = texte.replace('$$c', '£S£$$c£E£')

    # end
    return texte, erreur810


# Tests sur la 815 
def test815(texte):
    erreur815 = ''
    # 815 $a avec lien il faut : , aaaa-mm-jj
    if ('http' in texte):
        match = re.match(r'.*([1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])', texte)
        if match is None:
            erreur815 = erreur815 + 'Champ 815: Il manque la date de consultation ou la date de consultation doit être aaaa-mm-jj [TEST#ED]\n'
        match = re.match(r'.*([1-2][0-9][0-9][0-9] - [0-9][0-9] - [0-9][0-9])', texte)
        if match is not None:
            erreur815 = erreur815 + 'Champ 815: Il n\'y a pas d\'espace avant et après le tiret dans la date de consultation [TEST#EE]\n'
        # Champ 815: Le lien VIAF doit correspondre à une bibliothèque précise, il commence par http://viaf.org/processed/
        if ('viaf.org/viaf' in texte):
            erreur815 = erreur815 + 'Champ 815: Le lien VIAF doit correspondre à une bibliothèque précise, il commence par http://viaf.org/processed/ [TEST#EF]\n'
        # Champ 815: La source doit être mentionnée sous la forme : VIAF - Bibliothèque source - http://viaf.org/processed...., aaaa-mm-jj
        if ('viaf.org' in texte):
            match = re.match(r'VIAF - ([A-zÀ-ú0-9-\' ]+) - .*', texte)
            if match is None:
                erreur815 = erreur815 + 'Champ 815: La source doit être mentionnée sous la forme : VIAF - Bibliothèque source - http://viaf.org/processed..., aaaa-mm-jj [TEST#EG]\n'
        if (erreur815 != ''):
            texte = '££S££' + texte + '££E££'
    # end
    return texte, erreur815


# In[13]:


# test de zone ou champ répété
def repeatedSubstring(source):
    # flags = re.IGNORECASE
    erreur_repetition = ''
    # test de répétition d'une zone en entier
    source_split = source.split(' \n')
    source_split_unique = []
    source_split_unique_counts = []
    [source_split_unique.append(i) for i in source_split if i not in source_split_unique]
    for zone1 in source_split_unique:
        zone1_count = 0
        for zone2 in source_split:
            if (zone1.strip() == zone2.strip()):
                zone1_count = zone1_count + 1
        source_split_unique_counts.append(zone1_count)
    for i, myzone in enumerate(source_split_unique):
        myzone_code = myzone.strip()[0:3]
        myzone_count = source_split_unique_counts[i]
        if myzone_code.isdigit():
            if ((int(myzone_code) > 10) & (int(myzone_code) < 900)):
                # print(myzone_code + ' : ' + str(myzone_count) + ' occurences')
                if ((len(myzone) > 1) & (myzone_count > 1)) :
                    # print(myzone_code + ' : ' + str(myzone_count) + ' occurences')
                    erreur_repetition = erreur_repetition + 'Champ ' + myzone_code + ': Champ à double [TEST#CV]\n'
                    source = source.replace(myzone, '££S££' + myzone + '££E££')
    # test de répétition d'un sous-champ en entier
    # print ('*****************************')
    for myzone in source_split_unique:
        myzone_code = myzone.strip()[0:3]
        if myzone_code.isdigit():
            if ((int(myzone_code) > 10) & (int(myzone_code) < 900)):
                zone_split = myzone.split(' $')
                zone_split_unique = []
                zone_split_unique_counts = []
                [zone_split_unique.append(i) for i in zone_split if i not in zone_split_unique]
                for champ1 in zone_split_unique:
                    champ1_count = 0
                    for champ2 in zone_split:
                        if (champ1.strip() == champ2.strip()):
                            champ1_count = champ1_count + 1
                    zone_split_unique_counts.append(champ1_count)
                for i, mychamp in enumerate(zone_split_unique):
                    mychamp_count = zone_split_unique_counts[i]
                    # print(myzone_code + ' $' + mychamp[0:1] + ' : ' + str(mychamp_count) + ' occurences')
                    if ((len(mychamp) > 1) & (mychamp_count > 1)) :
                        # print(myzone_code + ' $' + mychamp[0:1] + ' : ' + str(mychamp_count) + ' occurences')
                        erreur_repetition = erreur_repetition + 'Champ ' + myzone_code + ': Sous-champ $' + mychamp[0:1] + ' à double [TEST#CW]\n'
                        source = source.replace(mychamp, '£S£' + mychamp + '£E£')
    return source, erreur_repetition


# normalization des noms de fichiers
def slugify(value, allow_unicode=False):
    # Taken from https://github.com/django/django/blob/master/django/utils/text.py
    # Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    # dashes to single dashes. Remove characters that aren't alphanumerics,
    # underscores, or hyphens. Convert to lowercase. Also strip leading and
    # trailing whitespace, dashes, and underscores.
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


# In[16]:



# Recherche d'erreurs et export final
def processidref(mypath):
    # dossier des fichiers à traiter
    pathin = 'xml/records/' + mypath + '/'
    pathout = 'par_date/' + mypath + '/'

    # files
    files = os.listdir(pathin)
    # boucle sur les fichiers
    recs_avec_erreur = 0
    for file in files:
        # isoler les fichiers de la date
        if (file[0:8] == madate2):
            myidref = file[9:18]
            myfilesuffix1 = ''
            myfilesuffix2 = ''
            nb_erreurs = 0
            nb_035 = 0
            nb_035_rero = 0
            nb_033_035_899 = 0
            nb_101 = 0
            nb_102 = 0
            nb_103 = 0
            nb_103ab = 0
            nb_120 = 0
            nb_150 = 0
            nb_150b = 0
            nb_200 = 0
            nb_200a = 0
            nb_200b = 0
            nb_200c = 0
            nb_200f = 0
            nb_210 = 0
            nb_210_1x = 0
            nb_210b = 0
            nb_210dfe = 0
            nb_210f = 0
            nb_400 = 0
            nb_400a = 0
            nb_400b = 0
            nb_400f = 0
            nb_410 = 0
            nb_410b = 0
            nb_410_1x = 0
            nb_410dfe = 0
            nb_510 = 0
            nb_510b = 0
            nb_700 = 0
            nb_700a = 0
            nb_700b = 0
            nb_700f = 0
            nb_710 = 0
            nb_710b = 0
            nb_710dfe = 0
            nb_810 = 0
            nb_810a = 0
            message_erreur = ''
            message_erreur_sorted = ''
            fichier_text = ''
            my008 = ''
            my035_a = ''
            my035_2 = ''
            my103a = ''
            my103b = ''
            my200_1 = ''
            my200_2 = ''
            my200_fs = []
            my400_1 = ''
            my400_2 = ''
            my700_1 = ''
            my700_2 = ''
            erreur_ordre_210dfe = 0
            # skip x files in case of error 
            # if (int(file_[-22:-14]) > 20220101):
            #     print(file_[-22:-14])
            # print(file)
            # Parse XML
            root = etree.parse(pathin + '/' + file)

            # XML to TXT
            fichier_text = fichier_text + 'Date de Creation : ' + root.find("./controlfield[@tag='004']").text + '\n'
            fichier_text = fichier_text + 'URL IdRef : ' + root.find("./controlfield[@tag='003']").text + '\n'
            fichier_text = fichier_text + 'Leader : ' + root.find("./leader").text + '\n'

            # controlfield
            mycontrolfields = root.findall("./controlfield")
            for mycontrolfield in mycontrolfields:
                fichier_text = fichier_text + mycontrolfield.attrib['tag'] + ' : ' + mycontrolfield.text + '\n'
                if (mycontrolfield.attrib['tag'] == '008'):
                    my008 = mycontrolfield.text
            # fields
            # boucle de comptage
            myfields = root.findall("./datafield")
            for myfield in myfields:
                ind1 = myfield.attrib['ind1']
                ind2 = myfield.attrib['ind2']
                mysubfields = myfield.findall("./subfield")
                # test 033 ou 035 ou 899 (notices importées)
                if (myfield.attrib['tag'] == '033'):
                    nb_033_035_899 = nb_033_035_899 + 1
                if (myfield.attrib['tag'] == '035'):
                    nb_035 = nb_035 + 1
                    nb_033_035_899 = nb_033_035_899 + 1
                if (myfield.attrib['tag'] == '899'):
                    nb_033_035_899 = nb_033_035_899 + 1
                # test 101
                if (myfield.attrib['tag'] == '101'):
                    nb_101 = nb_101 + 1
                # test 102
                elif (myfield.attrib['tag'] == '102'):
                    nb_102 = nb_102 + 1
                # test 103
                elif (myfield.attrib['tag'] == '103'):
                    nb_103 = nb_103 + 1
                    # test 103a et 103b
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            my103a = mysubfield.text
                            nb_103ab = nb_103ab + 1
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            my103b = mysubfield.text
                            nb_103ab = nb_103ab + 1
                # test 120
                elif (myfield.attrib['tag'] == '120'):
                    nb_120 = nb_120 + 1
                # test 150
                elif (myfield.attrib['tag'] == '150'):
                    nb_150 = nb_150 + 1
                    # test 150b
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_150b = nb_150b + 1
                # test 200
                elif (myfield.attrib['tag'] == '200'):
                    nb_200 = nb_200 + 1
                    my200_1 = ind1
                    my200_2 = ind2
                    # test 200a
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            nb_200a = nb_200a + 1
                            if (nb_200a == 1):
                                myfilesuffix1 = myfilesuffix1 + mysubfield.text + '_'
                    # test 200b
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_200b = nb_200b + 1
                            if (nb_200b == 1):
                                myfilesuffix1 = myfilesuffix1 + mysubfield.text + '_'
                    # test 200c
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'c') & (mysubfield.text is not None)):
                            nb_200c = nb_200c + 1
                            if (nb_200c == 1):
                                myfilesuffix1 = myfilesuffix1 + mysubfield.text + '_'
                    # test 200f
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            nb_200f = nb_200f + 1
                            my200_fs.append(mysubfield.text)
                            if (nb_200f == 1):
                                myfilesuffix1 = myfilesuffix1 + mysubfield.text + '_'
                # test 210
                elif (myfield.attrib['tag'] == '210'):
                    nb_210 = nb_210 + 1
                    # test 210_1x
                    if (ind1 == '1'):
                        nb_210_1x = nb_210_1x + 1
                    # test 210dfe et 210b
                    for mysubfield in mysubfields:
                        if (((mysubfield.attrib['code'] == 'd') | (mysubfield.attrib['code'] == 'f') | (mysubfield.attrib['code'] == 'e')) & (mysubfield.text is not None)):
                            nb_210dfe = nb_210dfe + 1
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_210b = nb_210b + 1
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            nb_210f = nb_210f + 1
                        # suffix pour les collectivités
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'c') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'd') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'e') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'x') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 215
                elif (myfield.attrib['tag'] == '215'):
                    for mysubfield in mysubfields:
                        # suffix pour les noms de famille
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'x') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 216
                elif (myfield.attrib['tag'] == '216'):
                    for mysubfield in mysubfields:
                        # suffix pour les noms de marque
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 220
                elif (myfield.attrib['tag'] == '220'):
                    for mysubfield in mysubfields:
                        # suffix pour les noms géo
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 230
                elif (myfield.attrib['tag'] == '230'):
                    for mysubfield in mysubfields:
                        # suffix pour les noms titre uniforme
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 240
                elif (myfield.attrib['tag'] == '240'):
                    for mysubfield in mysubfields:
                        # suffix pour les noms auteur titre
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 't') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 250
                elif (myfield.attrib['tag'] == '250'):
                    for mysubfield in mysubfields:
                        # suffix pour les Noms communs
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'x') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 280
                elif (myfield.attrib['tag'] == '280'):
                    for mysubfield in mysubfields:
                        # suffix pour la Forme ou Genre Rameau
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                        if ((mysubfield.attrib['code'] == 'x') & (mysubfield.text is not None)):
                            myfilesuffix2 = myfilesuffix2 + mysubfield.text + '_'
                # test 400
                elif (myfield.attrib['tag'] == '400'):
                    nb_400 = nb_400 + 1
                    my400_1 = ind1
                    my400_2 = ind2
                    # test 400a
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            nb_400a = nb_400a + 1
                    # test 400b
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_400b = nb_400b + 1
                    # test 400f
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            nb_400f = nb_400f + 1
                # test 410
                elif (myfield.attrib['tag'] == '410'):
                    nb_410 = nb_410 + 1
                    # test 410_1x
                    if ((ind1 == '1') & (ind2 == ' ')):
                        nb_410_1x = nb_410_1x + 1
                    # test 410dfe et 410b
                    for mysubfield in mysubfields:
                        if (((mysubfield.attrib['code'] == 'd') | (mysubfield.attrib['code'] == 'f') | (mysubfield.attrib['code'] == 'e')) & (mysubfield.text is not None)):
                            nb_410dfe = nb_410dfe + 1
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_410b = nb_410b + 1
                # test 510
                elif (myfield.attrib['tag'] == '510'):
                    nb_510 = nb_510 + 1
                    # test 510b
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_510b = nb_510b + 1
                # test 700
                elif (myfield.attrib['tag'] == '700'):
                    nb_700 = nb_700 + 1
                    my700_1 = ind1
                    my700_2 = ind2
                    # test 700a
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            nb_700a = nb_700a + 1
                    # test 700b
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_700b = nb_700b + 1
                    # test 700f
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            nb_700f = nb_700f + 1
                # test 710
                elif (myfield.attrib['tag'] == '710'):
                    nb_710 = nb_710 + 1
                    # test 710dfe et 710b
                    for mysubfield in mysubfields:
                        if (((mysubfield.attrib['code'] == 'd') | (mysubfield.attrib['code'] == 'f') | (mysubfield.attrib['code'] == 'e')) & (mysubfield.text is not None)):
                            nb_710dfe = nb_710dfe + 1
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_710b = nb_710b + 1
                # test 810
                elif (myfield.attrib['tag'] == '810'):
                    nb_810 = nb_810 + 1
                    # test 810a
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            nb_810a = nb_810a + 1
                
            # boucle pour les erreurs
            for myfield in myfields:
                subfields_text = ''
                tag_erreur = 0
                all_erreur = 0
                my035_a = ''
                my035_2 = ''
                myerror035 = ''
                nb_210b_part = 0
                nb_410b_part = 0
                nb_510b_part = 0
                nb_710b_part = 0
                myfieldnumber = int(myfield.attrib['tag'])
                ind1 = myfield.attrib['ind1']
                ind2 = myfield.attrib['ind2']
                if ind1 == ' ':
                    ind1 = '_'
                if ind2 == ' ':
                    ind2 = '_'
                mysubfields = myfield.findall("./subfield")

                # test 035 $2 RERO
                if (myfield.attrib['tag'] == '035'):
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'a') & (mysubfield.text is not None)):
                            my035_a = mysubfield.text
                        elif ((mysubfield.attrib['code'] == '2') & (mysubfield.text is not None)):
                            my035_2 = mysubfield.text
                    myerror035 = test035(my035_a, my035_2)
                    if (myerror035 != ''):
                        # print(file + ' 035 ERREUR : ' + myerror035)
                        # df.loc[df['idref'] == myidref, 'test_035'] = 'X'
                        nb_erreurs = nb_erreurs + 1
                        tag_erreur = 1
                        all_erreur = 1
                        message_erreur = message_erreur + myerror035
                
                # test sur les sous-champs $b
                if (myfield.attrib['tag'] == '210') :
                    nb_210b_part = 0
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_210b_part = nb_210b_part + 1
                if (myfield.attrib['tag'] == '410') :
                    nb_410b_part = 0
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_410b_part = nb_410b_part + 1
                if (myfield.attrib['tag'] == '510') :
                    nb_510b_part = 0
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_510b_part = nb_510b_part + 1
                if (myfield.attrib['tag'] == '710') :
                    nb_710b_part = 0
                    for mysubfield in mysubfields:
                        if ((mysubfield.attrib['code'] == 'b') & (mysubfield.text is not None)):
                            nb_710b_part = nb_710b_part + 1
                
                # test sur les indicateurs
                # 210: combinaison des indicateurs 11 impossible
                if ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (ind1 == '1') & (ind2 == '1')):
                    # print(file + ' 210 ERREUR : Un congrès n\'est jamais introduit sous un nom de lieu')
                    # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 210: Un congrès n\'est jamais introduit sous un nom de lieu. Soit le premier indicateur (collectivité 0 ou congrès 1) est faux, soit le deuxième indicateur est faux (nom de lieu 1 ou ordre direct 2) [TEST#CX]\n'
                    ind1 = '££S££' + ind1 + '££E££'
                    ind2 = '££S££' + ind2 + '££E££'
                # 210 si présence de $d et/ou $e et $f, sans $b, les indicateurs doivent être 12
                if ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (nb_210dfe > 0) & (nb_210f > 0) & (nb_210b_part == 0) & ((ind1 != '1') | (ind2 != '2'))):
                    # print(file + ' 210 ERREUR : corriger le nom de type « collectivité » en « congrès »')
                    # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 210: Corriger le nom de type « collectivité » en « congrès » s\'il s’agit bien d’un congrès dans l\'ordre direct [TEST#CY1]\n'
                    ind1 = '££S££' + ind1 + '££E££'
                    ind2 = '££S££' + ind2 + '££E££'
                # 210 si présence de $d et/ou $e sans $f, sans $b, les indicateurs doivent être 12
                if ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (nb_210dfe > 0) & (nb_210f == 0) & (nb_210b_part == 0) & ((ind1 != '1') | (ind2 != '2'))):
                    # print(file + ' 210 ERREUR : corriger le nom de type « collectivité » en « congrès »')
                    # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 210: Corriger le nom de type « collectivité » en « congrès » S\'il ne s’agit pas d’un congrès et que la date qualifie la collectivité, elle se met en $c [TEST#CY2]\n'
                    ind1 = '££S££' + ind1 + '££E££'
                    ind2 = '££S££' + ind2 + '££E££'
                # 210 Si champ 210 02 et $b 
                elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (ind1 == '0') & (ind2 == '2') & (nb_210b_part > 0)):
                    # print(file + ' 210 ERREUR : Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort)')
                    # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 210: Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort), sauf si le $b contient la localisation de la collectivité, elle doit être codifiée en $c [TEST#CZ]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 210 Si champ 210 01 et pas de $b
                elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (ind1 == '0') & (ind2 == '1') & (nb_210b_part == 0)):
                    # print(file + ' 210 ERREUR : Corriger le 2e indicateur en 0 (nom entré dans l’ordre direct)')
                    # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 210: Corriger le 2e indicateur en 2 sauf si lieu géographique (nom entré dans l\'ordre direct) [TEST#DA]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 210 l'ordre des élements doit être $d $f $e
                elif ((myfield.attrib['tag'] == '210') & (nb_210dfe > 1)):
                    # test de position des $d $f $e
                    my210i = 0
                    my210d_position = 0
                    my210f_position = 0
                    my210e_position = 0
                    erreur_ordre_210dfe = 0
                    for mysubfield in mysubfields:
                        my210i = my210i + 1
                        if ((mysubfield.attrib['code'] == 'd') & (mysubfield.text is not None)):
                            my210d_position = my210i
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            my210f_position = my210i
                        if ((mysubfield.attrib['code'] == 'e') & (mysubfield.text is not None)):
                            my210e_position = my210i
                    if ((my210d_position > my210f_position) | (my210d_position > my210e_position) | (my210f_position > my210e_position)):
                        # erreur de position 
                        erreur_ordre_210dfe = 1
                        tag_erreur = 1
                        # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                        nb_erreurs = nb_erreurs + 1
                        message_erreur = message_erreur + 'Champ 210: L\'ordre des sous-champs doit être $d $f $e [TEST#EK]\n'
                # 410: combinaison des indicateurs 11 impossible
                elif (((my008 == 'Tb5') | (my008 == 'Tg5')) & (myfield.attrib['tag'] == '410') & (ind1 == '1') & (ind2 == '1')):
                    # print(file + ' 410 ERREUR : Un congrès n\'est jamais introduit sous un nom de lieu')
                    # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 410: Un congrès n\'est jamais introduit sous un nom de lieu. Soit le premier indicateur (collectivité 0 ou congrès 1) est faux, soit le deuxième indicateur est faux (nom de lieu 1 ou ordre direct 2) [TEST#DB]\n'
                    ind1 = '££S££' + ind1 + '££E££'
                    ind2 = '££S££' + ind2 + '££E££'
                # 410 si présence de $d et/ou $e et/ou $f, sans $b, les indicateurs doivent être 12
                elif (((my008 == 'Tb5') | (my008 == 'Tg5')) & (myfield.attrib['tag'] == '410') & ((mysubfield.attrib['code'] == 'd') | (mysubfield.attrib['code'] == 'e') | (mysubfield.attrib['code'] == 'f')) & (nb_410dfe > 0) & (nb_410b_part == 0) & ((ind1 != '1') | (ind2 != '2'))):
                    # print(file + ' 410 ERREUR : corriger le nom de type « collectivité » en « congrès »')
                    # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 410: corriger le nom de type « collectivité » en « congrès » [TEST#DC]\n'
                    ind1 = '££S££' + ind1 + '££E££'
                    ind2 = '££S££' + ind2 + '££E££'
                # 410 Si champ 410 02 et $b 
                elif (((my008 == 'Tb5') | (my008 == 'Tg5')) & (myfield.attrib['tag'] == '410') & (ind1 == '0') & (ind2 == '2') & (nb_410b_part > 0)):
                    # print(file + ' 410 ERREUR : Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort)')
                    # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 410: Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort), sauf si le $b contient la localisation de la collectivité, elle doit être codifiée en $c [TEST#CZ]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 410 Si champ 410 01 et pas de $b
                elif (((my008 == 'Tb5') | (my008 == 'Tg5')) & (myfield.attrib['tag'] == '410') & (ind1 == '0') & (ind2 == '1') & (nb_410b_part == 0)):
                    # print(file + ' 410 ERREUR : Corriger le 2e indicateur en 0 (nom entré dans l’ordre direct)')
                    # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 410: Corriger le 2e indicateur en 2 sauf si lieu géographique (nom entré dans l\'ordre direct) [TEST#DA]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 410 l'ordre des élements doit être $d $f $e
                elif ((myfield.attrib['tag'] == '410') & (nb_410dfe > 1)):
                    # test de position des $d $f $e
                    my410i = 0
                    my410d_position = 0
                    my410f_position = 0
                    my410e_position = 0
                    erreur_ordre_410dfe = 0
                    for mysubfield in mysubfields:
                        my410i = my410i + 1
                        if ((mysubfield.attrib['code'] == 'd') & (mysubfield.text is not None)):
                            my410d_position = my410i
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            my410f_position = my410i
                        if ((mysubfield.attrib['code'] == 'e') & (mysubfield.text is not None)):
                            my410e_position = my410i
                    if ((my410d_position > my410f_position) | (my410d_position > my410e_position) | (my410f_position > my410e_position)):
                        # erreur de position 
                        erreur_ordre_410dfe = 1
                        tag_erreur = 1
                        # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                        nb_erreurs = nb_erreurs + 1
                        message_erreur = message_erreur + 'Champ 410: L\'ordre des sous-champs doit être $d $f $e [TEST#EK]\n'
                # 510 Si champ 510 02 et $b 
                # annulé car impossible à corriger
                # elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '510') & (ind1 == '0') & (ind2 == '2') & (nb_510b_part > 0)):
                    # print(file + ' 510 ERREUR : Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort)')
                    # df.loc[df['idref'] == myidref, 'test_510'] = 'X'
                    # nb_erreurs = nb_erreurs + 1
                    # tag_erreur = 1
                    # message_erreur = message_erreur + 'Champ 510: Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort) [TEST#CZ]\n'
                    # ind2 = '££S££' + ind2 + '££E££'
                # 510 Si champ 510 01 et pas de $b
                elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '510') & (ind1 == '0') & (ind2 == '1') & (nb_510b_part == 0)):
                    # print(file + ' 510 ERREUR : Corriger le 2e indicateur en 0 (nom entré dans l’ordre direct)')
                    # df.loc[df['idref'] == myidref, 'test_510'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 510: Corriger le 2e indicateur en 2 sauf si lieu géographique (nom entré dans l\'ordre direct) [TEST#DA]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 710 Si champ 710 02 et $b 
                elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '710') & (ind1 == '0') & (ind2 == '2') & (nb_710b_part > 0)):
                    # print(file + ' 710 ERREUR : Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort)')
                    # df.loc[df['idref'] == myidref, 'test_710'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 710: Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort) [TEST#CZ]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 710 Si champ 710 01 et pas de $b
                elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '710') & (ind1 == '0') & (ind2 == '1') & (nb_710b_part == 0)):
                    # print(file + ' 710 ERREUR : Corriger le 2e indicateur en 0 (nom entré dans l’ordre direct)')
                    # df.loc[df['idref'] == myidref, 'test_710'] = 'X'
                    nb_erreurs = nb_erreurs + 1
                    tag_erreur = 1
                    message_erreur = message_erreur + 'Champ 710: Corriger le 2e indicateur en 2 sauf si lieu géographique (nom entré dans l\'ordre direct) [TEST#DA]\n'
                    ind2 = '££S££' + ind2 + '££E££'
                # 710 l'ordre des élements doit être $d $f $e
                elif ((myfield.attrib['tag'] == '710') & (nb_710dfe > 1)):
                    # test de position des $d $f $e
                    my710i = 0
                    my710d_position = 0
                    my710f_position = 0
                    my710e_position = 0
                    erreur_ordre_710dfe = 0
                    for mysubfield in mysubfields:
                        my710i = my710i + 1
                        if ((mysubfield.attrib['code'] == 'd') & (mysubfield.text is not None)):
                            my710d_position = my710i
                        if ((mysubfield.attrib['code'] == 'f') & (mysubfield.text is not None)):
                            my710f_position = my710i
                        if ((mysubfield.attrib['code'] == 'e') & (mysubfield.text is not None)):
                            my710e_position = my710i
                    if ((my710d_position > my710f_position) | (my710d_position > my710e_position) | (my710f_position > my710e_position)):
                        # erreur de position 
                        erreur_ordre_710dfe = 1
                        tag_erreur = 1
                        # df.loc[df['idref'] == myidref, 'test_710'] = 'X'
                        nb_erreurs = nb_erreurs + 1
                        message_erreur = message_erreur + 'Champ 710: L\'ordre des sous-champs doit être $d $f $e [TEST#EK]\n'
                
                # test sur les sous-champs
                mysubfields = myfield.findall("./subfield")
                for mysubfield in mysubfields:
                    subfields_text = subfields_text + '$' + mysubfield.attrib['code'] + ' '
                    # test errors
                    if (mysubfield.text is not None):
                        # tests communs sauf pour les 9XX qui sont générées automatiquement
                        if (myfieldnumber < 900):
                            mysubfieldtext, myerror = test1(mysubfield.text, myfield.attrib['tag'])
                            if myerror != '':
                                # print(file + ' ERREUR : ' + myerror)
                                # df.loc[df['idref'] == myidref, 'test_caracteres'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + myerror
                        else:
                            mysubfieldtext = mysubfield.text
                            
                        # test 103
                        if (((my008 == 'Tp5') | (my008 == 'Tb5')) & (myfield.attrib['tag'] == '103') & ((mysubfield.attrib['code'] == 'a') | (mysubfield.attrib['code'] == 'b'))):
                            mysubfieldtext103, myerror103 = test103(mysubfieldtext)
                            if (myerror103 != ''):
                                # print(file + ' 103 ERREUR : ' + myerror103)
                                # df.loc[df['idref'] == myidref, 'test_103'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + myerror103
                            subfields_text = subfields_text + mysubfieldtext103 + ' '
                        elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '103') & (mysubfield.attrib['code'] == 'c')):
                            # print(file + ' 103 ERREUR : Le sous-champ $c n\'est pas autorisé')
                            # df.loc[df['idref'] == myidref, 'test_103'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 103: Le sous-champs $c n\'est pas autorisé [TEST#DD]\n'
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '103') & (mysubfield.attrib['code'] == 'd')):
                            # print(file + ' 103 ERREUR : Le sous-champ $d n\'est pas autorisé')
                            # df.loc[df['idref'] == myidref, 'test_103'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 103: Le sous-champ $d n\'est pas autorisé [TEST#DE]\n'
                            subfields_text = subfields_text + '££S££' + subfields_text + '££E££' + ' '

                        # test 150 et 210 1x
                        elif ((myfield.attrib['tag'] == '150') & (my008 == 'Tb5') & (mysubfield.attrib['code'] == 'b') & (nb_210_1x > 0)):
                            # 150: si 210 1x (congrès) $b est toujours 1 (dans les autres cas, $b = 0 ou 1) 
                            # Champ 150: S'il s'agit d'un congrès (210 1x), le $b doit être 1
                            if (mysubfieldtext != '1'):
                                # df.loc[df['idref'] == myidref, 'test_150'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 150: S\'il s\'agit d\'un congrès (210 1x), le $b doit être 1 [TEST#DF]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # test 150 et 210 Si présence de $d et/ou $e et/ou $f avec $b indicateurs 02 et champ 150 $b absent 
                        elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (mysubfield.attrib['code'] == 'b') & (nb_210dfe > 0) & (nb_210b_part > 0) & (ind1 == '0') & (ind2 == '2') & (nb_150b == 0)):
                            if (mysubfieldtext != ''):
                                # print(file + ' ERREUR : Il manque le champ 150, sous-champ $b 1 (l’entité décrite est un congrès)')
                                # df.loc[df['idref'] == myidref, 'test_150'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 210: Il manque le champ 150, sous-champ $b 1 (l\'entité décrite est un congrès) [TEST#DG]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # test 150 et 210 Si présence de $d et/ou $e et/ou $f avec $b indicateurs 02 et champ 150 $b 0 
                        elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '150') & (mysubfield.attrib['code'] == 'b') & (nb_210dfe > 0) & (nb_210b_part > 0) & (ind1 == '0') & (ind2 == '2')):
                            if (mysubfieldtext == '0'):
                                # print(file + ' 150 ERREUR : Corriger le sous-champ $b 1 (l’entité décrite est un congrès)')
                                # df.loc[df['idref'] == myidref, 'test_150'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 150: Corriger le sous-champ $b 1 (l\'entité décrite est un congrès) [TEST#DH]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        
                        # test 200
                        elif (myfield.attrib['tag'] == '200'):
                            mysubfieldtext200, myerror200 = test200(mysubfieldtext, mysubfield.attrib['code'], my200_1, my200_2, nb_200a, nb_200b, my103a, my103b, my200_fs)
                            if (myerror200 != ''):
                                # print(file + ' 200 ERREUR : ' + myerror200)
                                # df.loc[df['idref'] == myidref, 'test_200'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + myerror200
                            subfields_text = subfields_text + mysubfieldtext200 + ' '
                            
                        # test 210
                        # 210 si premier indicateur 1 et deuxième indicateur 2 (nom entré dans l’ordre direct) pas de $b
                        elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (ind1 == '1') & (ind2 == '2') & (mysubfield.attrib['code'] == 'b')):
                            # print(file + ' 210 ERREUR : Le sous-champ $b n\'est pas autorisé')
                            # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 210: Le sous-champ $b n\'est pas autorisé ou corriger « Nom entré sous un nom de lieu » [TEST#DI]\n'
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # 210 Si premier indicateur 1 deuxième indicateur 2 il faut $d ou $f ou $e au minimum
                        # elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '210') & (ind1 == '1') & (ind2 == '2') & (nb_210dfe == 0)):
                            # print(file + ' 210 ERREUR : Il manque un sous-champ $d et/ou $e et/ou $f')
                            # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                            # nb_erreurs = nb_erreurs + 1
                            # tag_erreur = 1
                            # message_erreur = message_erreur + 'Champ 210: Il manque un sous-champ $d et/ou $e et/ou $f\n'
                            # subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            # nb_210dfe = 1
                        # 210 l'ordre des élements doit être $d $f $e
                        elif ((myfield.attrib['tag'] == '210') & (erreur_ordre_210dfe == 1) & ((mysubfield.attrib['code'] == 'd') | (mysubfield.attrib['code'] == 'e') | (mysubfield.attrib['code'] == 'f'))):
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # 210 $a, $b, $c et $f : Le champ ne doit pas contenir de parenthèses
                        elif ((myfield.attrib['tag'] == '210') & ((mysubfield.attrib['code'] == 'a') | (mysubfield.attrib['code'] == 'b') | (mysubfield.attrib['code'] == 'c') | (mysubfield.attrib['code'] == 'f'))):
                            if (('(' in mysubfieldtext) | (')' in mysubfieldtext)):
                                # df.loc[df['idref'] == myidref, 'test_210'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 210: Le sous-champ $' + mysubfield.attrib['code'] + ' ne doit pas contenir de parenthèses [TEST#EL]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '

                        # test 215
                        # Virgule, parenthèses et point-virgule sont autorisés
                        elif ((my008 == 'Tg5') & (myfield.attrib['tag'] == '215') & ((mysubfield.attrib['code'] == 'a') | (mysubfield.attrib['code'] == 'x') | (mysubfield.attrib['code'] == 'z'))):
                            match215 = re.match(r'[A-zÀ-ú0-9 \,\(\)\;]+', mysubfieldtext)
                            if match215 is None:
                                # print(file + ' 215 ERREUR : $a, $x, $z seuls la virgule, les parenthèses et le point-virgule sont autorisés')
                                # df.loc[df['idref'] == myidref, 'test_215'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 215: $' + mysubfield.attrib['code'] + ' seuls la virgule, les parenthèses et le point-virgule sont autorisés [TEST#DJ]\n'
                                if (mysubfieldtext.startswith('@')):
                                    message_erreur = message_erreur + 'Champ 215: $' + mysubfield.attrib['code'] + ' le caractère @ en début de sous-champ n\'est pas autorisé [TEST#DK]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '

                        # test 340
                        # pas de codification (pas de |c |b  ou $$b $$c) 
                        # ne pas tester si la notice est importée (033 ou 035 présente)
                        elif ((myfield.attrib['tag'] == '340') & (mysubfield.attrib['code'] == 'a') & (nb_033_035_899 == 0)):
                            if (('|b' in mysubfieldtext) | ('|c' in mysubfieldtext) | ('$$b' in mysubfieldtext) | ('$$c' in mysubfieldtext)):
                                # print(file + ' Champ 340: La note biographique d\'activité ne doit pas contenir de codification')
                                # df.loc[df['idref'] == myidref, 'test_340'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 340: La note ne doit pas contenir de codification [TEST#DL]\n'
                                mysubfieldtext = mysubfieldtext.replace('|b', '£S£|b£E£')
                                mysubfieldtext = mysubfieldtext.replace('|c', '£S£|c£E£')
                                mysubfieldtext = mysubfieldtext.replace('$$b', '£S£$$b£E£')
                                mysubfieldtext = mysubfieldtext.replace('$$c', '£S£$$c£E£')
                            # pas de point final
                            if (mysubfieldtext[-1] == '.'):
                                # print(file + ' 340 ERREUR : La note biographique d\'activité ne doit pas contenir de point final')
                                # df.loc[df['idref'] == myidref, 'test_340'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 340: La note ne doit pas contenir de point final [TEST#DM]\n'
                                mysubfieldtext = mysubfieldtext[0:-1] + '£S£.£E£'
                            subfields_text = subfields_text + mysubfieldtext + ' '
                              
                        # test 356
                        # pas de codification (pas de |c |b  ou $$b $$c) 
                        elif ((myfield.attrib['tag'] == '356') & (mysubfield.attrib['code'] == 'a')):
                            if (('|b' in mysubfieldtext) | ('|c' in mysubfieldtext) | ('$$b' in mysubfieldtext) | ('$$c' in mysubfieldtext)):
                                # print(file + ' Champ 356: La note biographique d\'activité ne doit pas contenir de codification')
                                # df.loc[df['idref'] == myidref, 'test_356'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 356: La note ne doit pas contenir de codification [TEST#DN]\n'
                                mysubfieldtext = mysubfieldtext.replace('|b', '£S£|b£E£')
                                mysubfieldtext = mysubfieldtext.replace('|c', '£S£|c£E£')
                                mysubfieldtext = mysubfieldtext.replace('$$b', '£S£$$b£E£')
                                mysubfieldtext = mysubfieldtext.replace('$$c', '£S£$$c£E£')
                            # pas de point final
                            if (mysubfieldtext[-1] == '.'):
                                # print(file + ' 356 ERREUR : La note biographique d\'activité ne doit pas contenir de point final')
                                # df.loc[df['idref'] == myidref, 'test_356'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 356: La note ne doit pas contenir de point final [TEST#DO]\n'
                                mysubfieldtext = mysubfieldtext[0:-1] + '£S£.£E£'
                            subfields_text = subfields_text + mysubfieldtext + ' '

                        # test 400
                        elif (myfield.attrib['tag'] == '400'):
                            mysubfieldtext400, myerror400 = test400(mysubfieldtext, mysubfield.attrib['code'], my400_1, my400_2, nb_400a, nb_400b, my103a, my103b)
                            if (myerror400 != ''):
                                # print(file + ' 400 ERREUR : ' + myerror400)
                                # df.loc[df['idref'] == myidref, 'test_400'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + myerror400
                            subfields_text = subfields_text + mysubfieldtext400 + ' '
                              

                        # 410 si premier indicateur 1 et deuxième indicateur 2 (nom entré dans l’ordre direct) pas de $b
                        elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '410') & (ind1 == '1') & (ind2 == '2') & (mysubfield.attrib['code'] == 'b')):
                            # print(file + ' 410 ERREUR : Le sous-champ $b n\'est pas autorisé')
                            # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 410: Le sous-champ $b n\'est pas autorisé ou corriger « Nom entré sous un nom de lieu » [TEST#DP]\n'
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # 410 Si premier indicateur 1 deuxième indicateur 2 il faut $d ou $f ou $e au minimum
                        # elif ((my008 == 'Tb5') & (myfield.attrib['tag'] == '410') & (ind1 == '1') & (ind2 == '2') & (nb_410dfe == 0)):
                            # print(file + ' 410 ERREUR : Il manque un sous-champ $d et/ou $e et/ou $f')
                            # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                            # nb_erreurs = nb_erreurs + 1
                            # message_erreur = message_erreur + 'Champ 410: Il manque un sous-champ $d et/ou $e et/ou $f\n'
                            # subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            # nb_410dfe = 1
                        # 410 sur une autorité de type personne (Tp)
                        elif ((my008 == 'Tp5') & (myfield.attrib['tag'] == '410') & (mysubfield.attrib['code'] == 'a')):
                            # print(file + ' 410 ERREUR : Champ 410 : Merci de vérifier qu'il s'agit bien d'une collectivité')
                            # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 410: Merci de vérifier qu\'il s\'agit bien d\'une collectivité [TEST#EH]\n'
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # 410 $a, $b, $c et $f : Le champ ne doit pas contenir de parenthèses
                        elif ((myfield.attrib['tag'] == '410') & ((mysubfield.attrib['code'] == 'a') | (mysubfield.attrib['code'] == 'b') | (mysubfield.attrib['code'] == 'c') | (mysubfield.attrib['code'] == 'f'))):
                            if (('(' in mysubfieldtext) | (')' in mysubfieldtext)):
                                # df.loc[df['idref'] == myidref, 'test_410'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 410: Le sous-champ $' + mysubfield.attrib['code'] + ' ne doit pas contenir de parenthèses [TEST#EL]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '
                            
                        # test 415
                        # Virgule, parenthèses et point-virgule sont autorisés
                        elif ((my008 == 'Tg5') & (myfield.attrib['tag'] == '415') & ((mysubfield.attrib['code'] == 'a') | (mysubfield.attrib['code'] == 'x') | (mysubfield.attrib['code'] == 'z'))):
                            match415 = re.match(r'[A-zÀ-ú0-9 \,\(\)\;]+', mysubfieldtext)
                            if match415 is None:
                                # print(file + ' 415 ERREUR : $a, $x, $z seuls la virgule, les parenthèses et le point-virgule sont autorisés')
                                # df.loc[df['idref'] == myidref, 'test_415'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 415: $' + mysubfield.attrib['code'] + ' seuls la virgule, les parenthèses et le point-virgule sont autorisés [TEST#DQ]\n'
                                if (mysubfieldtext.startswith('@')):
                                    message_erreur = message_erreur + 'Champ 415: $' + mysubfield.attrib['code'] + ' le caractère @ en début de sous-champ n\'est pas autorisé [TEST#DR]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '

                        # test 500
                        # 500 $b le sous champ $b ne doit pas contenir de virgule
                        elif ((myfield.attrib['tag'] == '500') & (mysubfield.attrib['code'] == 'b')):
                            if (',' in mysubfieldtext):
                                # print(file + ' 500 ERREUR : le sous champ $b ne doit pas contenir de virgule')
                                # df.loc[df['idref'] == myidref, 'test_500'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 500: le sous champ $b ne doit pas contenir de virgule [TEST#DS]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '
             
                        # test 700
                        elif (myfield.attrib['tag'] == '700'):
                            mysubfieldtext700, myerror700 = test700(mysubfieldtext, mysubfield.attrib['code'], my700_1, my700_2, nb_700a, nb_700b, my103a, my103b)
                            if (myerror700 != ''):
                                # print(file + ' 700 ERREUR : ' + myerror700)
                                # df.loc[df['idref'] == myidref, 'test_700'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + myerror700
                            subfields_text = subfields_text + mysubfieldtext700 + ' '
                            
                        # test 710 sur une autorité de type personne (Tp)
                        elif ((my008 == 'Tp5') & (myfield.attrib['tag'] == '710')):
                            # print(file + ' 710 ERREUR : Champ 710 : Merci de vérifier qu'il s'agit bien d'une collectivité')
                            # df.loc[df['idref'] == myidref, 'test_710'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 710: Merci de vérifier qu\'il s\'agit bien d\'une collectivité [TEST#EH]\n'
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        # 710 $a, $b, $c et $f : Le champ ne doit pas contenir de parenthèses
                        elif ((myfield.attrib['tag'] == '710') & ((mysubfield.attrib['code'] == 'a') | (mysubfield.attrib['code'] == 'b') | (mysubfield.attrib['code'] == 'c') | (mysubfield.attrib['code'] == 'f'))):
                            if (('(' in mysubfieldtext) | (')' in mysubfieldtext)):
                                # df.loc[df['idref'] == myidref, 'test_710'] = 'X'
                                nb_erreurs = nb_erreurs + 1
                                tag_erreur = 1
                                message_erreur = message_erreur + 'Champ 710: Le sous-champ $' + mysubfield.attrib['code'] + ' ne doit pas contenir de parenthèses [TEST#EL]\n'
                                subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '
                              
                        # test 715
                        elif ((my008 == 'Tg5') & (myfield.attrib['tag'] == '715')):
                            # print(file + ' ERREUR 715 présent')
                            # df.loc[df['idref'] == myidref, 'test_715'] = 'X'
                            nb_erreurs = nb_erreurs + 1
                            tag_erreur = 1
                            message_erreur = message_erreur + 'Champ 715: il n\'est pas autorisé pour les noms géographiques [TEST#DT]\n'
                            subfields_text = subfields_text + '££S££' + mysubfieldtext + '££E££' + ' '
                        
                        # test 810
                        # ne pas tester si la notice est importée (033 ou 035 présente)
                        elif ((myfield.attrib['tag'] == '810') & (nb_033_035_899 == 0)):
                            if (mysubfield.attrib['code'] == 'a'):
                                mysubfieldtext810, myerror810 = test810(mysubfieldtext)
                                if (myerror810 != ''):
                                    # print(file + ' 810 ERREUR : ' + myerror810)
                                    # df.loc[df['idref'] == myidref, 'test_810'] = 'X'
                                    nb_erreurs = nb_erreurs + 1
                                    tag_erreur = 1
                                    message_erreur = message_erreur + myerror810
                                subfields_text = subfields_text + mysubfieldtext810 + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '
                            
                        # test 815
                        # ne pas tester si la notice est importée (033 ou 035 présente)
                        elif ((myfield.attrib['tag'] == '815') & (nb_033_035_899 == 0)):
                            if (mysubfield.attrib['code'] == 'a'):
                                mysubfieldtext815, myerror815 = test815(mysubfieldtext)
                                if (myerror815 != ''):
                                    # print(file + ' 810 ERREUR : ' + myerror810)
                                    # df.loc[df['idref'] == myidref, 'test_815'] = 'X'
                                    nb_erreurs = nb_erreurs + 1
                                    tag_erreur = 1
                                    message_erreur = message_erreur + myerror815
                                subfields_text = subfields_text + mysubfieldtext815 + ' '
                            else :
                                subfields_text = subfields_text + mysubfieldtext + ' '
                        else :
                            subfields_text = subfields_text + mysubfieldtext + ' '

                # enregistrement du champ et des indicateurs
                if (tag_erreur == 1):
                    fichier_text = fichier_text + '££S££' + myfield.attrib['tag'] + '££E££ ' + ind1 + ind2 + ' : '
                else:
                    fichier_text = fichier_text + myfield.attrib['tag'] + ' ' + ind1 + ind2 + ' : '
                
                # pour certains zones on surligne tout le champ
                if (all_erreur == 1):
                    fichier_text = fichier_text + '££S££' + subfields_text + '££E££\n'
                else:
                    fichier_text = fichier_text + subfields_text + '\n'

                # fin des sous champs

            # erreurs par manque d'élements
            if ((nb_101 == 0) & ((my008 == 'Tp5') | (my008 == 'Tb5'))):
                # print(file + ' ERREUR 101 manquante')
                # df.loc[df['idref'] == myidref, 'test_101'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 101: Il manque la langue d\'expression [TEST#DV]\n'
            if ((nb_102 == 0) & ((my008 == 'Tp5') | (my008 == 'Tb5'))):
                # print(file + ' ERREUR 102 manquante')
                # df.loc[df['idref'] == myidref, 'test_102'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 102: Il manque le pays [TEST#DW]\n'
            if ((nb_103 == 0) & (my008 == 'Tp5')):
                # print(file + ' ERREUR 103 manquante')
                # df.loc[df['idref'] == myidref, 'test_103'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 103: Il manque les dates de vie [TEST#DX]\n'
            if ((nb_103 == 0) & (my008 == 'Tp5') & (nb_200f > 0)):
                # print(file + ' ERREUR 103 manquante avec 200f')
                # df.loc[df['idref'] == myidref, 'test_103'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 103: Manque si le sous-champ 200 $f est présent [TEST#DY]\n'
            # Si champ 103, il doit y avoir 200 sous-champ $f
            if ((nb_103ab > 0) & (my008 == 'Tp5') & (nb_200f == 0)):
                # print(file + ' ERREUR 200 $f manquant')
                # df.loc[df['idref'] == myidref, 'test_200'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 200: Si les dates de vie sont indiquées en champ 103, elles doivent être répétées en 200 $f [TEST#DZ]\n'
            # Si champ 103, il doit y avoir 200 sous-champ $f partout
            if ((nb_103ab > 0) & (my008 == 'Tp5') & (nb_200 > 1) & (nb_200 > nb_200f)):
                # print(file + ' ERREUR 200 $f manquant')
                # df.loc[df['idref'] == myidref, 'test_200'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 200: Le sous-champ $f doit être identique sur les différents champs 200 [TEST#EI]\n'
            if ((nb_120 == 0) & (my008 == 'Tp5')):
                # print(file + ' ERREUR 120 manquante')
                # df.loc[df['idref'] == myidref, 'test_120'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 120: Il manque le genre [TEST#EA]\n'
            if ((nb_150 >0) & (nb_150b == 0) & (my008 == 'Tb5') & (nb_210_1x == 0)):
                # print(file + ' ERREUR 150 $b manquante')
                # df.loc[df['idref'] == myidref, 'test_150'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 150: Il manque le sous-champ 150 $b [TEST#EB]\n'
            # if (nb_810 == 0):
                # print(file + ' ERREUR 810 manquante')
                # # df.loc[df['idref'] == myidref, 'test_810'] = 'X'
                # nb_erreurs = nb_erreurs + 1
                # message_erreur = message_erreur + 'Champ 810: manquant\n'
            if (nb_810a == 0):
                # print(file + ' ERREUR 810a manquante : ' + file)
                # df.loc[df['idref'] == myidref, 'test_810'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + 'Champ 810: Il manque la source consultée avec profit [TEST#EC]\n'
            
            # erreurs par répétition
            myrepetitiontext, myrepetitionerror = repeatedSubstring(fichier_text)
            if (myrepetitionerror != ''):
                # print(file + ' ERREUR : ' + myerror)
                # df.loc[df['idref'] == myidref, 'test_champs_double'] = 'X'
                nb_erreurs = nb_erreurs + 1
                message_erreur = message_erreur + myrepetitionerror
                fichier_text = myrepetitiontext
                      
            # enregistrement du fichier final
            if (myfilesuffix1 != ''):
                myfilesuffix = myfilesuffix1
            elif (myfilesuffix2 != ''):
                myfilesuffix = myfilesuffix2
            else :
                myfilesuffix = ''
            if (myfilesuffix != '') :
                myfilesuffix = ''.join(i for i in myfilesuffix if i not in '/:*?<>|\"')
                # normalization : désactivée car perturbant de voir un autre nom
                # myfilesuffix = slugify(myfilesuffix)
                if (len(myfilesuffix) > 100):
                    myfilesuffix = myfilesuffix[0:100]
                    myfilesuffix = myfilesuffix + '---'
                myfilesuffix = myfilesuffix.strip()
                myfilesuffix = myfilesuffix.replace(' ', '_')
                if myfilesuffix.endswith('_'):
                    myfilesuffix = myfilesuffix[0:-1]
                if myfilesuffix.endswith('_'):
                    myfilesuffix = myfilesuffix[0:-1]
                if myfilesuffix.endswith('_'):
                    myfilesuffix = myfilesuffix[0:-1]
            if (nb_erreurs > 0):
                recs_avec_erreur = recs_avec_erreur + 1
                # tri des erreurs
                # print('erreurs : ' + str(nb_erreurs) + ' - lignes : ' + str(message_erreur.count('\n')))
                if (message_erreur.count('\n') > 1):
                    message_erreur_list = message_erreur.split('\n')
                    message_erreur_list_sorted = sorted(message_erreur_list)
                    message_erreur_sorted = '\n'.join(message_erreur_list_sorted)
                    fichier_text = '******************************************£SSS£' + message_erreur_sorted + '\n£EEE£******************************************\n' + fichier_text
                else :
                    fichier_text = '******************************************£SSS£\n' + message_erreur + '£EEE£******************************************\n' + fichier_text
                with io.open(pathout + file[:-4] + '_' + myfilesuffix + '_ERREUR.txt', 'w', encoding='utf8') as f:
                    f.write(fichier_text) 
                f.close()
            else:
                with io.open(pathout + file[:-4] + '_' + myfilesuffix + '.txt', 'w', encoding='utf8') as f:
                    f.write(fichier_text) 
                f.close()

    return recs_avec_erreur
    

# Créations
creations_erreur = processidref('creations')
print (madate2 + ' - Créations DONE - ids : ' + str(results_c) + ' - erreurs : ' + str(creations_erreur))

# Modifications
modifications_erreur = processidref('modifications')
print (madate2 + ' - Modifications DONE - ids : ' + str(results_m) + ' - erreurs : ' + str(modifications_erreur))

# Notification de recap
import smtplib
from email.message import EmailMessage
print ('notification email de recap lancée')
msg = EmailMessage()
# message pour les notifications
emailbody = 'Date : ' + madate1 + '\n'
emailbody = emailbody + 'Tentative : ' + str(tentative) + '\n'
emailbody = emailbody + 'Total de notices qui n\'ont pas pu être importées (timeout ou autre) : ' + str(results_e) + '\n'
if results_e > 0:
    emailbody = emailbody + '  - IDs : \n' + str(import_erreur)
emailbody = emailbody + 'Total de notices importées pour les créations : ' + str(results_c) + '\n'
emailbody = emailbody + '  - avec erreur trouvé : ' + str(creations_erreur) + '\n'
emailbody = emailbody + 'Total de notices importées pour les modifications : ' + str(results_m) + '\n'
emailbody = emailbody + '  - avec erreur trouvé : ' + str(modifications_erreur) + '\n'
msg.set_content(emailbody)
msg['Subject'] = 'Listages IdRef ' + madate1 
msg['From'] = 'noreply@votre_institution.ch'
msg['To'] = email_recap
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()
print('notification email de recap finalisée')
print('Fin du processus : ' + str(datetime.datetime.now()))

# Tout est OK -> enregistrement du fichier OK
with io.open(myfilein_ok, 'w', encoding='utf8') as f:
    f.write('Import idRef du ' + madate1 + ' OK')
f.close() 
# suppression du fichier d'erreur
os.remove(myfilein_error)
