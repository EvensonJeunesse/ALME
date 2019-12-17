<?php

$ip = "127.0.0.1";
$port = 1111;
$req = '{"type":"here", "req-id":"test","devices":["*"]};exit;';
$req_separator = ";";
/*
$fp = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$fp) {
    echo "$errstr ($errno)<br />\n";
} else {
    fwrite($fp, $request);
    while (!feof($fp)) {
        echo fgets($fp, 5);
    }
    echo fgets($fp, 5);
    fclose($fp);
}
*/


function GET($host_, $port_, $request_){
    $response = NULL;

    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    if(!is_resource($socket)) onSocketFailure("Failed to create socket");

    socket_connect($socket, $host_,$port_)
            or onSocketFailure("Failed to connect to $host_:$port_", $socket);


    socket_write($socket, $request_."\r\n");


    while(true) {
        // read a line from the socket
        $line = socket_read($socket, 1, PHP_NORMAL_READ);
        if(substr($line, -1) === "\r") {
            break;
            socket_read($socket, 1, PHP_BINARY_READ);
        }
        $response  = $response.$line;
    }

    socket_close($socket);
     return $response;
}



$reponses_JSON =  array();
$result = GET($ip, $port, $req);
if(!$result) die("No response receive");

$responses = explode($req_separator, $result);

foreach ($responses as $response) {
  try{
    //echo $response;
    $object = json_decode($response);
    $reponse_JSON[] = $object;
  }catch (Exception $e) {
        echo 'Caught exception: ',  $e->getMessage(), "\n";
        die("Unable to convert  a response to JSON");
    }
}

//var_dump($reponse_JSON);

 ?>

<div>
  <?
</div>
