rank_images = function (target) {
	$.ajax({
		url: "http://localhost:8000/get_ranked_pics/",
		type: "POST",
		data: {
			'target': target
		},
		dataType: "json",
		success: function (result) {
			var data = result["rank"];
			var container = d3.select("#align-items-flex-start");
			container.text("");
			var pics_cont = container.selectAll("div")
				.data(data).enter()
				.append("div")
				.attr("class", "cont-post");

			pics_cont.data(data)
				.append("div")
				.attr("class", "post-number")
				.text(function (d, i) {
					return i + 1;
				});

			pics_cont.data(data)
				.append("a")
				.attr("href", function (d) {
					return "http://localhost:8000/es_tool/single.html?pic=" + d.pic_url;
				})
				.append("div")
				.attr("class", "post ranked")
				.attr("id", function (d) {
					return "post_" + d.pic_url.replace(".", "_");
				})
				.attr("style", function (d) {
					return "background: url(http://media.localhost:8000/media/" + d.pic_url + ") 50% 50% no-repeat; background-size:cover;"
				});
		}
	});
};

fill_dropdown = function (target) {
	url = "http://localhost:8000/es_tool/json/clusters.json"
	d3.json(url).then(function (clusters_file) {
		var result = clusters_file.clusters.filter(function (squid) {
			return squid.center.name === target.replace("_", " ")
		})[0]
		var satellites = result.satellites;
		var center = result.center;

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
			.attr("onclick", function (d) {
				return "target_change('" + d.name + "')";
			})
			.html(function (d) {
				return d.name;
			});
	});
};

$(document).ready(function () {
	scompari();
	var GET = {};
	var query = window.location.search.substring(1).split("&");
	for (var i = 0, max = query.length; i < max; i++) {
		if (query[i] === "") // check for trailing & with no param
			continue;

		var param = query[i].split("=");
		GET[decodeURIComponent(param[0])] = decodeURIComponent(param[1] || "");
	}
	target = GET['target'];
	$(document).ajaxStop(function () {
		$("#loading").attr("style", "display: none;")
		//$("#loading").hide
	});
	prepare_squid(target);
	plot_pictures();
	fill_dropdown(target);
	rank_images(target);
});

target_change = function (target) {
	rank_images(target);
	fill_dropdown(target);
	plot_squid(target);
	plot_pictures();
}


var sotto = document.getElementById("sotto");
var style = window.getComputedStyle(sotto);

var scompari = function () {
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
	setTimeout(function () {
		appari()
	}, 1000)
}


var appari = function () {
	d3.select("#sopra")
		.transition()
		.duration(1000)
		.style("color", "white")

	d3.select("#sotto")
		.transition()
		.duration(1000)
		.style("width", "110px")
	setTimeout(function () {
		scomparidestra()
	}, 1000)
}
/*secondo ciclo*/
var scomparidestra = function () {
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
	setTimeout(function () {
		apparidestra()
	}, 1000)
}


var apparidestra = function () {
	d3.select("#sopra")
		.transition()
		.duration(1000)
		.style("color", "white")

	d3.select("#sotto")
		.transition()
		.duration(1000)
		.style("width", "110px")
	setTimeout(function () {
		scompari()
	}, 1000)
}

$("svg").find("#Path-3").click(function () {
	window.location = 'http://localhost:8000/es_tool/index.html';
});
