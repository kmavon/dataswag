console.log("miao");
d3.json("http://localhost:8000/es_tool/json/tags.json").then(function(result){
    console.log("miao");
	console.log(result);
	data = result['tags'];
	var tags = d3.select("#tags");
	tags.selectAll(".tag")
	.data(data)
	.enter().append("div")
	  .attr("class", "tag")
	  .text(function(d){return d.tag;})
      .style("background-color", function(d){return "rgba(255, 0, 0, "+d.score/100+")";});
});