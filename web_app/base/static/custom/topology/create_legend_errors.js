function create_legend() {
  legendValues = [ 
  {'value':'No Data','color':'#999','y':'30','x':'10'},
  {'value':'0 Er/s','color':'green','y':'30','x':'90'},
  {'value':'1-30 Er/s','color':'blue','y':'30','x':'170'},
  {'value':'30-2K Er/s','color':'orange','y':'30','x':'270'},
  {'value':'>2K Er/s','color':'red','y':'30','x':'380'}
  ]

  var legendRectSize = 20;
  var legendSpacing = 5;
  var legend = d3.select("body").select("#main_svg").selectAll('.legend')
  var svg = d3.select("#sfp_div1")
  .append("svg")
  .attr("id","legend_svg")
  .attr("width", 1000)
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
