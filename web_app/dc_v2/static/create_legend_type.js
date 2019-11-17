function create_legend(type,div_width) {
        $("#legend_svg").first().remove();
        var y_start = 30
        var space = div_width/8
        if (type == 'traffic') {
		legendValues = [
                {'value':'No Data','color':'#999','y': y_start  ,'x': space * 0 },
                {'value':'SPF-Path','color':'black','y': y_start ,'x': space * 1 },
                {'value':'0%-1%','color':'blue','y': y_start ,'x': space * 2 },
                {'value':'1%-30%','color':'green','y': y_start ,'x': space * 3 },
                {'value':'30%-50%','color':'yellow','y': y_start ,'x': space * 4 },
                {'value':'50%-70%','color':'orange','y': y_start ,'x': space * 5 },
                {'value':'70%-100%','color':'red','y': y_start ,'x': space * 6 },
                {'value':'>100%','color':'fuchsia','y': y_start ,'x': space * 7 },
				]
        		}
        else if (type == 'latency') {
        	legendValues = [
  			{'value':'No Data','color':'#999','y':'30','x':'10'},
  			{'value':'SPF-PATH','color':'black','y':'30','x':'90'},
  			{'value':'0-10ms','color':'blue','y':'30','x':'180'},
  			{'value':'10-30ms','color':'green','y':'30','x':'270'},
  			{'value':'30-80ms','color':'yellow','y':'30','x':'350'},
  			{'value':'80-100ms','color':'orange','y':'30','x':'440'},
  			{'value':'100-180ms','color':'red','y':'30','x':'530'}
  				]
        		}
        else if (type == 'errors') {
  		legendValues = [
  			{'value':'No Data','color':'#999','y':'30','x':'10'},
  			{'value':'0 Er/s','color':'green','y':'30','x':'90'},
  			{'value':'1-30 Er/s','color':'blue','y':'30','x':'170'},
  			{'value':'30-2K Er/s','color':'orange','y':'30','x':'270'},
  			{'value':'>2K Er/s','color':'red','y':'30','x':'380'}
  				]
			}
	var legendRectSize = 20;
	var legendSpacing = 5;
	var legend = d3.select("body").select("#main_svg").selectAll('.legend')
        var svg = d3.select("#legend_div")
	//var svg = d3.select("#sfp_div1")
				.append("svg")
				.attr("id","legend_svg")
				.attr("width", div_width)
				.attr("height", 80)

	var legend = svg.selectAll('.legend')
				.data(legendValues)
				.enter()
				.append('g')
				.attr('class', 'legend')
				.attr('transform', function(d, i) {
					return 'translate(' + d.x + ',' + d.y + ')'; });

	legend.append('rect')
		.attr('width', legendRectSize)
		.attr('height', legendRectSize)
		.style('fill', function(d) { return d.color})
		.style('stroke', function(d) { return d.color}) ;

	legend.append('text')
			.attr('x', legendRectSize + legendSpacing)
			.attr('y', legendRectSize - legendSpacing)
			.text(function(d) { return d.value; });

}

