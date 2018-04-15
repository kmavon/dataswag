rank_images = function(target) {
    $.ajax({
            url: 			'http://localhost:8000/get_ranked_pics/',
            method:			'POST',
            dataType:       'json',
            data:           { 'target': target },
            success: function( data )
            {
                //$("#align-items-flex-start").html('<div class="cont-post"><div class="post rank1 selected-post">1</div><div class="score">score ' + data['rank'][0]['score'] + '</div></div>');
                $("#align-items-flex-start").html('<div class="cont-post"><img src="' + data['rank'][0]['pic_url'] + '" class="post ranked selected-post"><div class="score">score ' + data['rank'][0]['score'] + '</div></div>');
                for (var i = 1; i < data['rank'].length; i++){
                    $("#align-items-flex-start").append(
                        '<div class="cont-post"><img src="' + data['rank'][i]['pic_url'] + '" class="post ranked"><div class="score">score ' + data['rank'][i]['score'] + '</div></div>'
                        //'<div class="cont-post"><div class="post rank' + (i + 1) + '">' + (i + 1) +'</div><div class="score">score ' + data['rank'][i]['score'] + '</div></div>'
                    );
                }
            },
            error: function()
            {
                alert( 'Error. Please, contact the webmaster!' );
            }
        });
    plot_squid(target);
};

$('#target_select').change( function () {
	target = $('#target_select').val();
	rank_images(target);
});

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
	target = GET['target']
	rank_images(target);
});

$("svg").find("#cluster-3").click(function(){
	$('#first-squid').css('display', 'none');
	$('#cluster3-asDefault').css('display', 'inline');
	$('#cluster4-asDefault').css('display', 'none');
	rank_images(3)
});

$("svg").find("#cluster-4").click(function(){
	$('#first-squid').css('display', 'none');
	$('#cluster3-asDefault').css('display', 'none');
	$('#cluster4-asDefault').css('display', 'inline');
	rank_images(4)
});

$("svg").find("#cluster-1-viz2").click(function(){
	$('#first-squid').css('display', 'inline');
	$('#cluster3-asDefault').css('display', 'none');
	$('#cluster4-asDefault').css('display', 'none');
	rank_images(1)
});

$("svg").find("#cluster-4-viz2").click(function(){
	$('#first-squid').css('display', 'none');
	$('#cluster3-asDefault').css('display', 'none');
	$('#cluster4-asDefault').css('display', 'inline');
	rank_images(4)
});

$("svg").find("#lab-cluster1-viz3").click(function(){
	$('#first-squid').css('display', 'inline');
	$('#cluster3-asDefault').css('display', 'none');
	$('#cluster4-asDefault').css('display', 'none');
	rank_images(1)
});

$("svg").find("#lab-cluster3-viz3").click(function(){
	$('#first-squid').css('display', 'none');
	$('#cluster3-asDefault').css('display', 'inline');
	$('#cluster4-asDefault').css('display', 'none');
	rank_images(3)
});

$(".dropdown-menu").find("#c1").click(function(){
	$('#dropdownMenuButton').html('Cluster 1');
	rank_images(1);
});

$(".dropdown-menu").find("#c2").click(function(){
	$('#dropdownMenuButton').html('Cluster 2');
	rank_images(2);
});

$(".dropdown-menu").find("#c3").click(function(){
	$('#dropdownMenuButton').html('Cluster 3');
	rank_images(3);
});

$(".dropdown-menu").find("#c4").click(function(){
	$('#dropdownMenuButton').html('Cluster 4');
	rank_images(4);
});

$(".dropdown-menu").find("#c5").click(function(){
	$('#dropdownMenuButton').html('Cluster 5');
	rank_images(5);
});

$(".dropdown-menu").find("#c6").click(function(){
	$('#dropdownMenuButton').html('Cluster 6');
	rank_images(6);
});

$("svg").find("#Path-3").click(function(){
	window.location = 'http://localhost:8000/es_tool/index.html'
});
