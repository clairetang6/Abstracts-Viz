var width = 900;
var height = 600;

var dataset;
		
var svg = d3.select("#canvas-container")
			.append("svg")
			.attr("width", width)
			.attr("height", height)
			.append("g");
			
var rect = svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .style("fill", "none")
    .style("pointer-events", "all")
	.on("mousedown", function(){
		if(force){
			force.alpha(0.15);
		}
	})


var container = svg.append("g");

var force; 
var nodes;
var edges;

var color = d3.scale.linear()
			.domain([0, 0.5, 1])
			.range([d3.rgb(230, 230, 120), d3.rgb(120,205,180), d3.rgb(44,127,184)]);


d3.json("/dataset", function(err, json){
	if (err) return console.warn(err);
	dataset = json;
	dataset.edges = [];
	getLinksFromDistanceMatrix(dataset, 0.8);
	buildForceLayout();
});


function getLinksFromDistanceMatrix(dataset, threshold){
	dataset.edges = [];
	for(var i = 0; i < dataset.distance_matrix.length - 1; i++){
		for(var j = i+1; j < dataset.distance_matrix[i].length; j++){
			if(dataset.distance_matrix[i][j] < threshold){
				dataset.edges.push({
					source: i,
					target: j,
					distance: dataset.distance_matrix[i][j]
				})
			}
		}
	}
	return dataset.edges.length;
}


function buildForceLayout(){
	force = d3.layout.force()
					.gravity(0)
					.charge(-60)
					.nodes(dataset.nodes)
					.links(dataset.edges)
					.linkDistance(function(d){
						return d.distance * 60;	
					})
					.size([width, height])
					.start()
					
	force.gravityX = 0.075;
	force.gravityY = 0.08;

	edges = container.append("g")
				.selectAll("line")
				.data(dataset.edges)
				.enter()
				.append("line")
				.style("stroke", "#888")
				.style("stroke-width", 1)
				.attr("alpha", 0.6)
				.style("pointer-events", "none")
				.on("mousedown", function(){d3.event.stopPropagation(); });
							
	nodes = container.append("g")
					.selectAll("circle")
					.data(dataset.nodes)
					.enter()
					.append("circle")
					.attr("r", 10)
					.style("stroke", "white")
					.style("stroke-width", 2)
					.style("fill", function(d){
						if(d.normYear == -1){
							return 'black'
						}else{
							return color(d.normYear);
						}
					})
					.call(force.drag)
					.on("mouseover", function(d){
						d3.select("#tooltip")
							.select("#name")
							.text(d.name + '  ' + d.year);
						d3.select("#tooltip")
							.classed("hidden", false);
					})
					.on("mousedadown", function(){d3.event.stopPropagation(); });
	
					
					
	force.on("tick", function(e){
		
		dataset.nodes.forEach( function(d) {
			if(d.normYear != - 1){
				d.x += (d.normYear - 0.5) * 10 * e.alpha;	
			}
			
			d.y += (height/2 - d.y) * e.alpha * force.gravityY;
			d.x += (width/2 - d.x) * e.alpha * force.gravityX;

		});
		
		edges.attr("x1", function(d) { return d.source.x})
			.attr("x2", function(d) { return d.target.x})
			.attr("y1", function(d) { return d.source.y})
			.attr("y2", function(d) { return d.target.y});
		
		nodes.attr("cx", function(d) { return d.x; })
	     	.attr("cy", function(d) { return d.y; });
	
	});
		
}
		
					



