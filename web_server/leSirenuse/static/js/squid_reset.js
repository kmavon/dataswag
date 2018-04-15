var h =  window.getComputedStyle(document.getElementById("squid")).getPropertyValue("height").slice(0,-2);
var w =  window.getComputedStyle(document.getElementById("squid")).getPropertyValue("width").slice(0,-2);

$("#squid").attr("viewBox", -w/2 + " " + -h/2 + " " + w + " " + h);

function plot_squid(target){
  url = "http://localhost:8000/es_tool/json/squid" + target + ".json"
  d3.json(url).then(function(result){

    //some variables needed for the viz
    var nodes = result.squid.satellites;
    var center = result.squid.center;
    var splits = (2*Math.PI)/nodes.length;
    var squid = d3.select("#squid");
    //empty the svg
    squid.selectAll("*").remove();

    //add links to svg
    var links = squid.selectAll("line")
    .data(nodes)
    .enter()
      .append("line")
      .attr("class", "links")
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", 0)
      .style("stroke", "yellow");

    //add satellites circles to svg
    var circles = squid.selectAll("circle")
      .data(nodes)
      .enter()
        .append("circle")
        .attr("id", function(d){ return d.name})
        .attr("onclick", function(d) {return "rank_images(" + d.name.slice(-1) + ")"})
        .attr("class", "satellite")
        .attr("r", function(d) { return d.size/20; })
        .attr("fill", "blue");

    //add center circle to svg
    d3.select("#squid")
      .append("circle")
      .attr("id", result.squid.center.name)
      .attr("cy", 0)
      .attr("cx", 0)
      .attr("r", result.squid.center.size/20)
      .attr("fill", "red");

    //statellites transitions
    circles.data(nodes)
    .transition()
    .duration(2000)
    .attr("cy", function(d, i) {
      var theta = i*splits - (Math.PI/2);
      return d.distance * (w/2) * Math.sin(theta);
    })
    .attr("cx", function(d, i) {
      var theta = i*splits - (Math.PI/2);
      return d.distance * (w/2) * Math.cos(theta);
    });

    //links transitions
    links.data(nodes)
    .transition()
    .duration(2000)
    .attr("y2", function(d, i) {
      var theta = i*splits - (Math.PI/2);
      return d.distance * (w/2) * Math.sin(theta);
    })
    .attr("x2", function(d, i) {
      var theta = i*splits - (Math.PI/2);
      return d.distance * (w/2) * Math.cos(theta);
    });

    //future
    become_target = function(cluster) {
      cluster.transition()
             .duration(2000)
             .attr("y2", 0)
             .attr("x2", 0)
             .attr("fill", "red")
    };
  });
}
