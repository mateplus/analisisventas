//variables globales para cambiarlas con eventos

//escalas para las ventas trimestrales
var configTrimestral = {
        top:10,
        columnWidth: 170,
        columnHeight: 25,
        columnGap: 5,
        padding: 30,
        width:0,
        height:260,
        marginleft:5,
		color:1,
        tituloX:"Ventas",
        tituloY:"Trimestres",
        tituloChart:"VENTAS TRIMESTRAL",
        trimestres:[1,2,3,4]
    };

var xtrim = d3.scaleLinear()
       .range([0,configTrimestral.columnWidth])
       .domain([0, 500]);
  var ejeXtrim = d3.axisBottom()
        .scale(xtrim)
        .tickSizeInner(5)
        .tickSizeOuter(0)
        .ticks(5);
var ytrim=d3.scaleBand()
        .domain(configTrimestral.trimestres)
        .rangeRound([configTrimestral.height - configTrimestral.padding *2 ,0 ]);

var ejeYtrim = d3.axisLeft()
        .scale(ytrim)
        .tickSizeInner(5)
        .tickSizeOuter(10)
        .tickPadding(10);


function Graficar(){
    //console.debug("estoy en el script");
    //console.debug(datomes);
    //barras();
    VentasxAnio();
    VentasMensuales();
    GraficaVentasTrimestrales();
}

//pinta mas fuerte
function SeleccionaTrace(key){

    var svg =d3.select( '#svg_mes');
    svg.selectAll("path")
        .transition()
        .duration(750)
        .each(function(d,i){
            if(d3.select(this).attr("data-legend")!= key){
                d3.select(this).style("opacity",0.1);
            }else{
                d3.select(this).style("opacity",1);
            }
        });
}

//prepara los datos para graficar por trismestre
function ActualizaVentasTrimestrales(key,color){
    //con los mismos detos de ventas mensuales se realiza una doble agrupacion
    //utilizando d3.nest
    //el arcivo resultante ha sido necesario tratarlo un poco para que sea compatible con
    //nuestros graficos, la ventaja de realizar de esta manera es que la respuesta sera mas rapida
    //al no saturar el acceso a al base de datos

    var ventasxtrimestre=d3.nest()
        .key(function(d){return d.Anio})
        .key(function(d){
			return d.trimestre;
		})
        .rollup(function(v){return d3.sum(v, function(d){return d.venta;}    ) } )
        .object(datomes);

    var v=[];
    var cont=0;
    var text=""
    for (i = 1; i <= 4; i++) {
        if (ventasxtrimestre[key][i] === undefined || ventasxtrimestre[key][i] === null) {
            text = text +  '{"trimestre":' + i   + ',"valor":0},'
        }else{
            //console.log(ventasxtrimestre[key][i]);
            v[cont] = ventasxtrimestre[key][i];

            text = text +  '{"trimestre":' + i   + ',"valor":' +  ventasxtrimestre[key][i] + "},"
            cont++;
        }
    }
    var VENTA_MAX =Math.max.apply(null, v);
   var _format = d3.format("$,.2f");
    //console.log( text.substr(0,text.length-1) );



    var datosT = JSON.parse(  "[" +  text.substr(0,text.length-1) + "]" );

    //cambiamos el eje del dominio de x
    xtrim.domain([0,VENTA_MAX]);
    ejeXtrim.ticks(5);


   var svg = d3.select('#svg_trimestre');
   // var svg = d3.select("'#vxtrimestre'").transition();
    svg.selectAll("#ejeX")
        .transition()
        .duration(750)
        .call(ejeXtrim);


      svg.selectAll("rect")
      .data(datosT)
          .transition()
          .duration(750)
          .attr("height", configTrimestral.columnHeight )
          .attr("width", function(d,i) { return  xtrim(d.valor) })
          .attr("y", function(d,i) {
             return ytrim(d.trimestre) + configTrimestral.padding + 5;
           })
          .attr("x", configTrimestral.padding + configTrimestral.marginleft +15 )
          .attr("fill",  color)
          .attr("data-trimestre",function(d,i){return d.trimeste } )
          .attr("data-valor",function(d,i){return d.valor } );

}

//en esta funcion de grea el svg
function GraficaVentasTrimestrales(){


    var NUM_COLUMNAS = 4;
   configTrimestral.width =configTrimestral.columnWidth+ configTrimestral.padding*2;

   //configTrimestral.height= 260
   // NUM_COLUMNAS * (configTrimestral.columnHeight + configTrimestral.columnGap) + (2*configTrimestral.padding) + 50;

  // console.log(config.width);
  //  console.log(config.height);

    var svg = d3.select('#vxtrimestre')
        .append('svg')
        .attr("width", configTrimestral.width)
        .attr("height", configTrimestral.height)
        .attr("id","svg_trimestre")
		.append("g")
		.attr("transform", "translate(" +configTrimestral.marginleft + "," + configTrimestral.top  + ")");

           // now add titles to the axes
        svg.append("g")
            .attr("class", "eje")
            .attr("id","ejeY")
            .attr("transform", "translate(" + (configTrimestral.marginleft + configTrimestral.padding)  + "," +  (configTrimestral.padding -15) + " )")
            .call(ejeYtrim);



    svg.append("g")
        .attr("class", "eje")
        .attr("id","ejeX")
        .attr("transform", "translate(" + (configTrimestral.marginleft + configTrimestral.padding)  + "," +  (configTrimestral.width -configTrimestral.padding+15) + " )")
        .call(ejeXtrim);

    //vamos acargar los datos porque luego solo modificamos los tama;os

    datosT =JSON.parse('[{"trimestre":1,"valor":0},{"trimestre":2,"valor":0},{"trimestre":3,"valor":0},{"trimestre":4,"valor":0}]');

       var tooltip = d3.tip()
            .attr('class', 'tooltip')
            .offset([-10, 0])
            .html(function(d) {
                return "<strong>" + d.trimestre + "</strong><br> ventas: " + _format(+d.valor);
            });


    svg.selectAll("rect")
        .data(datosT)
        .enter().append("rect")
        .attr("height", configTrimestral.columnHeight )
        .attr("width", function(d,i) { return  xtrim(d.valor) })
        .attr("y", function(d,i) {
             return ytrim(d.trimestre) + configTrimestral.padding + 5;
         })
        .attr("x", configTrimestral.padding + configTrimestral.marginleft +15 )
        .attr("data-trimestre",function(d,i){return d.trimeste } )
        .attr("data-valor",function(d,i){return d.valor } )
        .on('mouseover', tooltip.show)
	    .on('mouseout', tooltip.hide);



        svg.append("text")
            .attr("class","titulo-eje")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ ((configTrimestral.padding/2)-5 ) +","+(configTrimestral.height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
            .text(configTrimestral.tituloY);

        svg.append("text")
            .attr("class","titulo-eje")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ (configTrimestral.width/2) +","+( configTrimestral.height-(configTrimestral.padding/2))+")")  // centre below axis
            .text(configTrimestral.tituloX);

        svg.append("text")
            .attr("class","titulo-chart")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("x",(configTrimestral.width/2))
            .attr("y",( configTrimestral.padding/3))
            .text(configTrimestral.tituloChart)
            .attr("alignment-baseline","central");
            //.attr("transform", "translate("+ (config.width/2) +","+( config.padding/3)+")")  // centre below axis
}

function VentasMensuales(){
   //parametros
   //color: 1 schema de 10 colores 2 interpolacion de colores
   //para que funcione no debe estar definido ref en el css

    var config = {
        width:0,
        height:0,
        marginleft:100,
		marginright:100,
		bottom:50,
		top:50,
		color:1,
        months: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        tituloX:"Meses",
        tituloY:"Ventas",
        tituloChart:"VENTAS X MES"

    };

	config.width=800 - config.marginleft - config.marginright
	config.height=450 - config.top  - config.bottom

    var _format = d3.format("$,.2f");
        //.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    var VENTA_MAX = d3.max(datomes, function(d) { return +d.venta; });


	//console.log(dataGroup);

   var tooltip = d3.tip()
		.attr('class', 'tooltip')
		.offset([-10, 0])
		.html(function(d) {
			return "<strong>" + d.Anio + "-" + d.Mes + "</strong><br> ventas: " + _format(+d.venta);
		});

	var svg = d3.select('#vxanio')
        .append('svg')
        .attr("width", config.width + config.marginleft + config.marginright)
        .attr("height", config.height  + config.top  + config.bottom	)
		.append("g")
		.attr("transform", "translate(" +config.marginleft + "," +config.top  + ")")
        .attr("id","svg_mes");

    svg.call(tooltip);

	var x=d3.scaleBand()
            .domain(config.months)
            .rangeRound([0, config.width ]);

    // console.log(x.rangeBand());
    //datos.map(function(d) { console.log(d.Mes)})

    var y = d3.scaleLinear()
           .range([config.height,0])
           .domain([0, VENTA_MAX]);


      var ejeX = d3.axisBottom()
            .scale(x)
			.tickSizeInner(5)
			.tickSizeOuter(0)
			.tickPadding(10);
			//xAxis.tickFormat(d3.timeFormat('%Y'));   -config.height
			//yAxis.tickValues([0, 75, 150, 1000, 2500, 5000, 10000]);

        var ejeY = d3.axisLeft()
            .scale(y)
            .tickFormat(_format)
			.tickSizeInner(-config.width +25)
			.tickSizeOuter(0)
			.tickPadding(10);


	switch(config.color) {
		case 1:
			var color = d3.scaleOrdinal(d3.schemeCategory10);
			break;
		case 2:

			var color = d3.scaleLinear()
				.domain([0, 15])
				.range(["yellow", "steelblue"]);

			break;
	}


	var lineGen = d3.line()
		.x(function(d) { return x(d.Mes); })
		.y(function(d) { return y(d.venta); });

		//SUAVIZA LA CURVA PERO NO ES APLICABLE EN ESTE CASO .curve(d3.curveBasis)

	//---------------------------------------- trabajamos con los datos-------------
	var dataGroup=d3.nest()
		.key(function(d){
			return d.Anio;
		})
		.entries(datomes);
	//esta instruccion muestra los dadtos de una
	//console.log(JSON.stringify(dataGroup));

	dataGroup.forEach(function(d, i) {
		svg.append('svg:path')
			.attr('d', lineGen(d.values))
			.attr('stroke', color(i))
			.attr('stroke-width', 2)
			.attr('fill', 'none')
			.attr("data-legend", d.key);
	} 	);



   //no entiendo porque fue necesario regresar 25px
   svg.append("g")
        .attr("class", "eje")
        .attr("transform", "translate(-25," + (config.height) +  " )")
        .call(ejeX);

    svg.append("g")
        .attr("class", "eje")
        .attr("transform", "translate(0,0)")
        .call(ejeY);

	//cargamos los datos

   dataGroup.forEach(function(d,j){
		d.values.forEach(function(hijo,i){

		//console.log(hijo.Mes)
		 svg.append("svg:circle")
		 .attr("class", "mycircle")
		 .attr("cx", function (d) {
			return x(hijo.Mes);
		 })
		 .attr("cy", function (d) {
		   return y(hijo.venta);
		 })
		 .attr("r", 5)
		 .on('mouseover', tooltip.show)
		 .on('mouseout', tooltip.hide)
		 .attr("fill", color(j))

		})
   });

	svg.selectAll(".mycircle")
     .data(datomes);
    console.log(JSON.stringify(datomes));

    // now add titles to the axes
    svg.append("text")
        .attr("class","titulo-eje")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ "-80" +","+(config.height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
        .text(config.tituloY);

    svg.append("text")
        .attr("class","titulo-eje")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ (config.width/2) +","+ (config.height + config.bottom -20)  +")")  // centre below axis
        .text(config.tituloX);

    svg.append("text")
        .attr("class","titulo-chart")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ (config.width/2) +"," + "-20" +")")  // centre below axis
        .text(config.tituloChart);



	 svg.selectAll(".legend")
         .data(dataGroup);

     dataGroup.forEach(function(d,i){

        svg.append("rect")
          .attr('width', 20)
          .attr('height', 20)
          .attr('x',config.width)
          .attr('y',(config.top /2) * (i+1)  )
          .style('fill', color(i))
          .style('stroke', color(i))
          .attr('class','legend');

        svg.append('text')
          .attr('x', config.width +40)
          .attr('y', (config.top/2) *(i+1) + 10 )
          .text(d.key);
     })


}

function VentasxAnio(){
   //parametros
   //color: 1 schema de 10 colores 2 interpolacion de colores
   //para que funcione no debe estar definido ref en el css

    var config = {
        columnWidth: 30,
        columnHeight: 100,
        columnGap: 5,
        padding: 80,
        width:0,
        height:0,
        marginleft:5,
		color:1,
        tituloX:"Años",
        tituloY:"Ventas",
        tituloChart:"VENTAS X AÑO"
    };

	//logica para las ecalas
	//si tenemosque graficar ventas anuales los valores son 120.000 usd
	// en este caso deberiamos graficar en miles de usd


    var _format = d3.format("$,.2f");
        //.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    var VENTA_MAX = d3.max(datos, function(d) { return +d.valor; });
    var NUM_COLUMNAS = datos.length;

    config.width = NUM_COLUMNAS * (config.columnWidth + config.columnGap)
                   + (2 * config.padding);
    config.height = config.columnHeight + 2 * config.padding;


   var tooltip = d3.tip()
		.attr('class', 'tooltip')
		.offset([-10, 0])
		.html(function(d) {
			return "<strong>" + d.nombre + "</strong><br> ventas: " + _format(+d.valor);
		});

	var svg = d3.select('#vxanio')
        .append('svg')
        .attr("width", config.width)
        .attr("height", config.height);

    svg.call(tooltip);

	var x=d3.scaleBand()
            .domain(datos.map(function(d) { return d.nombre; }))
            .rangeRound([0, config.width - (2 * config.padding)  ])
            .paddingInner(0);

    var y = d3.scaleLinear()
           .range([config.columnHeight, 0])
           .domain([0, VENTA_MAX]);


      var ejeX = d3.axisBottom()
            .scale(x);


        var ejeY = d3.axisLeft()
            .scale(y)
            .tickFormat(_format);

	switch(config.color) {
		case 1:
			var color = d3.scaleOrdinal(d3.schemeCategory10);
			break;
		case 2:

			var color = d3.scaleLinear()
				.domain([0, 15])
				.range(["yellow", "steelblue"]);

			break;
	}

  d3.select("svg")
      .selectAll("rect")
      .data(datos)
    .enter().append("rect")
      .attr("width", config.columnWidth)
      .attr("x", function(d,i) {
         return config.padding + config.marginleft + i * (config.columnWidth + config.columnGap)
       })
      .attr("y", function(d,i) {
          //console.debug("con escala:" + y(d.valor) + "sin escala:" + d.valor );
          return (config.padding  + y( d.valor));

      })
      .attr("height", function(d,i) { return config.columnHeight - y(d.valor) })
      .attr("data-nombre",function(d,i){return d.nombre } )
      .attr("data-venta",function(d,i){return d.valor})
	  .attr("fill",    function(d,i) { return color(i);})
      .attr('id', function(d){ return 'bar_'+d.nombre;})
	  .on('mouseover', tooltip.show)
	  .on('mouseout', tooltip.hide)
      .on('click', function(d,i) {
          ActualizaVentasTrimestrales(d.nombre,color(i));
          SeleccionaTrace(d.nombre);  });

   svg.append("g")
        .attr("class", "eje")
        .attr("transform", "translate(" + (config.padding +config.marginleft  ) + "," + (config.height - config.padding +5) +" )")
        .call(ejeX);

    svg.append("g")
        .attr("class", "eje")
        .attr("transform", "translate(" + config.padding + "," + config.padding  +")")
        .call(ejeY.ticks(5));


        // now add titles to the axes
        svg.append("text")
            .attr("class","titulo-eje")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ ((config.padding/2)-15 ) +","+(config.height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
            .text(config.tituloY);

        svg.append("text")
            .attr("class","titulo-eje")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ (config.width/2) +","+( config.height-(config.padding/3))+")")  // centre below axis
            .text(config.tituloX);

        svg.append("text")
            .attr("class","titulo-chart")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ (config.width/2) +","+( config.padding/3)+")")  // centre below axis
            .text(config.tituloChart);



}
