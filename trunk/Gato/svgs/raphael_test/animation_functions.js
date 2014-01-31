function Animation() {
	this.do_command = function(anim) {
		if (anim.length === 3) {
			anim[1](anim[2]);
		} else if (anim.length === 4) {
			anim[1](anim[2], anim[3]);
		} else {
			anim[1](anim.slice(2));
		}
	}
	this.animator = function() {
		if (this.state !== 'animating') {
			return;
		}
		if (this.step_num >= anim_array.length) {
			this.state = 'stopped';
			g.button_panel.set_buttons_state('stopped');
			return;
		}

		var anim = anim_array[this.step_num];
		this.do_command(anim);
		this.step_num ++;
		var self = this;
		this.scheduled_animation = setTimeout(function() {self.animator()}, anim[0]*this.step_ms);
	}

	this.start = function() {
		if (this.state !== 'stopped') {
			return;
		}
		this.state = 'animating';
		this.animator();
	}

	this.stop = function() {
		if (this.state === 'animating' || this.state === 'stopped') {
			this.state = 'stopped';
			clearTimeout(this.scheduled_animation);
		}
	}
	
	this.continue = function() {
		if (this.state !== 'stepping') {
			return;
		}
		this.state = 'animating';
		this.animator();
	}

	this.step = function() {
		if (this.state === 'animating' || this.state === 'stepping') {
			this.state = 'stepping';
			clearTimeout(this.scheduled_animation);
			this.do_command(anim_array[this.step_num]);
			this.step_num ++;
		}
	}

	this.construct_graph_states = function() {

	}

	this.initialize_variables = function() {
		this.states = ['animating', 'stopped', 'stepping'];
		this.state = 'stopped';
		this.step_ms = 1;
		this.step_num = 0;

		// TODO: Do graph states
		this.graph_states = []
	}
	this.initialize_variables();
}

function start_animation() {
	g.running = true;
	for (var i=0; i<animation.length; i++) {	
		(function (index) {
			setTimeout(function() {
				animation[index][1](animation[index][2], animation[index][3]);
			}, g.step_ms*i);
		})(i);
	}
}

function step_animation() {

}

function continue_animation() {

}

function stop_animation() {

}



/**
*
*	Graph Modifying Functions
*
* /


/** Sets the vertex given by vertex_id to color */
function SetVertexColor(vertex_id, color) {
	g.vertices[vertex_id].attr('fill', color);
}

function UpdateEdgeInfo(edge_id, info) {

}

function UpdateGraphInfo(graph_id, info) {

}

/** Sets the given edge to the given color.  If the given edge
	is not found, then the reverse direction is tried, e.g. if g1_(5, 4) is
	not found we will try g1_(4, 5)
*/
function SetEdgeColor(edge_id, color) {
	console.log(edge_id);
	function switch_edge_vertices() {
	    // Switches the edge_id vertices.  ie. g1_(5, 4) in --> g1_(4, 5) out
	    // TODO: Test me
	    var re = /\d+/g;
	    var matches = edge_id.match(re);
	    return "g" + matches[0] + "_(" + matches[1] + ", " + matches[2] + ")";
	}
	var edge = g.edges[edge_id];
	if (edge === null) {
		edge_id = switch_edge_vertices();
		edge = g.edges[edge_id];
	}
	edge.attr({'stroke': color});
    
    var edge_arrow = g.edge_arrows[(g.arrow_id_prefix + edge_id)];
    if (edge_arrow !== undefined) {
    	edge_arrow.attr({'fill': color});
    }
}

/** Sets color of all vertices of a given graph to a given color.
* 	graph_id_and_color is string of form "g{graph_num}_#{hex_color}"
* 	If vertices != null, then only color the set of vertices specified by vertices
*/
function SetAllVerticesColor() {
	var graph_id_and_color = arguments[0];
	var vertices = arguments[1];
	// TODO: Modify this to use variable length args instead of vertices 
	var split = graph_id_and_color.split('_');
	var graph_id = split[0];
	var color = split[1];

	if (vertices == null) {
		for (var key in g.vertices) {
			g.vertices[key].attr({'fill': color});
		}
	} else {
		for (var i=0; i<vertices.length; i++) {
			g.vertices[vertices[i]].attr({'fill': color});
		}
	}
}


/** Sets all edges of given graph to color.  param is of form: "g1_#dd3333" */
function SetAllEdgesColor(graph_id_and_color) {
    var split = graph_id_and_color.split('_');
    var graph = split[0];
    var color = split[1];
    var graph_edges = g.edges[graph];
    var edge_arrows = g.edge_arrows[graph];
    for (var i=0; i<graph_edges.length; i++) {
    	graph_edges[i].attr({'stroke': color});
    	if (edge_arrows.length > i) {
    		edge_arrows[i].attr({'fill': color});
    	}
    }
}


/** Blinks the given vertex between black and current color 3 times */
function BlinkVertex(vertex_id, color) {
	var vertex = g.vertices[vertex_id];
    var curr_color = vertex.attr('fill');
    for (var i=0; i<6; i+=2) {
    	setTimeout(function() { vertex.attr({'fill': 'black'}); }, g.step_ms*(i));
    	setTimeout(function() { vertex.attr({'fill': curr_color}); }, g.step_ms*(i+1));
    }
}

/** Blinks the given edge between black and current color 3 times */
function BlinkEdge(edge_id, color){
    var edge = document.getElementById(edge_id);
    var curr_color = edge.getAttribute('stroke');
    for (var i=0; i<6; i+=2) {
    	setTimeout(function() { edge.setAttribute('stroke',  'black'); }, g.step_ms*(i));
    	setTimeout(function() { edge.setAttribute('stroke', curr_color); }, g.step_ms*(i+1));
    }
}

//Blink(self, list, color=None):
//Sets the frame width of a vertex
function SetVertexFrameWidth(vertex_id, val) {
	// Take away dropshadow
    var vertex = g.vertices[vertex_id];
	if (val !== '0') {
        vertex.attr({"style": ""});
	}
    vertex.attr({'stroke-width': val});

    // Add back in dropshadow
    if (val === "0") {
        vertex.attr({"style": "filter:url(#dropshadow)"});
    }
}

//Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(v, annotation, color) //removed 'this' parameter to because 'this' parameter was assigned value of v, v of annotation, and so on.
{
}


//Line with specified id is highlighted.  Becomes current line of code.  Previous highlight is removed.
function ShowActive(line_id){
    
}


//Directed or undirected added to graph.
function AddEdge(edge_id){
    
}

//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id){

}

//Adds vertex of into specified graph and coordinates in graph.  Optional id argument may be given.
function AddVertex(graph_and_coordinates, id){

}