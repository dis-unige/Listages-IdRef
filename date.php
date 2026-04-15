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

$date = $_GET['date'];
$date2 = substr($date, 6, 2) . "-" . substr($date, 4, 2) . "-" . substr($date, 0, 4);

if ($_GET['folder'] == "creations") {
    $montitre = "Notices créées le " . $date2;
    $directory = "./par_date/creations/";
}
else {
    $montitre = "Notices modifiées le " . $date2;
    $directory = "./par_date/modifications/";
}

   
print "<h4 class=\"text-primary\">" . $montitre . "</h4>\n";
$files = array(array());
$dir = opendir($directory);
while(false != ($file = readdir($dir))) {
    if(($file != ".") and ($file != "..") and ($file != "index.php") and (substr($file, 0, 8) == $date)) {
        $files[] = [substr($file, 18), $file];
    }
}
// print de la liste pour une date
// ex : 20230511_269836519_ERREUR.txt
echo "";
echo "<ul>\n";
// tri alpha (contraire de natsort)
// rsort : sort inverse
sort($files);
foreach ($files as $file) {
    if (isset($file[1])) {
        $idref = substr($file[1], 9, 9);
        $name = substr($file[1], 18);
        $name = str_replace("_ERREUR", " - ERREUR", $name);
        $name = str_replace("_", " ", $name);
        $name = str_replace("---", "[...]", $name);
        $file_url = $file[1];
        $file_url = str_replace("&", "%26", $file_url);

        // $name = ucwords($name); // Uncomment if you want to capitalize words
        if ($name == ".txt") {
            $name = "IdRef " . $idref;
        } else {
            if (isset($_GET['folder']) && $_GET['folder'] != "creations" && $date < '20231120') {
                $name = "IdRef " . $idref . " - " . $name;
            }
        }
        $name = str_replace(" -  - ", " - ", $name);
        $name = str_replace(".txt", "", $name);

        if ($idref != '') {
            $type = isset($_GET['type']) ? $_GET['type'] : '';
            $folder = isset($_GET['folder']) ? $_GET['folder'] : '';
            echo "<li><a href=\"detail.php?type=" . $type . "&folder=" . $folder . "&date=" . $date . "&idref=" . $idref . "&file=" . $file_url . "\">" . $name . "</a></li>\n";
        }
    } 
}
echo "</ul>\n";

echo "        </div>\n";
echo "  </body>\n";
echo "</html>\n";
?>