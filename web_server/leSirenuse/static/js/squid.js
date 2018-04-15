var h =  window.getComputedStyle(document.getElementById("squid")).getPropertyValue("height").slice(0,-2);
var w =  window.getComputedStyle(document.getElementById("squid")).getPropertyValue("width").slice(0,-2);

$("#squid").attr("viewBox", -w/2 + " " + -h/2 + " " + w + " " + h);

prepare_squid = function(target){
  url = "http://localhost:8000/es_tool/json/" + target + ".json";
  d3.json(url).then(function(result){

    //some variables needed for the viz
    var nodes = result.squid.satellites;
    var colors = []
    for(i=0; i<nodes.length; i++){
      colors.push("#"+((1<<24)*Math.random()|0).toString(16));
    };
    var center_color = "#"+((1<<24)*Math.random()|0).toString(16);
    var splits = (2*Math.PI)/nodes.length;
    var squid = d3.select("#squid");
    //empty the svg
    //squid.selectAll("*").remove();

    //add links to svg (only if empty)
    var links = squid.selectAll("line")
    .data(nodes)
    .enter()
      .append("line")
      .attr("i", function(d, i) { return i; })
      .attr("class", "links")
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", 0)
      .style("stroke", "yellow");

    //add satellites circles to svg (only if empty)
    var circles = squid.selectAll("circle")
      .data(nodes)
      .enter()
        .append("circle")
        .attr("i", function(d, i) { return i; })
        .attr("id", function(d){ return d.name; })
        .attr("onclick", function(d) { return "target_change('" + d.name + "')"; })
        .attr("class", "satellite")
        .attr("r", function(d) { return d.size/20; })
        .attr("fill", function(d, i) { return colors[i]; });

    //add center circle to svg
    d3.select("#squid")
      .append("circle")
      .attr("class", "center")
      .attr("id", result.squid.center.name)
      .attr("cy", 0)
      .attr("cx", 0)
      .attr("r", result.squid.center.size/20)
      .attr("fill", center_color);

    //statellites transitions
    circles.data(nodes)
    .transition()
    .duration(2000)
    .attr("cy", function(d, i) {
      var theta = i*splits;
      return d.distance * (w/2) * Math.sin(theta);
    })
    .attr("cx", function(d, i) {
      var theta = i*splits;
      return d.distance * (w/2) * Math.cos(theta);
    });

    //links transitions
    links.data(nodes)
    .transition()
    .duration(2000)
    .attr("y2", function(d, i) {
      var theta = i*splits;
      return d.distance * (w/2) * Math.sin(theta);
    })
    .attr("x2", function(d, i) {
      var theta = i*splits;
      return d.distance * (w/2) * Math.cos(theta);
    });
  });
};

function plot_squid(target){
  url = "http://localhost:8000/es_tool/json/" + target + ".json"
  d3.json(url).then(function(result){
    var nodes = result.squid.satellites;
    var splits = (2*Math.PI)/nodes.length;
    var squid = d3.select("#squid");

    var old_center_DOM = d3.select(".center");
    var old_center = nodes.filter(function(d){return d.name == old_center_DOM.attr("id");})[0];
    var new_center = result.squid.center;
    var new_center_DOM = d3.select("#" + new_center.name);

    var new_theta = (new_center_DOM.attr("i"))*splits;
    var new_cy = old_center.distance * (w/2) * Math.sin(new_theta);
    var new_cx = old_center.distance * (w/2) * Math.cos(new_theta);

    //switch_target
    old_center_DOM.classed("center", false);
    old_center_DOM.classed("satellite", true);
    old_center_DOM.attr("i", new_center_DOM.attr("i"));
    old_center_DOM.attr("onclick", function(d) {return "target_change('" + old_center.name + "')"});
    old_center_DOM.transition()
      .duration(2000)
      .attr("cy", new_cy)
      .attr("cx", new_cx);
      //.attr("fill", "blue");

    new_center_DOM.classed("center", true);
    new_center_DOM.classed("satellite", false);
    new_center_DOM.attr("i", "");
    new_center_DOM.attr("onclick", "");
    new_center_DOM.transition()
      .duration(2000)
      .attr("cy", 0)
      .attr("cx", 0);
      //.attr("fill", "red");

    //some variables needed for the viz
    var circles = d3.selectAll(".satellite");
    var links = d3.selectAll(".links");

    //statellites transitions
    circles.data(nodes, function(d){ return d ? d.name : this.id; })
    .transition()
    .duration(2000)
    .attr("cy", function(d) {
      var theta = d3.select(this).attr("i")*splits;
      return d.distance * (w/2) * Math.sin(theta);
    })
    .attr("cx", function(d) {
      var theta = d3.select(this).attr("i")*splits;
      return d.distance * (w/2) * Math.cos(theta);
    });

    //links transitions
    links.transition()
    .duration(2000)
    .attr("y2", function() {
      var i = d3.select(this).attr("i");
      var theta = i*splits;
      var d = circles.filter("[i='" + i + "']").data()[0].distance;
      return d * (w/2) * Math.sin(theta);
    })
    .attr("x2", function() {
      var i = d3.select(this).attr("i");
      var theta = i*splits;
      var d = circles.filter("[i='" + i + "']").data()[0].distance;
      return d * (w/2) * Math.cos(theta);
    });
  });
}
