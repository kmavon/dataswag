rank_images = function(target) {
    $.ajax({
            url: 			  'http://localhost:8000/get_ranked_pics/',
            method:			'POST',
            dataType:   'json',
            data:       { 'target': target },
            success: function( data )
            {
                //$("#align-items-flex-start").html('<div class="cont-post"><div class="post rank1 selected-post">1</div><div class="score">score ' + data['rank'][0]['score'] + '</div></div>');
                $("#align-items-flex-start").html('<div class="cont-post"><img src="' + data['rank'][0]['pic_url'] + '" class="post ranked selected-post"><div class="score">score ' + data['rank'][0]['score'] + '</div></div>');
                for (var i = 1; i < data['rank'].length; i++){
                    $("#align-items-flex-start").append(
                        '<div onclick="nextpage(1)" class="cont-post"><img src="' + data['rank'][i]['pic_url'] + '" class="post ranked"><div class="score">score ' + data['rank'][i]['score'] + '</div></div>'
                        //'<div class="cont-post"><div class="post rank' + (i + 1) + '">' + (i + 1) +'</div><div class="score">score ' + data['rank'][i]['score'] + '</div></div>'
                    );
                }
            },
            error: function()
            {
                alert( 'Error. Please, contact the webmaster!' );
            }
        });
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
