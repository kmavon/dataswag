rank_images = function(target) {
	d3.json("http://localhost:8000/get_ranked_pics/", { method: 'POST', data: { 'target': target } }).then(function(result){
		var data = result["rank"];
		var container = d3.select("#align-items-flex-start");
		container.text("");
		var pics_cont = container.selectAll("div")
			.data(data).enter()
			.append("div")
			.attr("class","cont-post");
		
		pics_cont.data(data)
			.append("div")
			.attr("class", "post-number")
			.text(function(d,i){ return i+1; });
		
		pics_cont.data(data)
			.append("a")
			.attr("href", function(d){
				return "http://localhost:8000/es_tool/single.html?pic=" + d.pic_url;
			})
			.append("div")
			.attr("class", "post ranked")
			.attr("style", function(d){
				return "background: url(http://media.localhost:8000/media/" + d.pic_url + ") 50% 50% no-repeat; background-size:cover;"
			});
	})	
};

fill_dropdown = function(target) {
  url = "http://localhost:8000/es_tool/json/" + target + ".json"
  d3.json(url).then(function(result){
    var satellites = result.squid.satellites;
    var center = result.squid.center;

    d3.select("#dropdownMenuButton")
      .html(center.name);

    var menu = d3.select(".dropdown-menu");
    menu.selectAll("*").remove();
    menu.selectAll("a")
        .data(satellites)
        .enter()
        .append("a")
        .attr("class", "dropdown-item")
        .attr("href", "#")
        .attr("onclick", function(d) {return "target_change('" + d.name + "')"; })
        .html(function(d){ return d.name; });
    });
  };

$(document).ready(function() {
	var GET = {};
    var query = window.location.search.substring(1).split("&");
    for (var i = 0, max = query.length; i < max; i++)
    {
        if (query[i] === "") // check for trailing & with no param
            continue;

        var param = query[i].split("=");
        GET[decodeURIComponent(param[0])] = decodeURIComponent(param[1] || "");
    }
	target = GET['target'];
  prepare_squid(target);
  fill_dropdown(target);
	rank_images(target);
});

target_change = function(target) {
  rank_images(target);
  fill_dropdown(target);
  plot_squid(target);
}

$("svg").find("#Path-3").click(function(){
	window.location = 'http://localhost:8000/es_tool/index.html';
});
