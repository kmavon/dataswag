d3.json("http://localhost:8000/es_tool/json/brands_sim.json").then(function(result){
	console.log(result);
	data = result['brands_sim'];
	//var svg = d3.select("#scatter").append("svg");
	//width = parseInt(window.getComputedStyle(document.getElementById("scatter")).getPropertyValue("width").slice(0,-2));
	//height =  parseInt(window.getComputedStyle(document.getElementById("scatter")).getPropertyValue("height").slice(0,-2));
	//svg.attr("width", width);
	//svg.attr("height", height);

//	svg.attr("padding-right", "19px")
var margin = {
	 top: 0,
	 right: -15,
	 bottom: 0,
	 left: -15
 },
  width = document.querySelector('#scatter').offsetWidth - margin.left - margin.right,
  height = document.querySelector('#scatter').offsetHeight - margin.top - margin.bottom;


// add the graph canvas to the body of the webpage
var svg = d3.select("#scatter").append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
	.attr("viewBox", "0 -67 " +(parseInt(height)+40)+" "+(parseInt(width)+100))
  //.attr("id", "scatter")

  //.attr("class", "graphSvgComponent")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	var x = d3.scaleBand().rangeRound([0, width]).padding(0.1),
		y = d3.scaleLinear().rangeRound([height, 0]);

	var g = svg.append("g");

	x.domain(data.map(function(d) { return d.name; }));
	y.domain([0, d3.max(data, function(d) { return d.sim; })]);

	//g.append("g")
	//  .attr("class", "axis axis--x")
	 // .attr("transform", "translate(0," + height + ")")
	 // .call(d3.axisBottom(x));

	//g.append("g")
	  //.attr("class", "axis axis--y")
	  //.call(d3.axisLeft(y).ticks(5, "%"))
	//.append("text")
	  //.attr("transform", "rotate(-90)")
	  //.attr("y", 6)
	  //.attr("dy", "0.71em")
	  //.attr("text-anchor", "end")
	  //.text("Brand");


	g.selectAll(".bar")
	.data(data)
	.enter().append("circle")
	  .attr("class", "bar")
	  .attr("cx", function(d) { return x(d.name); })
	  .attr("cy", function(d) { return y(d.sim); })
	  .attr("width", x.bandwidth())
	  //.attr("height", function(d) { return height - y(d.frequency); });
	  .attr("r", "0.8em")
		.attr("fill", "red")
		.attr("stroke", "#578290")
		.style("opacity", function(d) {return d.sim/100;});


		g.selectAll("text")
		  .data(data)
			.enter().append("text")
			.attr("class", "labels")
			.attr("x", function(d) { return x(d.name)-10; })
			.attr("y", function(d) { return y(d.sim)-25; })
			.text(function(d) {
				return d.name;
			})
			.attr("font-family", "Karla")
			.attr("font-size","0.8em")
			.attr("fill", "#578290");


});


//Here jQuery animation for scatterplot

$(function() {
  $('.labels').hover(function() {
    $(this).removeClass('invisible');
  }, function() {
    $(this).addClass('invisible');
  });
});


d3.json("http://localhost:8000/es_tool/json/caption.json").then(function(dataset){
	width = parseInt(window.getComputedStyle(document.getElementById("caption")).getPropertyValue("width").slice(0,-2));
	height =  parseInt(window.getComputedStyle(document.getElementById("caption")).getPropertyValue("height").slice(0,-2));

	var colors = []
    for(i=0; i<dataset.children.length; i++){
      colors.push("#"+((1<<24)*Math.random()|0).toString(16));
    };
	var bubble = d3.pack(dataset)
		.size([height, width])
		.padding(1.05);

	var svg = d3.select("#caption")
		.append("svg");
	svg.attr("viewBox", "65 0 "+width+" "+height);

	var nodes = d3.hierarchy(dataset)
		.sum(function(d) { return d.score; });

	var node = svg.selectAll(".node")
		.data(bubble(nodes).descendants())
		.enter()
		.filter(function(d){
			return  !d.children
		})
		.append("g")
		.attr("class", "node")
		.attr("transform", function(d) {
			return "translate(" + d.x + "," + d.y + ")";
		});

	node.append("title")
		.text(function(d) {
			return d.name + ": " + d.score;
		});

	node.append("circle")
		.attr("r", function(d) {
			return d.r;
		})
		.attr("fill", function(d,i){ return colors[i];});

	node.append("text")
		.attr("dy", ".2em")
		.style("text-anchor", "middle")
		.text(function(d) {
			console.log(d);
			return d.data.topic;
		})
		.attr("font-family", "sans-serif")
		.attr("font-size", function(d){
			return d.r/4;
		})
		.attr("fill", "white");

	node.append("text")
		.attr("dy", "1.3em")
		.style("text-anchor", "middle")
		.text(function(d) {
			return d.data.score;
		})
		.attr("font-family",  "Gill Sans", "Gill Sans MT")
		.attr("font-size", function(d){
			return d.r/3;
		})
		.attr("fill", "white");

});


d3.json("http://localhost:8000/es_tool/json/tags.json").then(function(dataset){
	width = parseInt(window.getComputedStyle(document.getElementById("caption")).getPropertyValue("width").slice(0,-2));
	height =  parseInt(window.getComputedStyle(document.getElementById("caption")).getPropertyValue("height").slice(0,-2));

	var colors = []
    for(i=0; i<dataset.children.length; i++){
      colors.push("#"+((1<<24)*Math.random()|0).toString(16));
    };
	var bubble = d3.pack(dataset)
		.size([height, width])
		.padding(1.05);

	var svg = d3.select("#caption")
		.append("svg");
	svg.attr("viewBox", "65 0 "+width+" "+height);

	var nodes = d3.hierarchy(dataset)
		.sum(function(d) { return d.score; });

	var node = svg.selectAll(".node")
		.data(bubble(nodes).descendants())
		.enter()
		.filter(function(d){
			return  !d.children
		})
		.append("g")
		.attr("class", "node")
		.attr("transform", function(d) {
			return "translate(" + d.x + "," + d.y + ")";
		});

	node.append("title")
		.text(function(d) {
			return d.name + ": " + d.score;
		});

	node.append("circle")
		.attr("r", function(d) {
			return d.r;
		})
		.attr("fill", function(d,i){ return colors[i];});

	node.append("text")
		.attr("dy", ".2em")
		.style("text-anchor", "middle")
		.text(function(d) {
			console.log(d);
			return d.data.topic;
		})
		.attr("font-family", "sans-serif")
		.attr("font-size", function(d){
			return d.r/4;
		})
		.attr("fill", "white");

	node.append("text")
		.attr("dy", "1.3em")
		.style("text-anchor", "middle")
		.text(function(d) {
			console.log(d);
			return d.data.score;
		})
		.attr("font-family",  "Gill Sans", "Gill Sans MT")
		.attr("font-size", function(d){
			return d.r/3;
		})
		.attr("fill", "white");

});
