function generate_ASR_9910(rtr1_chassis) {

    var chasssis_9910 = [
    { "x": 30, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP0/CPU0" ,'text_dx': 38 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/0/CPU0" ,'text_dx': 52 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/1/CPU0" ,'text_dx': 68 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/2/CPU0" ,'text_dx': 83 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/3/CPU0" ,'text_dx': 98 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/4/CPU0" ,'text_dx': 112 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/5/CPU0" ,'text_dx': 127 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/6/CPU0" ,'text_dx': 143 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/7/CPU0" ,'text_dx': 158 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 173 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_9910)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.x + 8; })
    .attr("y",  function(d) { return d.y * 6; })
    .attr("dy", "-.40em")
    .text(function(d) { return d.name; })
    .style("text-anchor", "middle")
    .style("alignment-baseline","central")
    .style("writing-mode","vertical-rl")


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 195; })
      .attr("height", function(d) { return 300; })
      .attr("fill","none");
}

function generate_ASR_9010_AC(rtr1_chassis) {
    var chasssis_9010 = [
    { "x": 30, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/0/CPU0" ,'text_dx': 38 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/1/CPU0" ,'text_dx': 52 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/2/CPU0" ,'text_dx': 68 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/3/CPU0" ,'text_dx': 83 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 98 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 112 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/4/CPU0" ,'text_dx': 127 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/5/CPU0" ,'text_dx': 143 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/6/CPU0" ,'text_dx': 158 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/7/CPU0" ,'text_dx': 173 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_9010)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 195; })
      .attr("height", function(d) { return 300; })
      .attr("fill","none");
}

function generate_ASR_9010_DC_V2(rtr1_chassis) {
    var chasssis_9010 = [
    { "x": 30, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/0/CPU0" ,'text_dx': 38 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/1/CPU0" ,'text_dx': 52 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/2/CPU0" ,'text_dx': 68 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/3/CPU0" ,'text_dx': 83 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 98 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 112 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/4/CPU0" ,'text_dx': 127 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/5/CPU0" ,'text_dx': 143 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/6/CPU0" ,'text_dx': 158 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/7/CPU0" ,'text_dx': 173 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_9010)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 195; })
      .attr("height", function(d) { return 300; })
      .attr("fill","none");
}

function generate_ASR_9010_AC_V2(rtr1_chassis) {
    var chasssis_9010 = [
    { "x": 30, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/0/CPU0" ,'text_dx': 38 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/1/CPU0" ,'text_dx': 52 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/2/CPU0" ,'text_dx': 68 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/3/CPU0" ,'text_dx': 83 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 98 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/RSP1/CPU0" ,'text_dx': 112 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/4/CPU0" ,'text_dx': 127 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/5/CPU0" ,'text_dx': 143 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/6/CPU0" ,'text_dx': 158 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":280 ,"color" : "white" , "name": "0/7/CPU0" ,'text_dx': 173 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_9010)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 195; })
      .attr("height", function(d) { return 300; })
      .attr("fill","none");
}

function generate_MX10003(rtr1_chassis) {
    var chasssis_10003 = [
    { "x": 15, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "Routing Engine 0" ,'text_dx': 18 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    { "x": 150, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "Routing Engine 1" ,'text_dx': 158 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    { "x": 15, "y": 90, "width": 265, "height":20 ,"color" : "white" , "name": "FPC 0" ,'text_dx': 18 ,'text_dy': 112, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    { "x": 15, "y": 120, "width": 265, "height":20 ,"color" : "white" , "name": "FPC 1" ,'text_dx': 18 ,'text_dy': 142, 'text_dy_em': '-.40em','text_mode':'vertical-lb'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_10003)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 280; })
      .attr("height", function(d) { return 150; })
      .attr("fill","none");
}

function generate_MX204(rtr1_chassis) {
    var chasssis_204 = [
    { "x": 15, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "FPC 0" ,'text_dx': 18 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    { "x": 150, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "Routing Engine 0" ,'text_dx': 158 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_204)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 280; })
      .attr("height", function(d) { return 50; })
      .attr("fill","none");
}

function generate_NE40E_X8(rtr1_chassis) {
    var chasssis_NE40E_X8 = [
    { "x": 30, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "1/0" ,'text_dx': 38 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "2/0" ,'text_dx': 52 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "3/0" ,'text_dx': 68 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "4/0" ,'text_dx': 83 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "9/0" ,'text_dx': 98 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "11/0" ,'text_dx': 112 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "10/0" ,'text_dx': 127 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "5/0" ,'text_dx': 143 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "6/0" ,'text_dx': 158 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "7/0" ,'text_dx': 172 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 180, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "8/0" ,'text_dx': 187 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},    
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_NE40E_X8)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return d.color } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 205; })
      .attr("height", function(d) { return 300; })
      .attr("fill","none");
}

function generate_NE40E_X8A(rtr1_chassis) {
    var chasssis_NE40E_X8A = [
    { "x": 30, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "1/0" ,'text_dx': 38 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "2/0" ,'text_dx': 52 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "3/0" ,'text_dx': 68 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "4/0" ,'text_dx': 83 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "9/0" ,'text_dx': 98 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":280 ,"color" : "orange" , "name": "11/0" ,'text_dx': 112 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":280 ,"color" : "orange" , "name": "12/0" ,'text_dx': 127 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "10/0" ,'text_dx': 143 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "5/0" ,'text_dx': 158 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "6/0" ,'text_dx': 172 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 180, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "7/0" ,'text_dx': 187 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},    
    { "x": 195, "y": 30, "width": 15, "height":280 ,"color" : "green" , "name": "8/0" ,'text_dx': 203 ,'text_dy': 150, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_NE40E_X8A)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return d.color } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 215; })
      .attr("height", function(d) { return 300; })
      .attr("fill","none");
}

function generate_R_IOSXRV9000_CC(rtr1_chassis) {
    var chasssis_204 = [
    { "x": 15, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "0/0" ,'text_dx': 18 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    { "x": 150, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "0/RP0" ,'text_dx': 158 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_204)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 280; })
      .attr("height", function(d) { return 50; })
      .attr("fill","none");
}

function generate_VMX(rtr1_chassis) {
    var chasssis_204 = [
    { "x": 15, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "FPC 0" ,'text_dx': 18 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    { "x": 150, "y": 30, "width": 130, "height":20 ,"color" : "white" , "name": "Routing Engine" ,'text_dx': 158 ,'text_dy': 52, 'text_dy_em': '-.4em','text_mode':'vertical-lb'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_204)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return 'green' } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 280; })
      .attr("height", function(d) { return 50; })
      .attr("fill","none");
}

function generate_MX2008(rtr1_chassis) {
    var chasssis_MX2008 = [
    { "x": 30, "y": 30, "width": 15, "height":110 ,"color" : "green" , "name": "Routing Engine 0" ,'text_dx': 38 ,'text_dy': 40, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":110 ,"color" : "green" , "name": "Routing Engine 1" ,'text_dx': 173 ,'text_dy': 40, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB0" ,'text_dx': 52 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 1" ,'text_dx': 68 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 2" ,'text_dx': 83 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 3" ,'text_dx': 98 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 4" ,'text_dx': 112 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 5" ,'text_dx': 127 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 6" ,'text_dx': 143 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":110 ,"color" : "orange" , "name": "SFB 7" ,'text_dx': 158 ,'text_dy': 80, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 30, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 0" ,'text_dx': 38 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 1" ,'text_dx': 52 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 2" ,'text_dx': 68 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 3" ,'text_dx': 83 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 4" ,'text_dx': 98 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 5" ,'text_dx': 112 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 6" ,'text_dx': 127 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 7" ,'text_dx': 143 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 8" ,'text_dx': 158 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 140, "width": 15, "height":180 ,"color" : "green" , "name": "FPC 9" ,'text_dx': 173 ,'text_dy': 200, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_MX2008)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return d.color } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 195; })
      .attr("height", function(d) { return 320; })
      .attr("fill","none");
}

function generate_ASR_9922(rtr1_chassis) {
    var chasssis_ASR9922 = [
    { "x": 30, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/0/CPU0" ,'text_dx': 38 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/1/CPU0" ,'text_dx': 173 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/2/CPU0" ,'text_dx': 52 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/3/CPU0" ,'text_dx': 68 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/4/CPU0" ,'text_dx': 83 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/5/CPU0" ,'text_dx': 98 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/6/CPU0" ,'text_dx': 112 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/7/CPU0" ,'text_dx': 127 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/8/CPU0" ,'text_dx': 143 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 30, "width": 15, "height":100 ,"color" : "green" , "name": "0/9/CPU0" ,'text_dx': 158 ,'text_dy': 50, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 30, "y": 130, "width": 16.6, "height":110 ,"color" : "green" , "name": "0/RP0/CPU0" ,'text_dx': 38 ,'text_dy': 145, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 46.6, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC0/SP" ,'text_dx': 55 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 63.2, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC1/SP" ,'text_dx': 72 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 79.8, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC2/SP" ,'text_dx': 89 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 96.4, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC3/SP" ,'text_dx': 106 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 113, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC4/SP" ,'text_dx': 122 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 129.6, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC5/SP" ,'text_dx': 138 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 146.2, "y": 130, "width": 16.6, "height":110 ,"color" : "orange" , "name": "0/FC6/SP" ,'text_dx': 155 ,'text_dy': 155, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 162.8, "y": 130, "width": 16.9, "height":110 ,"color" : "green" , "name": "0/RP1/CPU0" ,'text_dx': 172 ,'text_dy': 145, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 30, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/10/CPU0" ,'text_dx': 38 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 45, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/11/CPU0" ,'text_dx': 52 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 60, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/12/CPU0" ,'text_dx': 68 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 75, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/13/CPU0" ,'text_dx': 83 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 90, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/14/CPU0" ,'text_dx': 98 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 105, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/15/CPU0" ,'text_dx': 112 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 120, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/16/CPU0" ,'text_dx': 127 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 135, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/17/CPU0" ,'text_dx': 143 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 150, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/18/CPU0" ,'text_dx': 158 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    { "x": 165, "y": 234, "width": 15, "height":100 ,"color" : "green" , "name": "0/19/CPU0" ,'text_dx': 173 ,'text_dy': 250, 'text_dy_em': '-.40em','text_mode':'vertical-rl'},
    ];

var svg = d3.select("#chassis_rtr").append("svg")
    .attr("width", 400)
    .attr("height", 400)
    .append("g")


var node = svg.selectAll(".node")
    .data(chasssis_ASR9922)
    .enter().append("g")

node.append("rect")
      .attr("x", function(d) { return  d.x })
      .attr("y",function(d) { return  d.y})
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .attr("fill",function(d) { if (rtr1_chassis.includes(d.name)) { return  "red" } else { return d.color } });

node.append("text")
    .attr("x", function(d) { return d.text_dx })
    .attr("y",  function(d) { return d.text_dy })
    .attr("dy", function(d) { return d.text_dy_em})
    .text(function(d) { return d.name; })
    //.style("text-anchor", "middle")
    //.style("alignment-baseline","central")
    .style("writing-mode", function(d) { return d.text_mode})


svg.append("rect")
      .attr("x", function(d) { return  10})
      .attr("y",function(d) { return  20 })
      .attr("stroke-width",3)
      .attr("stroke","black")
      .attr("width", function(d) { return 195; })
      .attr("height", function(d) { return 320; })
      .attr("fill","none");
}

