var h =  window.getComputedStyle(document.getElementById("squid")).getPropertyValue("height").slice(0,-2);
var w =  window.getComputedStyle(document.getElementById("squid")).getPropertyValue("width").slice(0,-2);

$("#squid").attr("viewBox", -w/2 + " " + -h/2 + " " + w + " " + h);

d3.json("http://localhost:8000/es_tool/json/squid1.json").then(function(result){

  d3.select("#squid")
    .append("circle")
    .attr("cy", 0)
    .attr("cx", 0)
    .attr("r", result.squid1.center.size/20)
    .attr("fill", "red");

  var nodes = result.squid1.satellites;
  var splits = (2*Math.PI)/nodes.length
  var node = d3.select("#squid")
    .append("g")
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
      .attr("class", "satellite")
      .attr("r", function(d) { return d.size/20; })
      .attr("fill", "blue");

  // var simulation = d3.forceSimulation(nodes)
  //     .force("charge", d3.forceCollide().radius(function(d) {
  //        return d.size/20;
  //     }))
  //     .force("r", d3.forceRadial(function (d) {
  //       console.log("radial: " + d.distance*300);
  //       return d.distance*300;
  //     }))
  //     .on("tick", ticked);
  //
  // function ticked() {
  //   node
  //       .attr("cx", function(d) { return d.x; })
  //       .attr("cy", function(d) { return d.y; });

  d3.selectAll(".satellite")
  .data(nodes)
  .transition()
  .duration(2000)
  .attr("cy", function(d, i) {
    var theta = i*splits
    return d.distance * 100 * Math.sin(theta)
  })
  .attr("cx", function(d, i) {
    var theta = i*splits
    return d.distance * 750 * Math.cos(theta)
  });
});
