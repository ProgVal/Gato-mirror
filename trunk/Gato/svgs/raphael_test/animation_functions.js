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

		g.slider.go_to_step(this.step_num);
		var anim = anim_array[this.step_num];
		this.do_command(anim);
		this.step_num ++;
		var self = this;
		this.scheduled_animation = setTimeout(function() {self.animator()}, anim[0]*this.step_ms);
	}

	/* Animator that executes animation commands until 
	the given index with no timeout in between commands */
	this.animate_until = function(stop_at_ind) {
		for (var i=this.step_num; i<stop_at_ind; i++) {
			this.do_command(anim_array[i]);
			this.step_num ++;
		}
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

	this.jump_to_step = function(n) {
		var state_ind = parseInt(n/this.state_interval);
		var state = this.graph_states[state_ind];
		for (var i=0; i<g.graph_elem_types.length; i++) {
			var elem_type = g.graph_elem_types[i];
			var elem_state = state[elem_type];
			for (var id in elem_state) {
				var elem = snap.select('#' + id);
				if (elem == null) {
					// We need to create the element
					// Call the appropriate snap function and add the leement
					// elem = snap.
				}
				for (var attr in elem_state[id]) {
					var params = {};
					params[attr] = elem_state[id][attr];
					elem.attr(params);
				}
			}

			// Remove any elements that shouldn't be in global values
			var global_elem_state = g[elem_type];
			for (var id in global_elem_state) {
				if (!(id in elem_state)) {
					// Delete the element g[global_elem_state]][id]
				}
			}
		}
		this.step_num = state.step_num;
		this.animate_until(n);
		g.slider.go_to_step(n);
	}

	/*
		Builds the Graph State array to use for playback
	*/
	this.construct_graph_states = function() {
		function collect_attr(elem) {
			var our_attr = {};
			var attributes = elem.node.attributes;
			for (var i=0; i<attributes.length; i++) {
				var attr = attributes[i];
				our_attr[attr.name] = attr.value;
			}
			return our_attr;	
		}
		
		function construct_state(step_num) {
			// TODO: This will need to be changed for two graph operation
			var state = {'step_num': step_num};
			for (var i=0; i<g.graph_elem_types.length; i++) {
				var elem_type = g.graph_elem_types[i];
				var elem_obj = g[elem_type];
				state[elem_type] = {};
				for (var key in elem_obj) {
					state[elem_type][key] = collect_attr(elem_obj[key]);
				}
			}
			return state;
		}
		
		var states = [];
		console.log(anim_array.length);
		for (var i=0; i<anim_array.length; i++) {
			if (i % this.state_interval === 0) {
				states.push(construct_state(i))
			}
			this.do_command(anim_array[i]);
		}

		this.graph_states = states;
		this.jump_to_step(0);
	}



	this.initialize_variables = function() {
		// State of animation		
		this.states = ['animating', 'stopped', 'stepping'];
		this.state = 'stopped';
		
		// Our step interval in milliseconds
		this.step_ms = 1;
		
		// Current step in the animation
		this.step_num = 0;

		// How many steps we take between each saved graph state
		this.state_interval = 200; 

		// TODO: Do graph states
		this.construct_graph_states();
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


function Slider(width, height) {
	this.mousedown = function(evt) {
		console.log('clicked');
		g.slider.sliding = true;
		g.slider.start_cursor_x = parseInt(g.slider.cursor.attr('x'));
		g.slider.start_mouse_x = parseInt(evt.x);
	}
	this.drag = function(evt) {
		this.mouseup(evt);
	}
	this.mousemove = function(evt) {
		var step = 0;		
		var new_x = this.start_cursor_x + parseInt(evt.x) - g.slider.start_mouse_x;
		if (new_x > this.cursor_max_x) {
			new_x = this.cursor_max_x;
			step = anim_array.length - 1;
		} else if (new_x < this.cursor_min_x) {
			new_x = this.cursor_min_x;
			step = 0;
		} else {
			step = parseInt(new_x / this.step_width) + 1;
		}
		this.cursor.attr({'x': new_x});
		g.animation.jump_to_step(step);
	}
	this.mouseup = function(evt) {
		this.sliding = false;
	}

	this.go_to_step = function(n) {
		this.cursor.attr({'x': n*this.step_width});
	}

	this.sliding = false;
	this.width = width;
	this.height = height;
	this.step_width = this.width / anim_array.length;
	this.g = snap.group();

	this.track_width = this.width;
	this.track_height = 8;
	this.track_y = this.height/2-this.track_height/2;
	this.track = snap.rect(0, this.track_y, this.width, this.track_height, 2, 2).attr({
		'fill': '#AAA'
	});
	this.g.append(this.track);

	this.cursor_height = this.height;
	this.cursor_width = 10;
	this.cursor = snap.rect(0, 0, this.cursor_width, this.cursor_height, 6, 6).attr({
		'fill': '#eee',
		'stroke': '#111',
		'stroke-width': 1
	}).mousedown(this.mousedown);
	this.cursor_max_x = this.width - this.cursor_width;
	this.cursor_min_x = 0;
	this.g.append(this.cursor);
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
	function switch_edge_vertices() {
	    // Switches the edge_id vertices.  ie. g1_(5, 4) in --> g1_(4, 5) out
	    // TODO: Test me
	    var re = /\d+/g;
	    var matches = edge_id.match(re);
	    return "g" + matches[0] + "_" + matches[1] + "-" + matches[2];
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
