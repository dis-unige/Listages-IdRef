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

//path to file
// ex : idref_notices_crees_20210219.txt
// ex : idref_notices_modifiees_20201208.txt
if (isset($_GET['folder']) && $_GET['folder']== "modifications") {
    $myfolder_text = " modifiée ";
    $montitre = "Notice IdRef " . $_GET['idref'] . " modifiée le " . substr($_GET['date'] , 6, 2) . "." . substr($_GET['date'], 4, 2) . "." . substr($_GET['date'], 0, 4);
    $myfile = "./par_date/modifications/" . $_GET['file'];
}
else {
    $myfolder_text = " créée ";
    $montitre = "Notice IdRef " . $_GET['idref'] . " créée le " . substr($_GET['date'] , 6, 2) . "." . substr($_GET['date'], 4, 2) . "." . substr($_GET['date'], 0, 4);
    $myfile = "./par_date/creations/" . $_GET['file'];
}

$listage = file_get_contents($myfile);
// echo "<br/>Fichier : " . $myfile . "<br/>\n";
if ($listage == "") {
    echo "<p style=\"font-color: red;\">Erreur - pas de contenu trouvé " . $myfolder_text . "</p>";
} else {
    print "<h4 class=\"text-primary\">" . $montitre . "</h4>\n";
    // print du fichier
    $listage = str_replace("<<", "&lt;&lt;", $listage);
    $listage = str_replace(">>", "&gt;&gt;", $listage);
    $listage = str_replace("<", "&lt;", $listage);
    $listage = str_replace(">", "&gt;", $listage);
    $listageprint = nl2br($listage);
    $listageprint = str_replace("£S£  £E£", "£S£&nbsp;&nbsp;£E£", $listageprint);
    $listageprint = str_replace("£SSS£", "<span style='background-color : #FFFF00'>", $listageprint);
    $listageprint = str_replace("££S££", "<span style='background-color : #FFFF00'>", $listageprint);
    $listageprint = str_replace("£EEE£", "</span>", $listageprint);
    $listageprint = str_replace("££E££", "</span>", $listageprint);
    $listageprint = str_replace("£S£", "<span style='background-color : #FFFF00'>", $listageprint);
    $listageprint = str_replace("£E£", "</span>", $listageprint);
    echo $listageprint;
}
echo "<hr/><br />";
echo "        </div>\n";
echo "  </body>\n";
echo "</html>\n";
?>