function lnet_d3js(web_ip,result,type){
  nodes = result[1]
  links = result[0]
  linkstext = result[0]
  var linkedByIndex = {}
  links.forEach((d) => {
    linkedByIndex[`${d.source.name},${d.target.name}`] = true;
  });
  var width = 1900 ;
  var height = 1001;
  var svg = d3.select("#topology").append("svg")
                    .call(zoom)
                    .attr("id","main_svg")
                    //.attr("width", width)
                    //.attr("height", height)
		    .attr("preserveAspectRatio", "xMinYMin meet")
		    .attr("viewBox", "0 0 1900 1001")

  var simulation = d3.forceSimulation(nodes)
      .force("charge", d3.forceManyBody().strength(-800))
      .force("link", d3.forceLink(links).distance(10).strength(0))
      .force("x", d3.forceX(300)) //center to x 300 , only used when dynamic
      .force("y", d3.forceY(300)) // center to y 300, only used when dynamic
      .alphaDecay(1)
      .alphaTarget(0)
      .on("tick", ticked);
  var g = svg.append("g").attr("id","main_g")
      link = g.append("g").selectAll(".link"),
      linktext = g.append("g").selectAll(".link_text"),
      node = g.append("g").selectAll(".node");

  this.restart = function(nodes,links,linkstext){
    function isConnected(a, b) {
      return isConnectedAsTarget(a, b) || isConnectedAsSource(a, b) || a.index === b.index;
    }

    function isConnectedAsSource(a, b) {
        //console.log('a si b in as_src',a,b)
      return linkedByIndex[`${a.name},${b.name}`];
    }

    function isConnectedAsTarget(a, b) {
      return linkedByIndex[`${b.name},${a.name}`];
    }

    function isEqual(a, b) {
      return a.index === b.index;
    }
    var dragDrop = d3.drag().on('start', function (node) {
                  node.fx = node.x
                  node.fy = node.y
                }).on('drag', function (node) {
                  simulation.alphaTarget(1).restart()
                  node.fx = d3.event.x
                  node.fy = d3.event.y
                }).on('end', function (node) {
                  if (!d3.event.active) {
                    simulation.alphaTarget(0)
                  }
                  node.fx = node.x
                  node.fy = node.y
                })
//end
//drag
const mouseOverFunction = function (d) {
  // const circle = d3.select(this); //not needed for now
  node
    .transition(500)
      .style('opacity', (o) => {
        //console.log('d si o on mouseOverFunction',d,o)
        let opacity;
        if (isConnectedAsTarget(o, d) && isConnectedAsSource(o, d)) {
          opacity = 1;
        } else if (isConnectedAsSource(o, d)) {
          opacity = 1;
        } else if (isConnectedAsTarget(o, d)) {
          opacity = 1;
        } else if (isEqual(o, d)) {
          opacity = 1;
        } else {
          opacity = 0.3;
        }
        return opacity;
      })

  link
    .transition(500)
      .style('stroke-opacity', o => (o.source.name === d.name || o.target.name === d.name ? 1 : 0.2))
      .transition(500)
  linktext
      .transition(500)
      .style('opacity', o => (o.source.name === d.name || o.target.name === d.name ? 1 : 0))
      .transition(500)

};

const mouseOutFunction = function () {
  //const circle = d3.select(this);

  node
    .transition(500)
     .style("opacity",1);

  link
    .transition(500)
     .style("stroke-opacity",1);
  linktext
    .transition(200)
     .style("opacity",0);

};
  // Apply the general update pattern to the nodes.
  node = node.data(nodes, function(d) { return d.name ;});

  node.exit().transition()
      .attr("r", 0)
      .remove();

  var nodeEnter = node.enter() // enter, append the g
    .append("g")
    .call(dragDrop)
    .attr("class", "node");

  nodeEnter.append("circle") // enter the circle on the g
        .attr("r", 5)
        .attr('class', 'circle')
        //.attr('fill', 'red');
  nodeEnter.append("image").attr("class","image")
        .attr("xlink:href", "/static/images/router.png")
        .attr("x", "-12px")
        .attr("y", "-12px")
        .attr("width", "24px")
        .attr("height", "24px")
        .on('mouseover', mouseOverFunction)
        .on('mouseout', mouseOutFunction)
        .on('click', function(d) { return node_click(web_ip,d) } )
  nodeEnter.append("text") // enter the text on the g
        .attr("dy", ".35em")
        .attr("x", 12)
        .style("font-size", "12px")
        .text(function(d) {return d.name ;});

      node = nodeEnter.merge(node); // enter + update

  // Apply the general update pattern to the links.
  link = link.data(links, function(d) { return d.source.name + "-" + d.target.name + "-" + d.l_ip + "-" + d.util + "-" + d.metric; });

  // Keep the exiting links connected to the moving remaining nodes.
  link.exit().transition()
      .attr("stroke-opacity", 0)
      .remove();

  link = link.enter()
        .append("path")
        .attr("stroke","red")
        .attr("class", "link")
        .attr("id",function(d,i) { return "linkId_" + d.l_ip + i; })
        .call(function(link) { link.transition().attr("stroke-opacity", 1); })
        .style("stroke",function(d) {
          if (type == 'traffic'){
            return get_util(d,"0")
          }
	  else if (type == 'demand'){
	    return get_util(d,"0")
          }
          else if (type == 'errors'){
            return get_errors(d,"0")
          }
          else{
            return 'black'
          }
        })
        .on("click",function(d) { return link_click(web_ip,d,'topo')} )
        .merge(link);

  linktext = linktext.data(linkstext, function(d) { return d.source.name + "-" + d.target.name + "-" + d.l_ip + "-" + d.util + "-" + d.metric });
  linktext.exit().transition().remove()
  var linktextEnter = linktext.enter()
                  .append("g")
                  .attr("class","linktext_g")
                  .style( "opacity", 0 )

      linktextEnter.append("text").append("textPath")
                  .attr("class","link_text")
                  .attr("xlink:href",function(d,i) { return "#linkId_" + d.l_ip + i;})
                  .attr("text-anchor","middle")
                  .style("font-size", "4px")
                  .style("font-weight","bold")
                  .attr("dy",0)
                  .attr("startOffset","50%")
                  .text(function(d) {
                    if (type == 'traffic'){
                      return "cost:"  + d.metric + "/IP:"+ d.l_ip
                    }
		    else if ( type == 'demand'){
		      return "cost:"  + d.metric + "/IP:"+ d.l_ip + "/load:"
				+ (d.util*100)/(d.capacity*1000000)+"%"
		    }
                    else if (type == 'errors'){
                      return "errors:"  +parseFloat(d.errors)
                    }
                    else if (type == 'interface'){
                      return "INT: "  + d.l_ip
                    }
                    else{
                      return 'N/A'
                    }
                  })
  linktext = linktextEnter.merge(linktext)

  // Update and restart the simulation.
  simulation.nodes(nodes);
  simulation.force("link").links(links);
  simulation.alpha(1).restart();
  }

  function ticked() {
  link
   .attr("d", function(d,i){
        var LINK_WIDTH = 2
        var targetDistance = (d.linknum % 2 === 0 ? d.linknum * LINK_WIDTH : (-d.linknum + 1) * LINK_WIDTH);
        calcTranslationExact(d.source.name,targetDistance, d.source, d.target);
        return callback;}
      );

  node
    .attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")";});
  }
}
