<?php
$user_mail = isset($_SERVER['mail']) ? strtolower($_SERVER['mail']) : '';
include "header.php";
echo "        <ul>\n";
echo "        <li><b><a href=\"liste.php?type=date&folder=creations\">Notices créées par date</a></b></li>\n";
echo "        <li><b><a href=\"liste.php?type=date&folder=modifications\">Notices modifiées par date</a></b></li>\n";
// echo "        <li><b><a href=\"liste.php?type=personne&folder=creations\">Notices créées par personne</a></b></li>\n";
// echo "        <li><b><a href=\"liste.php?type=personne&folder=modifications\">Notices modifiées par personne</a></b></li>\n";
// logs uniquement pour les admins
if ($user_mail == 'admin@votre_institution.ch') {
    echo "        <li><b><a href=\"logs/log.txt\">Logs</a></b></li>\n";
}
echo "        </ul>\n";
echo "        <hr style=\"border-top:1px dotted #ccc;\"/>\n";
echo "        <div class=\"col-md-12\">\n";

# pour idref listes par date seulement
$mytype = 'date';

# dossier par défaut : créations
if (isset($_GET['folder'])) {
    $myfolder = $_GET['folder'];
} else {            
    $myfolder = 'creations';
}
if ($myfolder == 'modifications') {
    $montitre = "Notices modifiées par date";
    $directory = "./par_date/modifications/";
} else {
    $montitre = "Notices créées par date";
    $directory = "./par_date/creations/";
}

# range des dates
$today = date("Y-m-d");
if (isset($_GET['year']) && ($_GET['year'] != date("Y"))) {
    $syear = $_GET['year'];
    $edate = $syear + 1 . '-01-01';
} else {
    $syear = date("Y");
    $edate = $today;
}

# liste de jours de l'année choisi
$sdate = $syear . '-01-01';
$period = new DatePeriod(
     new DateTime($sdate),
     new DateInterval('P1D'),
     new DateTime($edate)
);
$period = array_reverse(iterator_to_array($period));

# range des années précédents
$edate2 = date("Y") . '-12-31';
$period2 = new DatePeriod(
     new DateTime('2023-01-01'),
     new DateInterval('P1Y'),
     new DateTime($edate2)
);

# liste des années
foreach ($period2 as $key => $value) {
    echo "<a href=\"liste.php?type=" . $mytype . "&folder=" . $myfolder . "&year=" . $value->format('Y') . "\">" . $value->format('Y') . "</a> &nbsp;&nbsp; \n";
}

# affichage de la liste
echo "<h4 class=\"text-primary\">" . $montitre . " en " . $syear . "</h4>\n";
echo "<ul>\n";
foreach ($period as $key => $value) {
    // recherche de fichiers et des erreurs
    $madate = $value->format('Ymd');
    $nbfiles = 0;
    $nberreurs = 0;
    
    // iteration des fichiers par date
    $files = array();
    $dir = opendir($directory);
    while(false != ($file = readdir($dir))) {
        if(($file != ".") and ($file != "..") and ($file != "index.php") and (substr($file, 0, 8) == $madate)) {
            $nbfiles = $nbfiles + 1;
            if (substr($file, -10, 6) == "ERREUR") {
                $nberreurs = $nberreurs + 1;
            }
        }
    }
    if ($nbfiles > 0) {
        echo "<li><a href=\"date.php?folder=" . $myfolder . "&date=" . $value->format('Ymd') . "\">" . $value->format('d-m-Y') . " : " . $nbfiles . " notices et " . $nberreurs . " erreurs</a></li>\n";
    } else {
        echo "<li>" . $value->format('d-m-Y') . " : " . $nbfiles . " notices</li>\n";
    }
}
echo "</ul>\n";
echo "        </div>\n";
echo "  </body>\n";
echo "</html>\n";
?>