/*
	Smooth scroll functionality for anchor links (animates the scroll
	rather than a sudden jump in the page)
*/
$('.js-anchor-link').click(function(e){
  e.preventDefault();
  var target = $($(this).attr('href'));
  if(target.length){
    var scrollTo = target.offset().top;
    $('body, html').animate({scrollTop: scrollTo+'px'}, 300);
  }
});

/*loader logo*/

var sotto = document.getElementById("sotto");
	var style = window.getComputedStyle(sotto);
	//d3.select("#sotto").style("margin-left", style.marginLeft)

  var scompari = function(){
  d3.select("#sotto").style("margin-left", style.marginLeft)
  d3.select("#sotto").style("margin-right", "auto")
	d3.select("#sopra")
	.transition()
	.duration(1000)
	.style("color", "#4d7a89")

	d3.select("#sotto")
	.transition()
	.duration(1000)
	.style("width", "0px")
	setTimeout(function() { appari() }, 1000)
}


var appari = function(){
	d3.select("#sopra")
	.transition()
	.duration(1000)
	.style("color", "white")

	d3.select("#sotto")
	.transition()
	.duration(1000)
	.style("width", "110px")
	setTimeout(function() { scomparidestra() }, 1000)
}
/*secondo ciclo*/
var scomparidestra = function(){
d3.select("#sotto").style("margin-right", style.marginRight)
d3.select("#sotto").style("margin-left", "auto")
d3.select("#sopra")
.transition()
.duration(1000)
.style("color", "#4d7a89")

d3.select("#sotto")
.transition()
.duration(1000)
.style("width", "0px")
setTimeout(function() { apparidestra() }, 1000)
}


var apparidestra = function(){
d3.select("#sopra")
.transition()
.duration(1000)
.style("color", "white")

d3.select("#sotto")
.transition()
.duration(1000)
.style("width", "110px")
setTimeout(function() { scompari() }, 1000)
}
scompari();
