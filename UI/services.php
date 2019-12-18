<!DOCTYPE HTML>
<!--
	Cube by FreeHTML5.co
	Twitter: http://twitter.com/gettemplateco
	URL: http://freehtml5.co
-->
<html>
	<head>
	<?php include("head.html"); ?>
	<!-- jQuery -->
	<script src="js/jquery.min.js"></script>
	<!-- jQuery Easing -->
	<script src="js/jquery.easing.1.3.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/victor/1.1.0/victor.min.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/pixi.js/5.1.1/pixi.min.js"></script>


	</head>
	<body>

	<div class="gtco-loader"></div>

	<div id="page">

	<?php include("nav.html"); ?>

<?php

$ip = "127.0.0.1";
$port = 1111;
$req = '{"type":"here", "req-id":"test","devices":["*"]};{"type":"here", "req-id":"test","devices":["2c:fd:a1:9d:ec:c9"]};exit;';
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

$size = $reponse_JSON[0]->info->quantity->devices;
 ?>

		<div class="gtco-services gtco-section">
			<div class="gtco-container">

					<div class="col-md-8 col-md-offset-2 gtco-heading text-center">
						<?php
						if ( $reponse_JSON[1]->type == "yep"){
						  ?>
							<h4>
								<img style="width: 48px;" src="images/eveson.png"/>
								Evenson mobile phone is active nearby !!
							</h4>
						<?php
						}
						?>
						<h2>Affluence</h2>
						<h2><?php echo $size ?></h2>
					</div>

			</div>
		</div>


		<div id="app">
			<script>let size = <?php echo $size ?>; </script>
			<script src="js/crowd.js"></script>
		</div>



		<script>
			window.setInterval(reload, 10000);
			function reload(){
				 location.reload();
			}
		</script>

		<style>
		body{
			min-height: 3000px;
		}
			canvas {
			display: block;
			}
		</style>


	<div class="gototop js-top">
		<a href="#" class="js-gotop"><i class="icon-arrow-up"></i></a>
	</div>


	<!-- Bootstrap -->
	<script src="js/bootstrap.min.js"></script>
	<!-- Waypoints -->
	<script src="js/jquery.waypoints.min.js"></script>
	<!-- Carousel -->
	<script src="js/owl.carousel.min.js"></script>
	<!-- Magnific Popup -->
	<script src="js/jquery.magnific-popup.min.js"></script>
	<script src="js/magnific-popup-options.js"></script>
	<!-- Main -->
	<script src="js/main.js"></script>

	<script src="js/modernizr-2.6.2.min.js"></script>



	</body>
</html>
