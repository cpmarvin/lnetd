//zoom
var zoom = d3.zoom()
  .scaleExtent([0.1, 900])
  //.translateExtent([[150, 150],[150, 150]])
  .on('zoom', zoomFn);

function zoomFn() {
  d3.select("#main_svg").select('g')
    .attr("transform", d3.event.transform)
}


function zoomfit() {
  d3.select("#main_svg").select('g').transition().duration(500).attr("transform", "translate(200,80)scale(0.8)")
}


//lnet function
function calcTranslationExact(debug,targetDistance, point0, point1) {
  let x1_x0 = point1.x - point0.x,
  y1_y0 = point1.y - point0.y,
  x2_x0, y2_y0;
  if (y1_y0 === 0) {
    x2_x0 = 0;
    y2_y0 = targetDistance;
  } 
  else {
    let angle = Math.atan((x1_x0) / (y1_y0));
    x2_x0 = -targetDistance * Math.cos(angle);
    y2_y0 = targetDistance * Math.sin(angle);
  }
  d0x= point0.x + (1 * x2_x0)
  d0y= point0.y + (1 * y2_y0)
  d1x= point1.x + ( 1 * x2_x0)
  d1y= point1.y + (1 * y2_y0)
  dx = d1x - d0x,
  dy = d1y - d0y,
  dr = Math.sqrt(dx * dx + dy * dy)
  var endX = (d1x + d0x) / 2;
  var endY = (d1y + d0y) / 2;
  var len = dr - ((dr/2) * Math.sqrt(3));
  endX = endX + (  len/dr) ;
  endY = endY + (  len/dr) ;
    //reverse start and end so that label links switch 
  if ( endX - d0x > 0 ) {
    callback = "M" + d0x + "," + d0y   + "L" + endX + "," + endY;
  }
  else {
    callback = "M" + endX + "," + endY   + "L" + d0x + "," + d0y;
  }
  return {
    callback
  };
}

function data_prepare(DataArray,re_source,re_target) {
  grapheDatas1 = JSON.parse(JSON.stringify(DataArray));
  //console.log('inside data_prepare data is :' ,grapheDatas1)

  function returnX (source) {
  //result is none at first 
  result = 'none'
  //read from position.js
  //console.log(node_position)
  //console.log('source is: ', source)
  node_position.forEach(function (d) {
    //iterate array
    if (source.trim() == d.id.trim()) {
      result = parseInt(d.x)
      //console.log('found') 
    }
  })
  //if forgot to define site name random x 
  if ( result == 'none') { 
    result = Math.floor(1 + Math.random()*(900 + 1 - 1 ))
  }
  //console.log('this is the result:',result)
  return result

  }

//need a better way to do this , repeating function is lame 
function returnY (source) {
  result = 'none'
  node_position.forEach(function (d) {
    if (source.trim() == d.id.trim() ) {
      result = parseInt(d.y)
    }
  })
  if ( result === 'none') { result = Math.floor(1 + Math.random()*(900 + 1 - 1 ))}
    return result
}

grapheDatas1 = grapheDatas1.filter(function(d) { return re_source.test(d.source) && re_target.test(d.target) });
grapheDatas1.sort(function(a,b) {
  if (a.source > b.source) {return 1;}
  else if (a.source < b.source) {return -1;}
  else {
    if (a.target > b.target) {return 1;}
    if (a.target < b.target) {return -1;}
    else {return 0;}
  }
});

for (var i=0; i<grapheDatas1.length; i++) { 
  if (i != 0 &&
    grapheDatas1[i].source == grapheDatas1[i-1].source && grapheDatas1[i].target == grapheDatas1[i-1].target) 
  {
    grapheDatas1[i].linknum = grapheDatas1[i-1].linknum + 1;
  }
  else {
    grapheDatas1[i].linknum = 1;
  };
};

for (var i = 0, len = grapheDatas1.length; i < len; i++) { 
  pair = grapheDatas1[i].l_ip_r_ip[0]+grapheDatas1[i].l_ip_r_ip[1]
  pair = grapheDatas1[i].l_ip_r_ip

  for (var z=0, len=grapheDatas1.length  ; z < len ; z++){
    pair2 = grapheDatas1[z].l_ip_r_ip[0]+grapheDatas1[z].l_ip_r_ip[1]
    pair2 = grapheDatas1[z].l_ip_r_ip
    if (pair2 == pair ) { grapheDatas1[z].linknum = grapheDatas1[i].linknum }

  } 
}
//push_unique id for each link
for (var i=0; i<grapheDatas1.length; i++) {
  grapheDatas1[i].link_id = i
};

var nodes = [];
grapheDatas1.forEach(function(link) {
  //console.log('link.source is : ', link.source)
  link.source = nodes[link.source] || (nodes[link.source] = {name: link.source , fixed:true, fx:returnX(link.source), fy:returnY(link.source), src_icon:link.src_icon });
  link.target = nodes[link.target] || (nodes[link.target] = {name: link.target , fixed:true, fx:returnX(link.target), fy:returnY(link.target) ,src_icon:link.tar_icon });
});

Object.values(nodes).forEach(function(d){
      //console.log(d.name)
      d.weight = grapheDatas1.filter(function(l) {
      return l.source.name == d.name // || l.target.index == d.index
    }).length
})

    return [ Object.values(grapheDatas1) , Object.values(nodes)  ]
}

function getData(url){
  var customAjaxResponse = $.ajax({
                                   type: 'GET',
                                   url: url,
                                   beforeSend: function (xhr) {
                                                  alertify.notify("Refreshing Data", 'warning', 5)

                                                               }
                                   }).done(function (jsondata) {
                                                  alertify.notify("Data Refreshed", 'success', 5)

                                   }).error(function (jqXHR, exception) {
                                                  alertify.notify("Data Refresh error", 'error',15)


                                  });
  return customAjaxResponse.promise();
  }

function link_click(web_ip,d) {
  //console.log("link_click_d",d)
  if (d.l_int == -1 || d.util == -1 ) {
    alert("NO SNMP DATA")
    return
  }
  $('#modal-top').modal('toggle')
  $('#modal-body').attr("id","graph2")
  .html(graph(web_ip,d.node,d.interface,d.capacity,d.direction))
}

function node_click(d) {
  if ($('#spf_check').is(':checked')){
    { return on_node_click(d);console.log("clicked") }
  }
  else {
     console.log("click but not if") 
  }
}

selectedNodes = []
function on_node_click(d) {
  if (selectedNodes.length <2) {
    d3.selectAll(".link").attr("stroke-width",1)
    d3.selectAll(".link").attr("stroke-dasharray",null)
    alert_text = 'selected:' + d.name
    alert(alert_text)
    d3.selectAll(".link").style("stroke",function(d) { return get_util(d,0) })
    selectedNodes.push(d.name)
  }
  if (selectedNodes.length ==2) {
    var spf_div_1 = document.getElementById('sfp_div1');
    spf_div_1.innerHTML =""
    spf_div_1.innerHTML += 'SPF between '+ 'Source: ' +selectedNodes[0]+'  Target: '+selectedNodes[1];
    spf_results = getSPF(selectedNodes[0],selectedNodes[1])
    spf_results = Object.values(spf_results)
    d3.selectAll(".link")
      .style("stroke", function(d) { if (check_link(d.l_ip) == d.l_ip || check_link(d.r_ip) == d.r_ip ) { return "black" } else { return get_util(d,0) } })
    d3.selectAll(".link")
      .attr("stroke-width", function(d) { if (check_link(d.l_ip) == d.l_ip || check_link(d.r_ip) == d.r_ip) { return 5 } else {  1 } })
    d3.selectAll(".link")
      .attr("stroke-dasharray",function(d) { if (check_link(d.l_ip) == d.l_ip || check_link(d.r_ip) == d.r_ip) { return 3.3 } else { } })
    selectedNodes=[]
  }
}

// BEGIN UTIL Function
function get_util(d,start) {
  var legend = [
          {'id':'black','low':0,'high':0},
          {'id':'blue','low':0,'high':20},
          {'id':'green','low':20,'high':40},
          {'id':'yellow','low':40,'high':60},
          {'id':'orange','low':60,'high':85},
          {'id':'red','low':85,'high':100},
          {'id':'fuchsia','low':100,'high':9991050}
        ]
  util = d.util
  if (util == -1)
    { util = "#999"}
  else {
    var cur_util = util
    var capacity = d.capacity*1000000
    util = (cur_util*100)/(capacity)
    legend.forEach(function (d) { 
      if (util >= d.low && util <= d.high) 
      { 
        util = d.id ; 
      }
    })
  }
  return util
}

    function get_errors(d,start) {
      var legend = [
             {'id':'green','low':0,'high':0},
             {'id':'blue','low':0,'high':30},
             {'id':'orange','low':30,'high':2000},
             {'id':'red','low':2000,'high':3000000000050}
            ]
      util = d.errors

      if (util == -1)
        { util = "#999"}
      else {
        util = Math.ceil(util)
        legend.forEach(function (d) { 
          if (util >= d.low && util <= d.high) 
          { 
            util = d.id ; 
          }
        })
      }
      return util
    }

//used in spf calculation , check if link id is equal to spf return 
function check_link(id) {
  result = spf_results[0].filter( function (d) { return d.l_ip == id })
  if (typeof(result[0]) !== "undefined") {
    results = result[0].l_ip 
  }
  else { results = -1 }
    return results 
}



//use to calculated node_weight
function node_weight(d) {
    d.weight = links.filter(function(l) {
      return l.source.index == d.index // || l.target.index == d.index 
    }).length
    return d.weight
  }



//circle
    $('#circle_topology').change(function() {
      if(this.checked){
        var circleCoord = function(node, index, num_nodes){
          var circumference = circle1.node().getTotalLength();
          var pointAtLength = function(l){return circle1.node().getPointAtLength(l)};
          var sectionLength = (circumference)/num_nodes;
          var position = sectionLength*index+sectionLength/2;
          return pointAtLength(circumference-position)
        }

        var width = 950
        var dim = width-100
        var circle1 = d3.select("#main_svg").select("#main_g").append("path")
        .attr("d", "M 40, "+(dim/2+40)+" a "+dim/2+","+dim/2+" 0 1,0 "+dim+",0 a "+dim/2+","+dim/2+" 0 1,0 "+dim*-1+",0")
        .style("fill", "none");
        d3.selectAll(".node").data().forEach(function(d,i) {
          var coord = circleCoord(d, i, nodes.length)
          d.fx = coord.x
          d.fy = coord.y
        })
      }
    });

//tier of connectivity
$('#level_topology').change(function() {
      if(this.checked){
          var pathCoord = function(node, index, num_nodes, level){
                  var circumference = level.node().getTotalLength(); //path lenght
                  var pointAtLength = function(l){return level.node().getPointAtLength(l)}; //function to get the point on the path
                  var sectionLength = (circumference)/num_nodes ; // distance between nodes
                  var position = sectionLength*index+sectionLength/2; // split the nodes
                  return pointAtLength(circumference-position)
                      }
                  var level1 = d3.select("#main_svg").select("#main_g").append("path")
                      .attr("d","M 5 1500 L 3500 1500")

                  var level2 = d3.select("#main_svg").select("#main_g").append("path")
                      .attr("d","M 5 1100 L 3500 1100")
                      .attr("fill","none")

                  var level3 = d3.select("#main_svg").select("#main_g").append("path")
                      .attr("d","M 5 750 L 3500 750")

                  var level4 = d3.select("#main_svg").select("#main_g").append("path")
                      .attr("d","M 5 450 L 3500 450")

                  var level5 = d3.select("#main_svg").select("#main_g").append("path")
                      .attr("d","M 5 200 L 3500 200")

                  var level6 = d3.select("#main_svg").select("#main_g").append("path")
                      .attr("d","M 5 10 L 3500 10")

var re_source_pe = new RegExp ('L..-P[E,1-8]');
var link_number1 = 0
var total_number1 = nodes.filter(function(d) { return d.weight >=1 & d.weight < 5 & !re_source_pe.test(d.name)}).length
console.log(total_number1)
var link_number2 = 0
var total_number2 = nodes.filter(function(d) { return d.weight >=5 & d.weight < 10 & !re_source_pe.test(d.name)}).length
console.log(total_number2)
var link_number3 = 0
var total_number3 = nodes.filter(function(d) { return d.weight >=10 & d.weight < 15  & !re_source_pe.test(d.name)}).length
console.log(total_number3)
var link_number4 = 0
var total_number4 = nodes.filter(function(d) { return d.weight >=15 & d.weight < 20  & !re_source_pe.test(d.name)}).length
console.log(total_number4)
var link_number5 = 0
var total_number5 = nodes.filter(function(d) { return d.weight >=20 & !re_source_pe.test(d.name) }).length
console.log(total_number5)
var link_pe = 0
var total_pe = nodes.filter(function(d) { return re_source_pe.test(d.name) }).length
console.log(total_pe)
          d3.selectAll(".node").data().forEach(function(d,i) {
                var valueToUse
                if (re_source_pe.test(d.name)){
                  valueToUse = level6
                  link_pe = link_pe + 1
                  var coord = pathCoord(d,link_pe , total_pe ,valueToUse)
                              d.fx = coord.x
                              d.fy = coord.y
                }
                else if (d.weight >=1 & d.weight < 5){ //at least 1 link
                  valueToUse = level1
                  link_number1 = link_number1 + 1
                  var coord = pathCoord(d,link_number1 , total_number1 ,valueToUse)
                              d.fx = coord.x
                              d.fy = coord.y
                }
                else if (d.weight >=5 & d.weight < 10){
                  valueToUse = level2
                  link_number2 = link_number2 + 1
                  var coord = pathCoord(d,link_number2 , total_number2 ,valueToUse)
                              d.fx = coord.x
                              d.fy = coord.y
                }
                else if (d.weight >=10 & d.weight < 15){
                  valueToUse = level3
                  link_number3 = link_number3 + 1
                  var coord = pathCoord(d,link_number3 , total_number3 ,valueToUse)
                              d.fx = coord.x
                              d.fy = coord.y
                }
                else if (d.weight >=15 & d.weight < 20){
                  valueToUse = level4
                  link_number4 = link_number4 + 1
                  var coord = pathCoord(d,link_number4 , total_number4 ,valueToUse)
                              d.fx = coord.x
                              d.fy = coord.y
                }
                else if (d.weight >=20 ){
                  valueToUse = level5
                  link_number5 = link_number5 + 1
                  var coord = pathCoord(d,link_number5 , total_number5 ,valueToUse)
                              d.fx = coord.x
                              d.fy = coord.y
                }
                var temp_sel = d3.selectAll(".node").selectAll('text')
                    temp_sel.attr("dy", "1.5em")
                            .attr("x","-35")
                            .text(function(d) { return d.name; })
          })
      }
  });
