function lnet_failed_d3js(web_ip,result,type){
  nodes_layer1 = result[1]
  links_layer1 = result[0]
  linkstext_layer1 = result[0]
  var linkedByIndex = {}
  links_layer1.forEach((d) => {
    linkedByIndex[`${d.source.name},${d.target.name}`] = true;
  });
  var width = 1400;
  var height = 800;
  var svg = d3.select("#topology_failed").append("svg")
        .call(zoom_layer1)
        .attr("id","main_svg_layer1")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", [0, 0, width, height])

  var simulation_layer1 = d3.forceSimulation(nodes_layer1)
      .force("charge", d3.forceManyBody().strength(-800))
      .force("link", d3.forceLink(links_layer1).distance(10).strength(0))
      .force("x", d3.forceX(300)) //center to x 300 , only used when dynamic
      .force("y", d3.forceY(300)) // center to y 300, only used when dynamic
      .alphaDecay(1)
      .alphaTarget(0)
      .on("tick", ticked_layer1);

  var g = svg.append("g").attr("id","main_g_layer1")
      link_layer1 = g.append("g").selectAll(".link_layer1"),
      linktext_layer1 = g.append("g").selectAll(".link_text_layer1"),
      node_layer1 = g.append("g").selectAll(".node_layer1");

  this.restart = function(nodes_layer1,links_layer1,linkstext_layer1){
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
    var dragDrop = d3.drag().on('start', function (node_layer1) {
                  node_layer1.fx = node_layer1.x
                  node_layer1.fy = node_layer1.y
                }).on('drag', function (node_layer1) {
                  simulation_layer1.alphaTarget(1).restart()
                  node_layer1.fx = d3.event.x
                  node_layer1.fy = d3.event.y
                }).on('end', function (node_layer1) {
                  if (!d3.event.active) {
                    simulation_layer1.alphaTarget(0)
                  }
                  node_layer1.fx = node_layer1.x
                  node_layer1.fy = node_layer1.y
                })
//end
//drag
const mouseOverFunction = function (d) {
  // const circle = d3.select(this); //not needed for now
  node_layer1
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

  link_layer1
    .transition(500)
      .style('stroke-opacity', o => (o.source.name === d.name || o.target.name === d.name ? 1 : 0.2))
      .transition(500)
  linktext_layer1
      .transition(500)
      .style('opacity', o => (o.source.name === d.name || o.target.name === d.name ? 1 : 0))
      .transition(500)

};

const mouseOutFunction = function () {
  //const circle = d3.select(this);

  node_layer1
    .transition(500)
     .style("opacity",1);

  link_layer1
    .transition(500)
     .style("stroke-opacity",1);
  linktext_layer1
    .transition(200)
     .style("opacity",0);

};
  // Apply the general update pattern to the nodes.
  node_layer1 = node_layer1.data(nodes_layer1, function(d) { return d.name ;});

  node_layer1.exit().transition()
      .attr("r", 0)
      .remove();

  var nodeEnter = node_layer1.enter() // enter, append the g
    .append("g")
    .call(dragDrop)
    .attr("class", "node_layer1");

  nodeEnter.append("circle") // enter the circle on the g
        .attr("r", 5)
        .attr('class', 'circle')
        //.attr('fill', 'red');
  nodeEnter.append("image").attr("class","image")
        .attr("xlink:href", "/static/images/router.png")
        .attr("x", "-18px")
        .attr("y", "-18px")
        .attr("width", "34px")
        .attr("height", "34px")
        .on('mouseover', mouseOverFunction)
        .on('mouseout', mouseOutFunction)
        .on('click', function(d) { return node_click(web_ip,d) } )
  nodeEnter.append("text") // enter the text on the g
        .attr("dy", ".35em")
        .attr("x", 12)
        .style("font-size", "12px")
        .text(function(d) {return d.name ;});
        //.text("")

      node_layer1 = nodeEnter.merge(node_layer1); // enter + update

  // Apply the general update pattern to the links.
  link_layer1 = link_layer1.data(links_layer1, function(d) { return d.source.name + "-" + d.target.name + "-" + d.status; });

  // Keep the exiting links connected to the moving remaining nodes.
  link_layer1.exit().transition()
      .attr("stroke-opacity", 0)
      .remove();

  link_layer1 = link_layer1.enter()
        .append("path")
        .attr("stroke","red")
        .attr("class", "link")
        .attr("id",function(d,i) { return "linkId_layer1_" + d.l_ip + i; })
        .call(function(link_layer1) { link_layer1.transition().attr("stroke-opacity", 1); })
        .style("stroke",function(d) {
            if (d.status == "up") {return "green"}
            else { return "red" }
         })
        //.style("stroke-width", function(d) { return 2 })
        .merge(link_layer1);

  linktext_layer1 = linktext_layer1.data(linkstext_layer1, function(d) { return d.source.name + "-" + d.target.name + "-" + d.l_ip + "-" + d.util + "-" + d.metric });
  linktext_layer1.exit().transition().remove()

  var linktextEnter = linktext_layer1.enter()
                  .append("g")
                  .attr("class","linktext_g")
                  .style( "opacity", 0 )

      linktextEnter.append("text").append("textPath")
                  .attr("class","link_text")
                  .attr("xlink:href",function(d,i) { return "#linkId_layer1_" + d.l_ip + i;})
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
  linktext_layer1 = linktextEnter.merge(linktext_layer1)

  // Update and restart the simulation.
  simulation_layer1.nodes(nodes_layer1);
  simulation_layer1.force("link").links(links_layer1);
  simulation_layer1.alpha(1).restart();
  }

  function ticked_layer1() {
  link_layer1
   .attr("d", function(d,i){
        var LINK_WIDTH = 2
        var targetDistance = (d.linknum % 2 === 0 ? d.linknum * LINK_WIDTH : (-d.linknum + 1) * LINK_WIDTH);
        calcTranslationExact(d.source.name,targetDistance, d.source, d.target);
        return callback;}
      );

  node_layer1
    .attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")";});
  }

}
