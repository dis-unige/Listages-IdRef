# Listages pour les notices d'autorité IdRef

## Crédits
* Code : Pablo Iriarte, UNIGE, pablo.iriarte@unige.ch
* Tests de détection d'erreurs : Catherine Dietschi et Katia Martin
 
## Desrciption

Cet application se compose de deux élements

* **Un script python "api_listages_idref.py"** qui permet de :
  1. Importer chaque nuit les notices d'autorité IdRef créées et modifiées par une institution en exploitant le service Web de l'Abes (https://documentation.abes.fr/aideidrefdeveloppeur/index.html)
  2. Lancer une batterie de tests sur chaque notice importée et ajouter des marqueurs visuels pour faciliter la relecture

* **Une application Web** qui permet de :
  1. Afficher le nombre des notices par jour avec le nombre qui ont des erreurs [voir copie d'écran 1](screenshot_1.png)
  2. Afficher la liste des notices pour le jour choisi [voir copie d'écran 2](screenshot_2.png)
  3. Afficher la notice complète avec les erreurs éventuels trouvés [voir copie d'écran 3](screenshot_3.png)

## Installation

Cet outil n'utilise pas de base de données, uniquement des fichiers txt pour chaque notice importée. Son installation est donc très simple, elle nécessite python 3 pour le script d'import et PHP8 pour la partie Web. Le script python doit être ajouté au cron du serveur pour automatiser les imports chaque nuit
 
## Liste des tests effectués

| Code | Champ testé | Sous-champ testé | Test | Message | Notes | 
| --- | --- | --- | --- | --- | --- |
| TEST#AA | Tous | Tous | ('(' in texte) & (')' not in texte) | Champ [numéro du champ] - Test sur les caractères: nombre de ( différent du nombre de ) |  | 
| TEST#AB | Tous | Tous | (')' in texte) & ('(' not in texte) | Champ [numéro du champ] - Test sur les caractères: nombre de ( différent du nombre de ) |  | 
| TEST#AC | Tous | Tous | texte.count('(') != texte.count(')') | Champ [numéro du champ] - Test sur les caractères: nombre de ( différent du nombre de ) |  | 
| TEST#AD | Tous | Tous | ('[' in texte) & (']' not in texte) | Champ [numéro du champ] - Test sur les caractères: nombre de [ différent du nombre de ] |  | 
| TEST#AE | Tous | Tous | (']' in texte) & ('[' not in texte) | Champ [numéro du champ] - Test sur les caractères: nombre de [ différent du nombre de ] |  | 
| TEST#AF | Tous | Tous | texte.count('[') != texte.count(']') | Champ [numéro du champ] - Test sur les caractères: nombre de [ différent du nombre de ] |  | 
| TEST#AG | Tous | Tous | texte.count('"') % 2 != 0 | Champ [numéro du champ] - Test sur les caractères: nombre de " impair |  | 
| TEST#AH | Tous | Tous | "' \| ' in texte" | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (0009) tabulation |  | 
| TEST#AI | Tous | Tous | u'\u200E' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (200E) marque gauche à droite |  | 
| TEST#AJ | Tous | Tous | u'\u200F' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (200F) marque droite à gauche |  | 
| TEST#AK | Tous | Tous | u'\u202A' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (202A) bloc gauche à droite |  | 
| TEST#AL | Tous | Tous | u'\u202B' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (202B) bloc droite à gauche |  | 
| TEST#AM | Tous | Tous | u'\u202C' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (202C) marque PDF |  | 
| TEST#AN | Tous | Tous | u'\u0098' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (0098) marque début de chaîne |  | 
| TEST#AO | Tous | Tous | u'\u009C' in texte | Champ [numéro du champ] - Caractères invisibles: Merci de supprimer (009C) marque fin de chaîne |  | 
| TEST#AP | Tous | Tous | u'\u2019' in texte | Champ [numéro du champ] - Caractères illégaux: Merci de remplacer l'apostrophe ’ par la touche correspondante du clavier |  | 
| TEST#AQ | Tous | Tous | u'\u2026' in texte | Champ [numéro du champ] - Caractères illégaux: Merci de remplacer le point de suspension … par la touche correspondante du clavier |  | 
| TEST#AR | Tous | Tous | u'\u2013' in texte | Champ [numéro du champ] - Caractères illégaux: Merci de remplacer le tiret demi-cadratin – par la touche correspondante du clavier |  | 
| TEST#AS | Tous | Tous | u'\u2014' in texte | Champ [numéro du champ] - Caractères illégaux: Merci de remplacer le tiret cadratin — par la touche correspondante du clavier |  | 
| TEST#AT | Tous sauf 103 | Tous | texte.endswith(' ') | Champ [numéro du champ]: Merci de supprimer l'espace de fin |  | 
| TEST#AU | Tous sauf 103 | Tous | texte.startswith(' ') | Champ [numéro du champ]: Merci de supprimer l'espace de début |  | 
| TEST#AV | Tous sauf 100 et 103 | Tous | '  ' in texte | Champ [numéro du champ]: Merci de corriger l'espace à double |  | 
| TEST#AW | Tous | Tous | ' ,' in texte | Champ [numéro du champ]: Merci de corriger l'espace avant la virgule |  | 
| TEST#AX | Tous | Tous | '<<' in texte | Champ [numéro du champ]: Merci de supprimer les << |  | 
| TEST#AY | Tous | Tous | '>>' in texte | Champ [numéro du champ]: Merci de supprimer les >> |  | 
| TEST#AZ | 103 | Tous | 'x' in texte | Champ 103: Merci de corriger en X majuscule |  | 
| TEST#BA | 103 | Tous | ('.' in texte) \| ('-' in texte) | Champ 103: Si on ne connaît pas la date précise, on remplace les chiffres par des X |  | 
| TEST#BB | 103 | Tous | re.match(r'( )?([0-9X\?]+( )?)', texte) is None | Champ 103: seulement chiffres, X ou ? admis |  | 
| TEST#BC | 103 | Tous | (re.match(r'([1-2][0-9][0-9][0-9][0-9][0-9][0-9][0-9])', texte) is not None) & (((int(texte[4:6]) > 12) \| (int(texte[6:8]) > 31)) | Champ 103: Date à vérifier, le mois ne peut aller au-delà de 12, le jour au-delà de 31 |  | 
| TEST#BD | 200 | $a | (ind2 == '1') & (nb_200b == 0) | Champ 200: Il manque le sous-champ $b prénom ou corriger « Nom entré au prénom ou dans l'ordre direct » |  | 
| TEST#BE | 200 | $b | (ind2 == '0') & (nb_200b > 0) | Champ 200: Seul le sous-champ $a est autorisé ou corriger « Nom entré au patronyme » |  | 
| TEST#BF | 200 | $a | ',' in texte | Champ 200: Le sous-champ $a ne doit pas contenir de virgule |  | 
| TEST#BG | 200 | $b | re.match(r'.*[A-Z]\.[A-Z]\.', texte) is not None | Champ 200: Merci de rajouter un espace entre les initiales |  | 
| TEST#BH | 200 | $b | re.match(r'.*[A-Z]$', texte) is not None | Champ 200: Une initiale doit se terminer par un point |  | 
| TEST#BI | 200 | $b | re.match(r'.*[A-Z]\. - [A-Z]\.', texte) is not None | Champ 200: Merci de supprimer l'espace en trop entre l'initiale et le tiret |  | 
| TEST#BJ | 200 | $b | ',' in texte | Champ 200: le sous champ $b ne doit pas contenir de virgule |  | 
| TEST#BK | 200 | $c | re.match(r'^( )?[A-Z].*', texte) is not None | Champ 200: Le sous-champ $c doit généralement commencer par une minuscule |  | 
| TEST#BL | 200 | $f | ' - ' in texte | Champ 200: Il ne doit pas y avoir d'espace avant et après le tiret dans le sous-champ $f |  | 
| TEST#BM | 200 | $f | (champ_103a == '19XX') & (champ_103b == '') & (texte != '19..-....') | Champ 200: Le sous-champ $f doit être 19..-.... Ne pas tenir compte du message si la date est incertaine et qu'il y a un point d'interrogation en $f  |  | 
| TEST#BN | 200 | $f | (champ_103a != '19XX') & (texte == '19..') | Champ 103:  Le champ 103 doit être 19XX |  | 
| TEST#BO | 200 | $f | (re.match(r'[1-2][0-9][0-9][0-9]\?', champ_103a) is not None) & (champ_103b == '') & (texte != (champ_103a + '-....')) | Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa |  | 
| TEST#BP | 200 | $f | (re.match(r'[1-2][0-9][0-9][0-9]+$', champ_103a) is not None) & (champ_103b == '') & (texte != (champ_103a[0:4] + '-....')) | Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa |  | 
| TEST#BQ | 200 | $f | (re.match(r'[1-2][0-9][0-9][0-9]+', fmy103a) is not None) & (re.match(r'[1-2][0-9][0-9][0-9]+', fmy103b) is not None) & (texte != (fmy103a + '-' + fmy103b)) & (texte != (fmy103a[0:4] + '-' + fmy103b[0:4])) | Champ 200: Les dates en sous-champ $f ne correspondent pas aux dates du champ 103 ou vice versa, ou il manque en $f .... (4 points) Ne pas tenir compte du message si la date est incertaine et qu'il y a un point d'interrogation en $f  |  | 
| TEST#BR | 200 | $c | ('(' in texte) \| (')' in texte) | Champ 200: Le sous-champ $c ne doit pas contenir de parenthèses | Test supprimé (fusioné en #EL) | 
| TEST#BS | 200 | $f | ('(' in texte) \| (')' in texte) | Champ 200: Le sous-champ $f ne doit pas contenir de parenthèses | Test supprimé (fusioné en #EL) | 
| TEST#BT | 400 | $a | ',' in texte | Champ 400: Le sous-champ $a ne doit pas contenir de virgule |  | 
| TEST#BU | 400 | $b | re.match(r'.*[A-Z]\.[A-Z]\.', texte) is not None | Champ 400: Merci de rajouter un espace entre les initiales |  | 
| TEST#BV | 400 | $b | re.match(r'.*[A-Z]$', texte) is not None | Champ 400:  Une initiale doit se terminer par un point |  | 
| TEST#BW | 400 | $b | re.match(r'.*[A-Z]\. - [A-Z]\.', texte) is not None | Champ 400: Merci de supprimer l'espace en trop entre l'initiale et le tiret |  | 
| TEST#BX | 400 | $b | ',' in texte | Champ 400: le sous champ $b ne doit pas contenir de virgule |  | 
| TEST#BY | 400 | $c |  | Champ 400: La forme rejetée ne contient généralement pas de qualificatif (sous-champ $c) |  | 
| TEST#BZ | 400 | $c | re.match(r'^( )?[A-Z].*', texte) is not None | Champ 400: Le sous-champ $c doit généralement commencer par une minuscule |  | 
| TEST#CA | 400 | $f |  | Champ 400: La forme rejetée ne doit pas contenir de dates de vie (sous-champ $f) |  | 
| TEST#CB | 400 | $c | ('(' in texte) \| (')' in texte) | Champ 400: Le sous-champ $c ne doit pas contenir de parenthèses | Test supprimé (fusioné en #EL) | 
| TEST#CC | 400 | $f | ('(' in texte) \| (')' in texte) | Champ 400: Le sous-champ $f ne doit pas contenir de parenthèses | Test supprimé (fusioné en #EL) | 
| TEST#CD | 700 | $a | (ind2 == '1') & (nb_700b == 0) | Champ 700: Il manque le sous-champ $b prénom ou corriger « Nom entré au prénom ou dans l'ordre direct |  | 
| TEST#CE | 700 | $b | (ind2 == '0') & (nb_700b > 0) | Champ 700: Seul le sous-champ $a est autorisé ou corriger « Nom entré au patronyme » |  | 
| TEST#CF | 700 | $a | ',' in texte | Champ 700: Le sous-champ $a ne doit pas contenir de virgule |  | 
| TEST#CG | 700 | $b | re.match(r'.*[A-Z]\.[A-Z]\.', texte) is not None | Champ 700: Merci de rajouter un espace entre les initiales |  | 
| TEST#CH | 700 | $b | re.match(r'.*[A-Z]$', texte) is not None | Champ 700: Une initiale doit se terminer par un point |  | 
| TEST#CI | 700 | $b | re.match(r'.*[A-Z]\. - [A-Z]\.', texte) is not None | Champ 700: Merci de supprimer l'espace en trop entre l'initiale et le tiret |  | 
| TEST#CJ | 700 | $b | ',' in texte | Champ 700: le sous champ $b ne doit pas contenir de virgule |  | 
| TEST#CK | 700 | $c | re.match(r'^( )?[A-Z].*', texte) is not None | Champ 700: Le sous-champ $c doit généralement commencer par une minuscule |  | 
| TEST#CL | 700 | $f | ' - ' in texte | Champ 700: Il ne doit pas y avoir d'espace avant et après le tiret dans le sous-champ $f |  | 
| TEST#CM | 700 | $c | ('(' in texte) \| (')' in texte) | Champ 700: Le sous-champ $c ne doit pas contenir de parenthèses | Test supprimé (fusioné en #EL) | 
| TEST#CN | 700 | $f | ('(' in texte) \| (')' in texte) | Champ 700: Le sous-champ $f ne doit pas contenir de parenthèses | Test supprimé (fusioné en #EL) | 
| TEST#CO | 810 | Tous | (nb_033_035_899 == 0) & ('http' in texte) & (re.match(r'.*([1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])', texte) is None) | Champ 810: Il manque la date de consultation ou la date de consultation doit être aaaa-mm-jj |  | 
| TEST#CP | 810 | Tous | (nb_033_035_899 == 0) & ('http' in texte) & (re.match(r'.*([1-2][0-9][0-9][0-9] - [0-9][0-9] - [0-9][0-9])', texte) is not None) | Champ 810: Il n'y a pas d'espace avant et après le tiret dans la date de consultation |  | 
| TEST#CQ | 810 | Tous | (nb_033_035_899 == 0) & ('http' in texte) & ('viaf.org/viaf' in texte) | Champ 810: Le lien VIAF doit correspondre à une bibliothèque précise, il commence par http://viaf.org/processed/ |  | 
| TEST#CR | 810 | Tous | (nb_033_035_899 == 0) & ('http' in texte) & ('viaf.org' in texte) & (re.match(r'VIAF - ([A-zÀ-ú0-9-\' ]+) - .*', texte) is None) | Champ 810: La source doit être mentionnée sous la forme : VIAF - Bibliothèque source - http://viaf.org/processed..., aaaa-mm-jj |  | 
| TEST#CS | 810 | Tous | (nb_033_035_899 == 0) & ('http' not in texte) & (re.match(r'.*, ([\[\) ])?([1-2][0-9]{3})([\]\) ])?', texte) is None) | Champ 810: la date de publication est-elle bien présente? |  | 
| TEST#CT | 810 | Tous | (nb_033_035_899 == 0) & ('http' not in texte) & (texte.endswith('.')) | Champ 810: La source ne doit pas contenir de point final |  | 
| TEST#CU | 810 | Tous | (nb_033_035_899 == 0) & ('http' not in texte) & (('\|b' in texte) \| ('\|c' in texte) \| ('\$\$b' in texte) \| ('\$\$c' in texte)) | Champ 810: La source ne doit pas contenir de codification |  | 
| TEST#CV | 100 à 899 | Champ entier | [champ répété en entier] | Champ [numéro du champ]: Champ à double |  | 
| TEST#CW | 100 à 899 | Tous | [sous-champ répété en entier] | Champ [numéro du champ]: Sous-champ $[lettre du sous-champ] à double |  | 
| TEST#CX | 210 |  | (champ_008 == 'Tb5') & (ind1 == '1') & (ind2 == '1') | Champ 210: Un congrès n'est jamais introduit sous un nom de lieu. Soit le premier indicateur (collectivité 0 ou congrès 1) est faux, soit le deuxième indicateur est faux (nom de lieu 1 ou ordre direct 2) |  | 
| TEST#CY1 | 210 |  | (champ_008 == 'Tb5') & (nb_210dfe > 0) & (nb_210f > 0) & (nb_210b == 0) & ((ind1 != '1') \| (ind2 != '2')) | Champ 210: Corriger le nom de type « collectivité » en « congrès » s’il s’agit bien d’un congrès dans l’ordre direct |  | 
| TEST#CY2 | 210 |  | (champ_008 == 'Tb5') & (nb_210dfe > 0) & (nb_210f = 0) & (nb_210b == 0) & ((ind1 != '1') \| (ind2 != '2')) | Champ 210: Corriger le nom de type « collectivité » en « congrès ». S’il ne s’agit pas d’un congrès et que la date qualifie la collectivité, elle se met en $c |  | 
| TEST#CZ | 210, 410 et 710 |  | (champ_008 == 'Tb5') & (ind1 == '0') & (ind2 == '2') & (nb_210b > 0) | Champ X10: Corriger le 2e indicateur en 1 (nom entré sous un nom de lieu ou de ressort), sauf si le $b contient la localisation de la collectivité, elle doit être codifiée en $c  |  | 
| TEST#DA | 210, 410, 510 et 710 |  | (champ_008 == 'Tb5') & (ind1 == '0') & (ind2 == '1') & (nb_210b == 0) | Champ X10: Corriger le 2e indicateur en 0 sauf si lieu géographique (nom entré dans l'ordre direct) |  | 
| TEST#DB | 410 |  | (champ_008 == 'Tb5') & (ind1 == '1') & (ind2 == '1') | Champ 410: Un congrès n'est jamais introduit sous un nom de lieu. Soit le premier indicateur (collectivité 0 ou congrès 1) est faux, soit le deuxième indicateur est faux (nom de lieu 1 ou ordre direct 2) |  | 
| TEST#DC | 410 | $d$e$f | (champ_008 == 'Tb5') & (nb_410dfe > 0) & (nb_410b == 0) & ((ind1 != '1') \| (ind2 != '2')) | Champ 410: corriger le nom de type « collectivité » en « congrès » |  | 
| TEST#DD | 103 | $c | (champ_008 == 'Tb5') | Champ 103: Le sous-champs $c n'est pas autorisé |  | 
| TEST#DE | 103 | $d | (champ_008 == 'Tb5') | Champ 103: Le sous-champs $d n'est pas autorisé |  | 
| TEST#DF | 150 | $b | (champ_008 == 'Tb5') & (nb_210_1x > 0) & (mysubfieldtext != '1') | Champ 150: S'il s'agit d'un congrès (210 1x), le $b doit être 1 |  | 
| TEST#DG | 210 | $b | (champ_008 == 'Tb5') & (nb_210dfe > 0) & (nb_210b > 0) & (ind1 == '0') & (ind2 == '2') & (nb_150b == 0) | Champ 210: Il manque le champ 150, sous-champ $b 1 (l'entité décrite est un congrès) |  | 
| TEST#DH | 150 | $b | (champ_008 == 'Tb5') & (nb_210dfe > 0) & (nb_210b > 0) & (ind1 == '0') & (ind2 == '2') | Champ 150:  Corriger le sous-champ $b 1 (l'entité décrite est un congrès) |  | 
| TEST#DI | 210 | $b | (champ_008 == 'Tb5') & (ind1 == '1') & (ind2 == '2') | Champ 210: Le sous-champ $b n'est pas autorisé ou corriger « Nom entré sous un nom de lieu » |  | 
| TEST#DJ | 215 | $a$x$z | (champ_008 == 'Tg5') & (re.match(r'[A-zÀ-ú0-9 \,\(\)\;]+', mysubfieldtext) is None) | Champ 215: $[lettre du sous-champ] seuls la virgule, les parenthèses et le point-virgule sont autorisés |  | 
| TEST#DK | 215 | $a$x$z | (champ_008 == 'Tg5') & (re.match(r'[A-zÀ-ú0-9 \,\(\)\;]+', mysubfieldtext) is None) & mysubfieldtext.startswith('@') | Champ 215: $[lettre du sous-champ] le caractère @ en début de sous-champ n'est pas autorisé |  | 
| TEST#DL | 340 | $a | ('\|b' in mysubfieldtext) \| ('\|c' in mysubfieldtext) \| ('\$\$b' in mysubfieldtext) \| ('\$\$c' in mysubfieldtext) | Champ 340: La note ne doit pas contenir de codification |  | 
| TEST#DM | 340 | $a | mysubfieldtext[-1] == '.' | Champ 340: La note ne doit pas contenir de point final |  | 
| TEST#DN | 356 | $a | ('\|b' in mysubfieldtext) \| ('\|c' in mysubfieldtext) \| ('\$\$b' in mysubfieldtext) \| ('\$\$c' in mysubfieldtext) | Champ 356: La note ne doit pas contenir de codification |  | 
| TEST#DO | 356 | $a | mysubfieldtext[-1] == '.' | Champ 356: La note ne doit pas contenir de point final |  | 
| TEST#DP | 410 | $b | (champ_008 == 'Tb5') & (ind1 == '1') & (ind2 == '2') | Champ 410: Le sous-champ $b n'est pas autorisé ou corriger « Nom entré sous un nom de lieu » |  | 
| TEST#DQ | 415 | $a$x$z | (champ_008 == 'Tg5') & (re.match(r'[A-zÀ-ú0-9 \,\(\)\;]+', mysubfieldtext) is None) | Champ 415: $[lettre du sous-champ] seuls la virgule, les parenthèses et le point-virgule sont autorisés |  | 
| TEST#DR | 415 | $a$x$z | (champ_008 == 'Tg5') & (re.match(r'[A-zÀ-ú0-9 \,\(\)\;]+', mysubfieldtext) is None) & mysubfieldtext.startswith('@') | Champ 415: $[lettre du sous-champ] le caractère @ en début de sous-champ n'est pas autorisé |  | 
| TEST#DS | 500 | $b | ',' in mysubfieldtext | Champ 500: le sous champ $b ne doit pas contenir de virgule |  | 
| TEST#DT | 715 |  | (champ_008 == 'Tg5') | Champ 715: il n'est pas autorisé pour les noms géographiques |  | 
| TEST#DU | Tous | Tous | [sous-champ vide] | Champ vide: [numéro du champ] [ind1] [ind2] $[lettre du sous-champ] | Test supprimé | 
| TEST#DV | 101 |  | (nb_101 == 0) & ((champ_008 == 'Tp5') \| (champ_008 == 'Tb5')) | Champ 101: Il manque la langue d'expression |  | 
| TEST#DW | 102 |  | (nb_102 == 0) & ((champ_008 == 'Tp5') \| (champ_008 == 'Tb5')) | Champ 102: Il manque le pays |  | 
| TEST#DX | 103 |  | (nb_103 == 0) & (champ_008 == 'Tp5') | Champ 103: Il manque les dates de vie |  | 
| TEST#DY | 103 |  | (nb_103 == 0) & (champ_008 == 'Tp5') & (nb_200f > 0) | Champ 103: Manque si le sous-champ 200 $f est présent |  | 
| TEST#DZ | 103 |  | (nb_103ab > 0) & (my008 == 'Tp5') & (nb_200f == 0) | Champ 200: Si les dates de vie sont indiquées en champ 103, elles doivent être répétées en 200 $f |  | 
| TEST#EA | 120 |  | (nb_120 == 0) & (champ_008 == 'Tp5') | Champ 120: Il manque le genre |  | 
| TEST#EB | 150 | $b | (nb_150b == 0) & (champ_008 == 'Tb5') & (nb_210_1x == 0) | Champ 150: Il manque le sous-champ 150 $b |  | 
| TEST#EC | 810 | $a | nb_810a == 0 | Champ 810: Il manque la source consultée avec profit |  | 
| TEST#ED | 815 | $a | re.match(r'.*([1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])') is none | Champ 815: Il manque la date de consultation ou la date de consultation doit être aaaa-mm-jj |  | 
| TEST#EE | 815 | $a | re.match(r'.*([1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])') is not none | Champ 815: Il n\'y a pas d\'espace avant et après le tiret dans la date de consultation |  | 
| TEST#EF | 815 | $a | 'viaf.org/viaf' | Champ 815: Le lien VIAF doit correspondre à une bibliothèque précise, il commence par http://viaf.org/processed/ |  | 
| TEST#EG | 815 | $a | `'viaf.org' & re.match(r'VIAF - ([A-zÀ-ú0-9-\' ]+) - .*') is none | Champ 815: La source doit être mentionnée sous la forme : VIAF - Bibliothèque source - http://viaf.org/processed..., aaaa-mm-jj |  | 
| TEST#EH | 710 |  | ((my008 == 'Tp5') & (myfield.attrib['tag'] == '710')) | Champ 710: Merci de vérifier qu\'il s\'agit bien d\'une collectivité  |  | 
| TEST#EI | 200 | $f | ((nb_103ab > 0) & (my008 == 'Tp5') & (nb_200 > nb_200f)) ; (len(fmy200_fs) > 1 & len(set(fmy200_fs)) == 1) | Champ 200: Le sous-champ $f doit être identique sur les différents champs 200 |  | 
| TEST#EJ | 035 | $2 | $a = 'A[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]' & $2 != RERO OR $2 = RERO & $a != 'A[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]' | Champ 035: Le champ n\'a pas le bon format $a A[9 chiffres] $2 RERO |  | 
| TEST#EK | 210, 410, 710 | $d $e $f | (my210d_position > my210f_position) \| (my210d_position > my210f_position) \| (my210f_position > my210e_position) | Champ [210, 410, 710]: L'ordre des sous-champs doit être $d $f $e |  | 
| TEST#EL | 200, 210, 400, 410, 700, 710 | $a $b | ('(' in texte) \| (')' in texte) | Champ [200, 210, 400, 410, 700, 710]: Le sous-champ [$a, $b, $c, $f] ne doit pas contenir de parenthèses |  | 
