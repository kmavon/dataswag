/*SVG.wrap = function(node) {
    /* Wrap an existing node in an SVG.js element. This is a slight hack
     * because svg.js does not (in general) provide a way to create an
     * Element of a specific type (eg SVG.Ellipse, SVG.G, ...) from an
     * existing node and still call the Element's constructor.
     *
     * So instead, we call the Element's constructor and delete the node
     * it created (actually, just leaving it to garbage collection, since it
     * hasn't been inserted into the doc yet), replacing it with the given node.
     *
     * Returns the newly created SVG.Element instance.
     
    if (node.length) node = node[0];    // Allow using with or without jQuery selections
    var element_class = capitalize(node.nodeName);
    try {
        var element = new SVG[element_class];
    } catch(e) {
        throw("No such SVG type '"+element_class+"'");
    }
    element.node = node;
    return element;
};

function capitalize(string) {
    if (!string) return string;
    return string[0].toUpperCase() + string.slice(1);
}

var rect = SVG.wrap($('#Livello_4'))


rect.draggable({
  minX: -230.5
, minY: -654.9
, maxX: 280.5
, maxY: 654.9
, snapToGrid: 10
})
*/

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

