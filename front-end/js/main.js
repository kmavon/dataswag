SVG.wrap = function(node) {
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
     */
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

$(document).ready(function() {
    $.ajax({
            url: 			'http://localhost:8000/get_ranked_pics/',
            method:			'POST',
            dataType:       'json',
            success: function( data )
            {
                $("#align-items-flex-start").html('<div class="cont-post"><div class="post rank1 selected-post">1</div><div class="score">score ' + data['rank'][0]['score'] + '</div></div>');
                for (var i = 1; i < data['rank'].length; i++){
                    $("#align-items-flex-start").append(
                        '<div class="cont-post"><div class="post rank' + (i + 1) + '">' + (i + 1) +'</div><div class="score">score ' + data['rank'][i]['score'] + '</div></div>'
                    );
                }
            },
            error: function()
            {
                alert( 'Error. Please, contact the webmaster!' );
            }
        });
    
}); 