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
	.on("mouseleave", function(){
		if(colorbar){
			colorbar.defaultSelectedYear();
		}		
	});


var container = svg.append("g")
				.attr("transform", "translate(0, -" + (0.1 * height) + ")");

var force; 
var nodes;
var edges;

var color = d3.scale.linear()
			.domain([0, 0.5, 1])
			.range([d3.rgb(230, 230, 120), d3.rgb(120,205,180), d3.rgb(44,127,184)]);
var colorbar;

function getDataset() {
	d3.json("/dataset/" + name, function(err, json){
		if (err){
			setTimeout(getDataset, 1000);	
		}else{
		dataset = json;
		dataset.edges = [];
		getLinksFromDistanceMatrix(dataset, dataset.nodes.length < 120 ? 0.8 : 0.70);
		buildForceLayout();
		showYearColorBar();	
		}
	});	
}

getDataset();

function showYearColorBar(){
	colorbar = new Colorbar();
	colorbar.colorbarGroup = svg.append("g")
					.selectAll("rect")
					.data(colorbar.years)
					.enter()
					.append("rect")
					.attr("width", colorbar.colorWidth)
					.attr("height", colorbar.colorbarHeight)
					.attr("y", 0.8 * height)
					.attr("x", function(d, i){
						return colorbar.startX + i * colorbar.colorWidth;
					})
					.attr("fill", function(d){
						return color(colorbar.yearScale(d));
					});
	
					
	colorbar.colorbarLabels = svg.append("g").selectAll("text")
				.data(colorbar.selectedYear)
				.enter()
				.append("text")
				.attr("font-family", "sans-serif")
				.attr("x", function(d, i){
					return colorbar.startX + (i * colorbar.colorWidth * colorbar.numRects);
				})
				.attr("y", 0.80 * height + colorbar.colorbarHeight + 10)
				.attr("text-anchor", function(d){
					if (d.anchor){
						return d.anchor;
					}else{
						return 'center';
					}
				})
				.attr("alignment-baseline", "hanging")
				.attr("fill", "#888")
				.text(function(d){
					return d.year;
				});
}

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
					.charge(function(){
						var charge;
						if(dataset.nodes.length < 100){
							charge = -60
						}else if(dataset.nodes.length < 150){
							charge = -40
						}else {
							charge = -30
						}
						if(dataset.edges.length < dataset.nodes.length){
							charge += 5
						}
						return charge
					}())
					.nodes(dataset.nodes)
					.links(dataset.edges)
					.linkDistance(function(d){
						var multiplier = 60;
						if(dataset.edges.length < dataset.nodes.length){
							multiplier -= 10;
						}
						return d.distance * multiplier;	
					})
					.size([1, 0.7])
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
							.html('<a href="http://www.ncbi.nlm.nih.gov/pubmed/' + d.pmid + '" target="_blank">'+ d.name + '  ' + d.year + '</a>');
						d3.select("#tooltip")
							.classed("hidden", false);
						if(colorbar){
							colorbar.updateSelectedYear(d.year, d.normYear);
						}
					})
					.on("mousedown", function(){d3.event.stopPropagation(); });
				
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

var Colorbar = function(){
	this.yearScale = d3.scale.linear()
				.domain([dataset.minYear.year, dataset.maxYear.year])
				.range([dataset.minYear.normYear, dataset.maxYear.normYear]);
	
	this.minYear = dataset.minYear.year;
	this.maxYear = dataset.maxYear.year - 1;
	this.numRects = 20;

	this.years = [];
	for (var i = this.minYear; i < this.maxYear; i = i+((this.maxYear-this.minYear)/this.numRects)){
		this.years.push(i);
	}
	
	this.startX = 0.15 * width;
	this.colorbarWidth = 0.7 * width;
	this.colorbarHeight = 25;
	this.colorWidth = this.colorbarWidth/this.years.length;
	
	this.xScale = d3.scale.linear()
				.domain([dataset.minYear.normYear, dataset.maxYear.normYear])
				.range([this.startX, this.startX + this.colorbarWidth]);
	
	this.selectedYear = [{'year': this.minYear, 'anchor': 'start'},
					{'year': this.maxYear, 'anchor': 'end'}];
}

Colorbar.prototype.updateSelectedYear = function(year, normYear){
	this.selectedYear = [{'year': year, 'normYear': normYear}]
	this.colorbarLabels = this.colorbarLabels.data(this.selectedYear);
	var xScale = this.xScale;
	
	this.colorbarLabels.transition()
				.text(function(d){
					return d.year;
				})
				.attr("x", function(d){
					return xScale(d.normYear);
				})
				.attr("text-anchor", function(d){
					if (d.anchor){
						return d.anchor;
					}else{
						return 'center';
					}
				});
	
	this.colorbarLabels.exit().remove();			
}

Colorbar.prototype.defaultSelectedYear = function(){
	this.selectedYear = [{'year': this.minYear, 'anchor': 'start'},
					{'year': this.maxYear, 'anchor': 'end'}];
			
	this.colorbarLabels = this.colorbarLabels
				.data(this.selectedYear);
				
	this.colorbarLabels.enter()
				.append("text")
				.attr("y", 0.80 * height + this.colorbarHeight + 10)
				.attr("text-anchor", function(d){
					if (d.anchor){
						return d.anchor;
					}else{
						return 'center';
					}
				})
				.attr("alignment-baseline", "hanging")
				.attr("fill", "#888")
				
	var startX = this.startX;
	var colorWidth = this.colorWidth;
	var numRects = this.numRects;
	this.colorbarLabels.transition()
				.attr("font-family", "sans-serif")
				.attr("x", function(d, i){
					return startX + (i * colorWidth * numRects);
				})
				.text(function(d){
					return d.year;
				});	
}