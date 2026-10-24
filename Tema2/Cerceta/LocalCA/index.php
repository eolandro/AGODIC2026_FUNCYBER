<?php
// Rutas de comprobación
$certFile = 'C:/xampp/apache/conf/ssl.crt/cerceta2.cerceta.local.pem';
$keyFile  = 'C:/xampp/apache/conf/ssl.key/cerceta2.cerceta.local-key.pem';

// Verificación de existencia de archivos en el servidor
if (!file_exists($certFile) || !file_exists($keyFile)) {
    error_log("Aviso: No se encontraron los archivos SSL (.crt o .key) en la ruta especificada.");
}

// Recibe el nombre por URL o usa "Mundo" por defecto
$name = isset($_GET['name']) ? htmlspecialchars($_GET['name']) : 'Mundo';

// Muestra el saludo
echo "<b>Hello " . $name . "</b>!";
?>