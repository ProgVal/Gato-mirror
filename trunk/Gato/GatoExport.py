#!/usr/bin/env python2.6
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoExport.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 2010, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schliep.org, winfried.hochstaettler@fernuni-hagen.de
#
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#
#
#       This file is version $Revision: 353 $ 
#                       from $Date: 2010-06-03 14:58:37 -0400 (Thu, 03 Jun 2010) $
#             last change by $Author: schliep $.
#
################################################################################
import os
import StringIO
import tokenize
from math import sqrt, pi, sin, cos, atan2, degrees, log10, floor

# SVG Fileheader and JavaScript animation code
#
animationhead = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm"
onload="Initialize(evt)">
<defs> 
    <marker id="Arrowhead" 
      viewBox="0 0 10 10" refX="0" refY="5" 
      markerUnits="strokeWidth" 
      markerWidth="4" markerHeight="3" 
      orient="auto"> 
      <path d="M 0 0 L 10 5 L 0 10 z" /> 
    </marker> 
    
    <linearGradient id="active_button_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="blue">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    
    <linearGradient id="inactive_button_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="blue" stop-opacity="0">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    
    
    
    <linearGradient id="slider_bar_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="skyblue" >
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    <linearGradient id="slider_thumb_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="#C0C0C0">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
</defs>
<script type="text/ecmascript"><![CDATA[
var step = 0;
var v_ano_id = "va"; //ID prefix for vertex annotation
var e_arrow_id = "ea"; //ID prefix for edge arrow
var svgNS="http://www.w3.org/2000/svg";
var the_evt;
var element;
var blinkcolor;
var blinkcount;
var e_blinkcolor;
var e_blinkcount;


var code;    //tracks HTB of code.  Vertical layout
var init_graphs;  //initial graph, for restarting
var action_panel;   //tracks buttons
var state;	//tracks state of animation
var timer;	//variable for timer for AnimateLoop
var timeout = 50;  //Initial timeout
var horiz_layout;  //horizontal layout manager of visible elements
var vert_layout;   //vertical layout manager of visible elements
var speed_slider;  //Manages speed settings of animation
var current_line = -1;  //Currently 'executing' line of code in program
var default_vertex_radius = 14.0; //Default vertex radius
var default_line_width = 4.0; //Default line width
var x_offset = 20;  //Twice the distance the layout is translated horizontally, in pixels
var y_offset = 20;  //Twice the distance layout is translated vertically, in pixels


/**
*
*
*
* Helper functions
*
*
**/
//Accepts a string of the form "transform(x y)" and returns x and y in a 2-index array
function getTranslate(str){
	var x;
	var y;
	
	if(str == null){
		return new Array(0, 0);
	}
	
	var to_parse = str.slice(str.indexOf("translate") + "translate".length);
	
	if(to_parse == null){
		return new Array(0, 0);
	}
	
	
	var r = to_parse.match(/[^,\(\)\sA-Za-z]+/g);;
	
	if(r[0] != null){
		x = parseFloat(r[0]);
	}
	
	if(r[1] != null){
		y = parseFloat(r[1]);
	}
	
	if(r[1] == null || (to_parse.indexOf(")") < to_parse.indexOf(r[1]))){
		return new Array(x, 0);
	}
	
	return new Array(x, y);

}

//Sets the first instance of "translate" in components "transform" attribute to "translate(x y)"
function setTranslate(component, x, y){
	var transformation = component.getAttribute("transform");
	
	if(transformation != null){
		var header = transformation.substring(0, transformation.indexOf("translate") + "translate".length);
		if(transformation.indexOf("translate") == -1){
			component.setAttribute("transform", transformation + " translate(" + x + " " + y + ")");
		}else{

			var trailer = transformation.slice(transformation.indexOf("translate") + "translate".length);
			trailer = trailer.slice(trailer.indexOf(")"));
		
			var newattr = header + "(" + x + " " + y + trailer;

			component.setAttribute("transform", newattr);
		}

	}else{
		component.setAttribute("transform", "translate(" + x + " " + y + ")");
	}
}

//Return a 2-index array [v1,v2] which has an angle of
//90 degrees clockwise to the vector (dx,dy)
function Orthogonal(dx, dy){

	var u1 = dx;
	var u2 = dy;
	
	var length = Math.sqrt(Math.pow(u1,2) + Math.pow(u2,2));
	
	if(length < 0.001){
		length = 0.001;
	}
	
	u1 /= length;
	u2 /= length;
	return [-1*u2, u1];
}

//Creates an arrowhead aligned with line starting at (vx,vy) and ending at (wx,wy)
//Arrowhead has specified id and ends outside the radius of a vertex with cx=wx and cy=wy
function createArrowhead(vx, vy, wx, wy, stroke_width, id){

 		var l = Math.sqrt(Math.pow(parseFloat(wx)-parseFloat(vx),2) + Math.pow(parseFloat(wy)-parseFloat(vy), 2));
		
		
                if (l < .001)
                    l = .001;
		    	
		var a_width = (1 + 1.5/(1*Math.pow(Math.log(parseFloat(stroke_width))/Math.log(10), 6)));

                if(a_width > 5.0)
                    a_width = 5.0;
		    
		var cr = default_vertex_radius;
		
                a_width = a_width * parseFloat(stroke_width);

                var p1 = [0,0];
                var p2 = [0, a_width];
                var p3 = [cr, a_width/2];
                var angle = (Math.atan2(parseInt(wy)-parseInt(vy), parseInt(wx)-parseInt(vx))) * 180/Math.PI;
                var c = (l-2*default_vertex_radius)/l;
                var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
                var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
		
		var arrowhead = the_evt.target.ownerDocument.createElementNS(svgNS, "polyline");
		arrowhead.setAttribute("points", p1[0] + " " + p1[1] + " " + p2[0] + " " + p2[1] + " " + p3[0] + " " + p3[1]);
		arrowhead.setAttribute("fill", "#EEEEEE");
		arrowhead.setAttribute("transform", "translate(" + tmpX + " " + (tmpY-a_width/2) + ") rotate(" + angle + " " + p1[0] + " " + a_width/2 + ")");
		arrowhead.setAttribute("id", id);

                return arrowhead;
}




/**
*
*
*
* Classes for visible components
*
*
*/
//Highlightable block of text
//Accepts parameters: horizontal and vertical padding between lines, id, font size of text, and layout mode (horizontal or vertical)
function HighlightableTextBlock(hp, vp, id, font_size, layout){
	this.line_llc = new LinearLayoutComponent(hp, vp, id, layout);
	this.line_llc.group.setAttribute("font-size", font_size);
	this.highlight_group = the_evt.target.ownerDocument.createElementNS(svgNS,"g");
	this.highlight_group.setAttribute("id", id + "_hg");
	the_evt.target.ownerDocument.documentElement.insertBefore(this.highlight_group, this.line_llc.group);	
}

//Initializes prototype, to call object.function
function HTB_prototypeInit(){
	var htb = new HighlightableTextBlock(2,2,"foo",14, "vertical");
	HighlightableTextBlock.prototype.insertLine = HTB_insertLine;
	HighlightableTextBlock.prototype.deleteLine = HTB_deleteLine;
	HighlightableTextBlock.prototype.highlightLine = HTB_highlightLine;
	HighlightableTextBlock.prototype.removeHighlight = HTB_removeHighlight;

	htb = the_evt.target.ownerDocument.getElementById("foo");
	htb.parentNode.removeChild(htb);
	htb = the_evt.target.ownerDocument.getElementById("foo_hg");
	htb.parentNode.removeChild(htb);
}

//Insert line with respective into nth slot.  0-based indexing.  If line already exists in HTB, line is shifted to respective spot.
function HTB_insertLine(id, n){
	var to_insert = the_evt.target.ownerDocument.getElementById(id);
	if(to_insert != null && to_insert.childNodes.length == 0){ // Empty Text  Replace with Rectangle
		var new_rect = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
		var children = this.line_llc.group.childNodes;
		for(i = 0; i < children.length; i++){
			if(children.item(i).childNodes.length > 0){
				for(j = 0; j < children.item(i).childNodes.length; j++){
					if(children.item(i).childNodes.item(j).wholeText != null){
						new_rect.setAttribute("x", children.item(i).getAttribute("x"));
						new_rect.setAttribute("y", children.item(i).getAttribute("y"));
						new_rect.setAttribute("height", children.item(i).getBBox().height);
						new_rect.setAttribute("width", this.line_llc.group.getBBox().width);
						to_insert.parentNode.removeChild(to_insert);
						new_rect.setAttribute("id", to_insert.getAttribute("id"));
						new_rect.setAttribute("fill", "white");
						new_rect.setAttribute("fill-opacity", 0);
						the_evt.target.ownerDocument.documentElement.appendChild(new_rect);
						break;
					}
				}
				if(new_rect.getAttribute("id") != null){
					break;
				}
			}
		}
	}
	this.line_llc.insertComponent(id, n);
}

//Deletes nth line, using 0-based indexing
function HTB_deleteLine(n){
	this.line_llc.deleteComponent(n);
	this.removeHighlight(this.line_llc.group.childNodes.length);
}



//highlight nth line, using 0-based indexing
function HTB_highlightLine(n){
	if(n < this.line_llc.group.childNodes.length && n >= 0){
		if(the_evt.target.ownerDocument.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + n) == null){
			var line = this.line_llc.group.childNodes.item(n);
			var htb_bbox = this.line_llc.group.getBBox();
			var line_bbox = line.getBBox();
			var line_translation = getTranslate(this.line_llc.group.childNodes.item(n).getAttribute("transform"));
			var m = 1;

			var background = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
			
			var dx = line.getAttribute("dx");
			var dy = line.getAttribute("dy");
			if(dx == null){
				dx = 0;
			}else{
				dx = parseFloat(dx);
			}
			if(dy == null){
				dy = 0;
			}else{
				dy = parseFloat(dy);
			}

			background.setAttribute("x", line_bbox.x + line_translation[0] - this.line_llc.h_padding - dx);
			background.setAttribute("y", line_bbox.y + line_translation[1] - this.line_llc.v_padding - dy);
			background.setAttribute("width", htb_bbox.width + 2*this.line_llc.h_padding);
			background.setAttribute("height", line_bbox.height + 2*this.line_llc.v_padding);

			background.setAttribute("stroke", "blue");
			background.setAttribute("fill", "yellow");
			background.setAttribute("id", this.line_llc.group.getAttribute("id") + "_hl" + n);
			
			this.highlight_group.appendChild(background);
		}
	}
}

//Removes the highlight of the nth line, using 0-based indexing.
function HTB_removeHighlight(n){
	var hl = the_evt.target.ownerDocument.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + n);
	if(hl != null){
		hl.parentNode.removeChild(hl);
	}
}


//Layout for components
//Lays out components linearly either 'horizontal' or 'vertical' as specified by layout
//With hp pixels of horizontal padding and vp pixels of vertical padding
function LinearLayoutComponent(hp, vp, id, layout){
	this.h_padding = hp;  //Number of pixels padding the top and bottom of each line
	this.v_padding = vp;  //Number of pixels padding the left and right of each line
	this.id = id;           //ID of group that is abstracted by this HTB instance
	
	//Create new group element to place all lines of code
	this.group = the_evt.target.ownerDocument.createElementNS(svgNS,"g");
	this.group.setAttribute("id", id);
	the_evt.target.ownerDocument.documentElement.appendChild(this.group);
	this.layout = layout;  //'horizontal' or 'vertical'
}

//Initializes prototype to call methods of the form object.function
function LLC_prototypeInit(){
	var llc = new LinearLayoutComponent(0,0,"foo","horizontal");
	LinearLayoutComponent.prototype.insertComponent = LLC_insertComponent;
	LinearLayoutComponent.prototype.deleteComponent = LLC_deleteComponent;
	LinearLayoutComponent.prototype.resnapComponent = LLC_resnapComponent;
	llc.group.parentNode.removeChild(llc.group);
}



//Insert element of specified id into nth slot, using 0-based indexing.
//If element is already in LLC, element is moved to nth slot
function LLC_insertComponent(id, n){
	var new_c = the_evt.target.ownerDocument.getElementById(id);
	var padding = 0;
	if(this.layout == "horizontal"){
		padding = this.h_padding;
	}else{
		padding = this.v_padding;
	}
	var bbox = null;
	var translation = null;
	var shift = 0;
	
	if(new_c != null){   //Component exists
		if((new_c.parentNode != this.group) && (n <= this.group.childNodes.length) && (n >=0)){ //Component is not in group.  Insert and shift if necessary
		
			if(n == 0){
				setTranslate(new_c, 0, 0);
			}else{
				bbox = this.group.childNodes.item(n-1).getBBox();
				translation = getTranslate(this.group.childNodes.item(n-1).getAttribute("transform"));
				
				if(this.layout == "horizontal"){
					shift = translation[0] + bbox.width + 2*padding;
					setTranslate(new_c, shift, 0);

				}else{		
					shift = translation[1] + bbox.height + 2*padding;
					setTranslate(new_c, 0, shift);
				}
			}
			
			if(n == this.group.childNodes.length){
				this.group.appendChild(new_c);
			}else{	
				var children = this.group.childNodes;
				this.group.insertBefore(new_c, children.item(n));
				for(i = n+1; i < children.length; i++){
					bbox = children.item(i-1).getBBox();
					translation = getTranslate(children.item(i-1).getAttribute("transform"));
					if(this.layout == "horizontal"){
						shift = translation[0] + bbox.width + 2*padding;
						setTranslate(children.item(i), shift, 0);
					}else{		
						shift = translation[1] + bbox.height + 2*padding;
						setTranslate(children.item(i), 0, shift);
					}
					
				}
			}
		}else if(n <= this.group.childNodes.length && (n >= 0)){ //Component is in group.  Move it and shift necessary lines
			var children = this.group.childNodes;
			var old_index = 0;
			for(; old_index < children.length; old_index++){
				if(children.item(old_index) === new_c){
					break;
				}
			}
			if(old_index > n){
				this.group.insertBefore(new_c, children.item(n));
				
				for(i = n; i <= old_index; i++){
					if(i == 0){
						setTranslate(children.item(i), 0, 0);
					}else{
						bbox = children.item(i-1).getBBox();	
						translation = getTranslate(children.item(i-1).getAttribute("transform"));
						if(this.layout == "horizontal"){
							shift = translation[0] + bbox.width + 2*padding;
							setTranslate(children.item(i), shift, 0);
						}else{		
							shift = translation[1] + bbox.height + 2*padding;
							setTranslate(children.item(i), 0, shift);
						}
					}
				}
			}else if(old_index < n){
				if(n == children.length){
					this.group.appendChild(new_c);
				}else{	
					this.group.insertBefore(new_c, children.item(n+1));
				}
				for(i = old_index; i <= n; i++){			
					if(i == 0){
						setTranslate(children.item(i), 0, 0);

					}else{
						bbox = children.item(i-1).getBBox();
						translation = getTranslate(children.item(i-1).getAttribute("transform"));
						if(this.layout == "horizontal"){
							shift = translation[0] + bbox.width + 2*padding;
							setTranslate(children.item(i), shift, 0);
						}else{		
							shift = translation[1] + bbox.height + 2*padding;
							setTranslate(children.item(i), 0, shift);
						}
					}
				}
			}
		}
	}
}


//Refits the nth element, to fit according to specs
function LLC_resnapComponent(n){
	var children = this.group.childNodes;
	var child = children.item(n);
	child.parentNode.removeChild(child);
	
	the_evt.target.ownerDocument.documentElement.appendChild(child);
	this.insertComponent(child.getAttribute("id"), n);
}

//Deletes the nth element, using 0-based indexing, and refits components if necessary
function LLC_deleteComponent(n){
	var padding = 0;
	var children = this.group.childNodes;
	var bbox = null;
	var translation = null;
	var shift = 0;
	
	if(this.layout == "horizontal"){
		padding = this.h_padding;
	}else{
		padding = this.v_padding;
	}
	
	if(this.group.childNodes.length == 0){
		return;
	}	

	var removed_element = this.group.removeChild(this.group.childNodes.item(n));
	
	for(i = n; i < children.length; i++){

		if(i == 0){

			setTranslate(children.item(i), 0, 0);


		}else{
			bbox = children.item(i-1).getBBox();


			translation = getTranslate(children.item(i-1).getAttribute("transform"));

			if(this.layout == "horizontal"){
				shift = translation[0] + bbox.width + 2*padding;
				setTranslate(children.item(i), shift, 0);
			}else{		
				shift = translation[1] + bbox.height + 2*padding;

				setTranslate(children.item(i), 0, shift);
			}
		}
	}
}




//Button Panel
//Buttons are padded by hp and vp pixels.
//Button panel's id given by id, and layout of buttons is given by layout
function ButtonPanel(hp, vp, id, layout){
	this.llc = new LinearLayoutComponent(hp, vp, id, layout);
}

//Initializes prototype for button panel
function BP_prototypeInit(){
	var bp = new ButtonPanel(0,0,"baz","horizontal");
	ButtonPanel.prototype.createButton = BP_createButton;
	ButtonPanel.prototype.deleteButton = BP_deleteButton;
	ButtonPanel.prototype.deleteButtonById = BP_deleteButtonById;
	ButtonPanel.prototype.activateButton = BP_activateButton;
	ButtonPanel.prototype.deactivateButton = BP_deactivateButton;
	bp.llc.group.parentNode.removeChild(bp.llc.group);
}

//Creates a button of specified ID with shape and color specified by draw_path and color
//Inserts it into slot #index, and assigned an action
function BP_createButton(id, draw_path, color, index, action){  //Create button with corresponding id, text, and action into slot #index
	if(the_evt.target.ownerDocument.getElementById(id) == null){
		var button_group = the_evt.target.ownerDocument.createElementNS(svgNS, "path");
		button_group.setAttribute("id", id);
		button_group.setAttribute("d", draw_path);
		button_group.setAttribute("fill", color);
		button_group.setAttribute("cursor", "pointer");
		button_group.setAttribute("onclick", action);

		the_evt.target.ownerDocument.documentElement.appendChild(button_group);
		this.llc.insertComponent(button_group.getAttribute("id"), index);

	}else{
		this.llc.insertComponent(id, index);

	}
}

//Deletes the nth button from panel (0-based indexing)
function BP_deleteButton(n){
	this.llc.deleteComponent(n);
}

//Deletes button of given id from the panel
function BP_deleteButtonById(id){
	var children = this.llc.group.childNodes;
	
	for(i = 0; i < children.length; i++){
		if(children.item(i).getAttribute("id") == id){
			this.deleteButton(i);
			break;
		}
	}
}

//Makes button with corresponding id active, assigning it the given action
function BP_activateButton(id, action){
	var children = this.llc.group.childNodes;
	for(i = 0; i < children.length; i++){
		if(children.item(i).getAttribute("id") == id){
			children.item(i).setAttribute("onclick", action);
			children.item(i).setAttribute("cursor", "pointer");
			children.item(i).setAttribute("fill", "url(#active_button_lg)");
			break;
		}
	}
}

//Deactivates button with corresponding id
function BP_deactivateButton(id){
	var children = this.llc.group.childNodes;

	for(i = 0; i < children.length; i++){
		if(children.item(i).getAttribute("id") == id){
			children.item(i).setAttribute("onclick", "");
			children.item(i).setAttribute("cursor", "default");
			children.item(i).setAttribute("fill", "url(#inactive_button_lg)");

			break;
		}
	}
}


//Slider
//Creates a simple slider with corresponding id
//Thumb's height is specified.  'Offset' is the x-offset from the edge of the canvas (pixels)
//Range is a 2-index array, specifying the upper and lower bounds of the slider.
//labels specifies the labels given to the slider
//Title indicates the slider's title
//Actions is an array of 2-index arrays of ['attribute', 'action'] pairs
function Slider(id, slider_width, thumb_height, offset, range, labels, title, actions){	
	this.slider = null;
	this.slider_bar = null;
	this.slider_thumb = null;
	this.low_bound = range[0];
	this.up_bound = range[1];
	this.thumb_active = false;
	this.current_setting = range[0];
	this.offset = offset;
	
	this.default_thickness = 10;
	var font_size = 10;
	
	this.slider = the_evt.target.ownerDocument.createElementNS(svgNS, "g");	
	this.slider.setAttribute("id", id);
	
	this.slider_bar = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
	this.slider_bar.setAttribute("width", slider_width);
	this.slider_bar.setAttribute("height", this.default_thickness);
	this.slider_bar.setAttribute("x", this.default_thickness/2);
	this.slider_bar.setAttribute("y",(thumb_height-this.default_thickness)/2);
	this.slider_bar.setAttribute("rx", this.default_thickness/2);
	this.slider_bar.setAttribute("ry", this.default_thickness/2);
	this.slider_bar.setAttribute("stroke", "black");
	this.slider_bar.setAttribute("fill", "url(#slider_bar_lg)");
	this.slider_bar.setAttribute("stroke-width", 1);
	this.slider_bar.setAttribute("cursor", "pointer");
	this.slider_bar.setAttribute("id", id + "_slider_bar");
	this.slider.appendChild(this.slider_bar);
	
	this.slider_thumb = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
	this.slider_thumb = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
	this.slider_thumb.setAttribute("width", this.default_thickness);
	this.slider_thumb.setAttribute("height", thumb_height);
	this.slider_thumb.setAttribute("rx", this.default_thickness/2);
	this.slider_thumb.setAttribute("ry", this.default_thickness/2);
	this.slider_thumb.setAttribute("stroke", "black");
	this.slider_thumb.setAttribute("fill", "url(#slider_thumb_lg)");
	this.slider_thumb.setAttribute("stroke-width", 1);
	this.slider_thumb.setAttribute("cursor", "pointer");
	this.slider_thumb.setAttribute("id", id + "_slider_thumb");
	this.slider.appendChild(this.slider_thumb);
	
	//create labels below slider
	for(i in labels){
		var text = the_evt.target.ownerDocument.createElementNS(svgNS, "text");
		text.setAttribute("x", this.default_thickness/2 + i*(slider_width/(labels.length-1)));
		text.setAttribute("y", thumb_height+ font_size);
		text.setAttribute("text-anchor","middle");
		text.setAttribute("font-size", font_size);
		text.setAttribute("font-family","Helvetica");
		text.setAttribute("font-style","normal");
		text.appendChild(the_evt.target.ownerDocument.createTextNode(labels[i]));
		this.slider.appendChild(text);
	}
	
	//create slider title
	
	var header = the_evt.target.ownerDocument.createElementNS(svgNS, "text");
	header.setAttribute("x", (this.default_thickness + slider_width)/2);
	header.setAttribute("y", 0);
	header.setAttribute("text-anchor","middle");
	header.setAttribute("font-size", font_size);
	header.setAttribute("font-family","Helvetica");
	header.setAttribute("font-style","normal");
	header.appendChild(the_evt.target.ownerDocument.createTextNode(title));
	this.slider.appendChild(header);
		
	for(i in actions){
		this.slider.setAttribute(actions[i][0], actions[i][1]);
	}
	
	the_evt.target.ownerDocument.documentElement.appendChild(this.slider);
}

/**
*
*
* Speed Slider functions
*
*
*/
//Drags or moves thumb when slider is clicked
function SSlider_Click(evt){
	if(evt.target.getAttribute("id") == "speed_slider_slider_thumb"){  //Drag thumb
		speed_slider.thumb_active = true;
	} else if(evt.target.getAttribute("id") == "speed_slider_slider_bar"){	//Move thumb.
		Move_SSlider(evt);
	}	
}

//Stops thumb movement
function Deactivate_SSlider(evt){
	speed_slider.thumb_active=false;
}

//Moves thumb and changes associated values
function Move_SSlider(evt){
	var bbox = speed_slider.slider_bar.getBBox();
	speed_slider.slider_thumb.setAttribute("x", evt.clientX-speed_slider.offset-(speed_slider.default_thickness/2));

	speed_slider.current_setting = speed_slider.low_bound + (speed_slider.up_bound-speed_slider.low_bound)*(speed_slider.slider_thumb.getAttribute("x")/speed_slider.slider_bar.getAttribute("width"));
	timeout = speed_slider.current_setting;
}

//Drag slider and change associated values
function Drag_SSlider(evt){
	if(speed_slider.thumb_active){
		if(evt.clientX >= speed_slider.slider_bar.getBBox().x+speed_slider.offset && evt.clientX <= (speed_slider.slider_bar.getBBox().x + speed_slider.offset + speed_slider.slider_bar.getBBox().width)){
			speed_slider.slider_thumb.setAttribute("x", evt.clientX-speed_slider.offset-(speed_slider.default_thickness/2));
			speed_slider.current_setting = speed_slider.low_bound + (speed_slider.up_bound-speed_slider.low_bound)*(speed_slider.slider_thumb.getAttribute("x")/speed_slider.slider_bar.getAttribute("width"));
			timeout = speed_slider.current_setting;
		}
	}
}


/**
*
*
*
* Animation control functions
*
*
*/
//Starts animation loop.  If called more than once, resets display and begins loop
function StartAnimation(evt){
	if(evt.target.getAttribute("id") == "start_button" || evt.target.parentNode.getAttribute("id") == "start_button"){

		if(state != null){
			horiz_layout.deleteComponent(1);
			vert_layout[1] = new LinearLayoutComponent(2, 2, "vert_layout_1", "vertical");

			for(x in init_graphs){
                            var new_graph = init_graphs[x].cloneNode(true);
                            the_evt.target.ownerDocument.documentElement.appendChild(new_graph);
			
                            vert_layout[1].insertComponent(new_graph.getAttribute("id"), x);
                        }
			horiz_layout.insertComponent(vert_layout[1].group.getAttribute("id"), 1);
		}
	
		state = "running";
		action_panel.activateButton("stop_button", "StopAnimation(evt)");
		action_panel.activateButton("continue_button", "ContinueAnimation(evt)");
		action_panel.activateButton("step_button", "StepAnimation(evt)");
		action_panel.deactivateButton("start_button");

		AnimateLoop();
	}
}

//Loop of animation.  Performs actions in animation array at specified intervals
function AnimateLoop(){
	var duration = animation[step][0] * timeout;
	animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
	step = step + 1;
	the_evt.target.ownerDocument.documentElement.setAttribute("width", 2*x_offset + horiz_layout.group.getBBox().x + horiz_layout.group.getBBox().width);
	the_evt.target.ownerDocument.documentElement.setAttribute("height", 2*y_offset + horiz_layout.group.getBBox().y + horiz_layout.group.getBBox().height);
	
	if(step < animation.length) {
		timer = setTimeout(AnimateLoop, duration);
	}else{
                state = "stopped";
		action_panel.activateButton("start_button", "StartAnimation(evt)");
		action_panel.deactivateButton("continue_button");
		action_panel.deactivateButton("stop_button");
		action_panel.deactivateButton("step_button");
		step = 0;
		code.removeHighlight(current_line);
                current_line = -1;
	}

}

//Resumes execution of animation loop if paused by pressing step button
function ContinueAnimation(evt){
	if(evt.target.getAttribute("id") == "continue_button" || evt.target.parentNode.getAttribute("id") == "continue_button" ){
		if(state != "running"){
			state = "running";
			AnimateLoop();
		}
	}
}

//Stops execution of animation loop and plays next animation on press of step button
function StepAnimation(evt){
	if(evt.target.getAttribute("id") == "step_button" || evt.target.parentNode.getAttribute("id") == "step_button"){
                clearTimeout(timer);
		state = "stepping";
		animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
		step = step + 1;
		the_evt.target.ownerDocument.documentElement.setAttribute("width", 2*x_offset + horiz_layout.group.getBBox().x + horiz_layout.group.getBBox().width);
        	the_evt.target.ownerDocument.documentElement.setAttribute("height", 2*y_offset + horiz_layout.group.getBBox().y + horiz_layout.group.getBBox().height);
        	
                if(step >= animation.length){
                    state = "stopped";
                    action_panel.activateButton("start_button", "StartAnimation(evt)");
                    action_panel.deactivateButton("continue_button");
                    action_panel.deactivateButton("stop_button");
                    action_panel.deactivateButton("step_button");
                    step = 0;
                    code.removeHighlight(current_line);
                    current_line = -1;
                }
	}
}

//Stops animation and clears code highlights.  To resume animation, it must be restarted
function StopAnimation(evt){
	if(evt.target.getAttribute("id") == "stop_button" || evt.target.parentNode.getAttribute("id") == "stop_button"){
		clearTimeout(timer);
		state = "stopped";
		action_panel.activateButton("start_button", "StartAnimation(evt)");
		action_panel.deactivateButton("continue_button");
		action_panel.deactivateButton("stop_button");
		action_panel.deactivateButton("step_button");
		step = 0;
		code.removeHighlight(current_line);
                current_line = -1;
	}
}




/**
*
*
*
* Graph animation functions
*
*
*/
//Sets color of vertex with id given by v to specified color
function SetVertexColor(v, color) {
    element = the_evt.target.ownerDocument.getElementById(v);
    element.setAttribute("fill", color);
}
// Cannot map: SetAllVerticesColor(self, color, graph=None, vertices=None):
//Colors edge with id given by e
function SetEdgeColor(e, color) {
    // NOTE: Gato signature SetEdgeColor(v, w, color)
    element = the_evt.target.ownerDocument.getElementById(e);
    element.setAttribute("stroke", color);
    //added changes to color of arrowheads
    element = the_evt.target.ownerDocument.getElementById(e_arrow_id + e);
    if(element != null){
        element.setAttribute("fill", color);
    }
}

//function SetEdgesColor(edge_array, color) {
// Cannot map: SetAllEdgesColor(self, color, graph=None, leaveColors=None)
//Vertex blinks between black and current color
function BlinkVertex(v, color) {
    element = the_evt.target.ownerDocument.getElementById(v);
    blinkcolor = element.getAttribute("fill")
    blinkcount = 3;
    element.setAttribute("fill", "black");
    setTimeout(VertexBlinker, 3*timeout);
}
//Helper for BlinkVertex
function VertexBlinker() {
    if (blinkcount %% 2 == 1) {
       element.setAttribute("fill", "black"); 
    } else {
       element.setAttribute("fill", blinkcolor); 
    }
    blinkcount = blinkcount - 1;
    if (blinkcount >= 0)
       setTimeout(VertexBlinker, 3*timeout);
}


//Edge blinks between black and current color
function BlinkEdge(e, color){
    e_element = the_evt.target.ownerDocument.getElementById(e);
    e_blinkcolor = e_element.getAttribute("stroke");
    e_blinkcount = 3;
    e_element.setAttribute("stroke", "black");
    var element2 = the_evt.target.ownerDocument.getElementById(e_arrow_id + e);
    if(element2 != null){
        element2.setAttribute("fill", "black");
    }
    setTimeout(EdgeBlinker, 3*timeout);
    
}
//Helper for BlinkEdge
function EdgeBlinker(){
    var element2;
    if (e_blinkcount %% 2 == 1) {
       e_element.setAttribute("stroke", "black");
       element2 = the_evt.target.ownerDocument.getElementById(e_arrow_id + e_element.getAttribute("id"));
       if(element2 != null){
           element2.setAttribute("fill", "black");
       }
    } else {
       e_element.setAttribute("stroke", e_blinkcolor);
       element2 = the_evt.target.ownerDocument.getElementById(e_arrow_id + e_element.getAttribute("id"));
       if(element2 != null){
           element2.setAttribute("fill", e_blinkcolor);
       }
    }
    e_blinkcount = e_blinkcount - 1;
    if (e_blinkcount >= 0)
       setTimeout(EdgeBlinker, 3*timeout);
}

//Blink(self, list, color=None):
//Sets the frame width of a vertex
function SetVertexFrameWidth(v, val) {
    var element = the_evt.target.ownerDocument.getElementById(v);
    element.setAttribute("stroke-width", val);
}

//Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(v, annotation, color) //removed 'self' parameter to because 'self' parameter was assigned value of v, v of annotation, and so on.
{
    element = the_evt.target.ownerDocument.getElementById(v);
    if(element != null){
	if(the_evt.target.ownerDocument.getElementById(v_ano_id + v) !=null){
		ano = the_evt.target.ownerDocument.getElementById(v_ano_id + v);
		ano.parentNode.removeChild(ano);
	
	}
	
	var newano = the_evt.target.ownerDocument.createElementNS(svgNS,"text");
	x_pos = parseFloat(element.getAttribute("cx")) + parseFloat(element.getAttribute("r")) + 1;
	y_pos = parseFloat(element.getAttribute("cy")) + parseFloat(element.getAttribute("r")) + 1;
	newano.setAttribute("x", x_pos);
	newano.setAttribute("y", y_pos);
	newano.setAttribute("fill",color);
	newano.setAttribute("id", v_ano_id+v);
	newano.setAttribute("text-anchor","center");
	newano.setAttribute("font-size","14.0");
	newano.setAttribute("font-family","Helvetica");
	newano.setAttribute("font-style","normal");
	newano.setAttribute("font-weight","bold");
	newano.appendChild(the_evt.target.ownerDocument.createTextNode(annotation));
	element.parentNode.appendChild(newano);
    }
}

//Line with specified id is highlighted.  Becomes current line of code.  Previous highlight is removed.
function ShowActive(line_id){
	for(i = 0; i < code.line_llc.group.childNodes.length; i++){
		if(code.line_llc.group.childNodes.item(i).getAttribute("id") == line_id){
			code.removeHighlight(current_line);
			code.highlightLine(i);
			current_line = i;
			break;
		}
	}	
}

//Directed or undirected added to graph.
function AddEdge(edge_id){
	var graph_id = edge_id.split("_")[0];
	var vertices = edge_id.split("_")[1].match(/[^,\(\)\s]+/g);
	var v = the_evt.target.ownerDocument.getElementById(graph_id + "_" + vertices[0]);
	var w = the_evt.target.ownerDocument.getElementById(graph_id + "_" + vertices[1]);
	
	var vx = v.getAttribute("cx");
	var wx = w.getAttribute("cx");
	var vy = v.getAttribute("cy");
	var wy = w.getAttribute("cy");
	
	if(v != null && w != null){
		var parent_graph = the_evt.target.ownerDocument.getElementById(graph_id);
		var arrowhead = null;
		var edge = null;
		
		if(parent_graph.getAttribute("type") == "directed"){
			var reverse_edge = the_evt.target.ownerDocument.getElementById(graph_id + "_(" + vertices[1] + ", " + vertices[0] + ")");
			if(reverse_edge != null){  //reverse edge exists.  Make this edge an arc.
				//Another directed edge.  Great... Change existing edge to arc and add new arc
				//Be sure to alter polylines as well.
				
				
				var l = Math.sqrt(Math.pow((parseFloat(vx)-parseFloat(wx)),2) + Math.pow((parseFloat(vy)-parseFloat(wy)),2));
				
				if(l < 0.001)
					l = 0.001;
				
				var c = (l - default_vertex_radius)/l - 0.001;
				var tmpX = parseFloat(vx) + c * (parseFloat(wx) - parseFloat(vx));
				var tmpY = parseFloat(vy) + c * (parseFloat(wy) - parseFloat(vy));
				
				
				var orthogonal = Orthogonal((parseFloat(wx)-parseFloat(vx)),(parseFloat(wy)-parseFloat(vy)));
				
				var mX = orthogonal[0];
				var mY = orthogonal[1];
				c = 1.5*default_vertex_radius + l/25;
				mX = parseFloat(vx) + .5 * (parseFloat(wx) - parseFloat(vx)) + c * mX
				mY = parseFloat(vy) + .5 * (parseFloat(wy) - parseFloat(vy)) + c * mY
				
				
				
				arrowhead = createArrowhead(mX, mY, wx, wy, 4.0, "ea" + edge_id);
				
				
				l = Math.sqrt(Math.pow(wx-mX,2) + Math.pow(wy-mY,2));
               
				if (l < .001)
					l = .001;
				

				c = (l-2*default_vertex_radius)/l + .01;
				tmpX = mX + c*(wx - mX);
				tmpY = mY + c*(wy - mY);
				
				
				edge = the_evt.target.ownerDocument.createElementNS(svgNS,"path");
				edge.setAttribute("id", edge_id);
				edge.setAttribute("stroke", "#EEEEEE");
				edge.setAttribute("stroke-width", 4.0);
				edge.setAttribute("fill", "none");
				edge.setAttribute("d", "M " + vx +"," + vy +" Q "+ mX +"," + mY + " " + tmpX + "," + tmpY);
	    
				parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
				if(arrowhead != null)
					parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
					
					
				if(reverse_edge.getAttribute("d") == null){
					reverse_edge.parentNode.removeChild(the_evt.target.ownerDocument.getElementById("ea" + reverse_edge.getAttribute("id")));
					reverse_edge.parentNode.removeChild(reverse_edge);
					AddEdge(reverse_edge.getAttribute("id"));
				}
				the_evt.target.ownerDocument.getElementById(reverse_edge.getAttribute("id")).setAttribute("stroke", reverse_edge.getAttribute("stroke"));
				the_evt.target.ownerDocument.getElementById("ea" + reverse_edge.getAttribute("id")).setAttribute("fill", reverse_edge.getAttribute("stroke"));
			}else{  //No reverse edge.  Just make a straight line
                                edge = the_evt.target.ownerDocument.createElementNS(svgNS,"line");
                                edge.setAttribute("id", edge_id);
                                edge.setAttribute("stroke", "#EEEEEE");
                                edge.setAttribute("stroke-width", 4.0);
				edge.setAttribute("x1", vx);
				edge.setAttribute("y1", vy);

				var l = Math.sqrt(Math.pow((parseFloat(wx)-parseFloat(vx)),2) + Math.pow((parseFloat(wy)-parseFloat(vy)),2));
               
				if (l < .001)
					l = .001;

				var c = (l-2*default_vertex_radius)/l + .01;
				var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
				var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
								
				edge.setAttribute("x2", tmpX);
				edge.setAttribute("y2", tmpY);

				arrowhead = createArrowhead(vx, vy, wx, wy, 4.0, "ea" + edge_id);	
				
				parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
				if(arrowhead != null)
					parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
			}
		}else{ //Undirected edge
                        edge = the_evt.target.ownerDocument.createElementNS(svgNS,"line");
            		edge.setAttribute("id", edge_id);
                	edge.setAttribute("stroke", "#EEEEEE");
                	edge.setAttribute("stroke-width", 4.0);
			edge.setAttribute("x1", vx);
			edge.setAttribute("y1", vy);
			edge.setAttribute("x2", wx);
			edge.setAttribute("y2", wy);
			
			parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
			if(arrowhead != null)
				parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
		}
	}
}

//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id){
	var edge =  the_evt.target.ownerDocument.getElementById(edge_id);
	if(edge != null){
		edge.parentNode.removeChild(edge);
	}
	var arrowhead = the_evt.target.ownerDocument.getElementById("ea" + edge_id);
	
	if(arrowhead != null){
		arrowhead.parentNode.removeChild(arrowhead);
	}

	var graph_id = edge_id.split("_")[0];
	var vertices = edge_id.split("_")[1].match(/[^,\(\)\s]+/g);
	var reverse_edge = the_evt.target.ownerDocument.getElementById(graph_id + "_(" + vertices[1] + ", " + vertices[0] + ")");
	if(reverse_edge != null){
            DeleteEdge(reverse_edge.getAttribute("id"));
            AddEdge(reverse_edge.getAttribute("id"));
            var new_edge = the_evt.target.ownerDocument.getElementById(reverse_edge.getAttribute("id"));
            new_edge.setAttribute("stroke", reverse_edge.getAttribute("stroke"));
            new_edge.setAttribute("stroke-width", reverse_edge.getAttribute("stroke-width"));
	}
}

//Adds vertex of into specified graph and coordinates in graph.  Optional id argument may be given.
function AddVertex(graph_and_coordinates, id){
	var graph = the_evt.target.ownerDocument.getElementById(graph_and_coordinates.split("_")[0]);
	var next_vertex = 1;

	while(true){
		if(the_evt.target.ownerDocument.getElementById(graph.getAttribute("id") + "_" + next_vertex) == null){
			break;
		}
		next_vertex++;
	}
	
	var coords = graph_and_coordinates.split("(")[1].match(/[\d\.]+/g);
	
	var new_vertex = the_evt.target.ownerDocument.createElementNS(svgNS,"circle");
	new_vertex.setAttribute("cx", coords[0]);
	new_vertex.setAttribute("cy", coords[1]);
	new_vertex.setAttribute("r", default_vertex_radius);
	new_vertex.setAttribute("fill", "#000099");
	new_vertex.setAttribute("stroke", "black");
	new_vertex.setAttribute("stroke-width", 0.0);
	if(id != null){
		new_vertex.setAttribute("id", graph.getAttribute("id") + "_" + id);
	}else{
		new_vertex.setAttribute("id", graph.getAttribute("id") + "_" + next_vertex);
	}
	graph.appendChild(new_vertex);
	
	var new_label = the_evt.target.ownerDocument.createElementNS(svgNS,"text");
	new_label.setAttribute("x", coords[0]);
	new_label.setAttribute("y", parseFloat(coords[1]) + .33*parseFloat(new_vertex.getAttribute("r")));
	new_label.setAttribute("text-anchor", "middle");
	new_label.setAttribute("fill", "white");
	new_label.setAttribute("font-family", "Helvetica");
	new_label.setAttribute("font-size", 14.0);
	new_label.setAttribute("font-style", "normal");
	new_label.setAttribute("font-weight", "bold");
	new_label.setAttribute("id", "vl" + new_vertex.getAttribute("id"));
	if(id != null){
		new_label.appendChild(the_evt.target.ownerDocument.createTextNode(id));
	}else{
		new_label.appendChild(the_evt.target.ownerDocument.createTextNode(next_vertex + ""));
	}
	graph.appendChild(new_label);

        //resnap graph to fit	
	for(i = 0; i < vert_layout[1].group.childNodes.length; i++){
		vert_layout[1].resnapComponent(i);
	}
}

//function SetEdgeAnnotation(self,tail,head,annotation,color="black"):
//def UpdateVertexLabel(self, v, blink=1, color=None):

/**
*
*
*
* Main program
*
*
*/
function Initialize(evt) {
	the_evt = evt;
	HTB_prototypeInit();
	LLC_prototypeInit();
	BP_prototypeInit();


        //Create code layout
	code = new HighlightableTextBlock(2, 0, "code", 14, "vertical");

	var linenum = 1;
	while(the_evt.target.ownerDocument.getElementById("l_" + linenum) != null){
		code.insertLine("l_" + linenum, linenum-1);
		linenum++;
	}
	

	//Clone initial graphs and keep references to them
	init_graphs = new Array();
	var i = 1;
	var tree = the_evt.target.ownerDocument.getElementById("g" + i);
	while(tree != null){
            init_graphs[i-1] = tree.cloneNode(true);
            i++;
            tree = the_evt.target.ownerDocument.getElementById("g" + i);
	}
	
	
	//Create buttons
	action_panel = new ButtonPanel(15, 2, "actions", "horizontal");
	action_panel.createButton("start_button", "M0,0 0,40 10,40 10,0 Z M20,0 20,40 50,20 Z", "url(#active_button_lg)", 0, "StartAnimation(evt)");
	action_panel.createButton("step_button", "M0,0 0,40 30,20 Z M30,0 30,40 40,40 40,0 Z" , "url(#active_button_lg)", 1, "StepAnimation(evt)");
	action_panel.createButton("continue_button", "M0,0 0,40 30,20 Z", "url(#active_button_lg)", 2, "ContinueAnimation(evt)");
	action_panel.createButton("stop_button", "M0,0 0,40 40,40 40,0 Z", "url(#active_button_lg)", 3, "StopAnimation(evt)");
	action_panel.deactivateButton("continue_button");
	action_panel.deactivateButton("stop_button");
	action_panel.deactivateButton("step_button");
	

	//Create speed slider 
	speed_slider = new Slider("speed_slider", 400, 50, x_offset, [timeout,1], ["Slow", "Fast"], "Speed", [["onmousedown", "SSlider_Click(evt)"],["onmouseup", "Deactivate_SSlider(evt)"], ["onmousemove","Drag_SSlider(evt)"]]);
	

	//Lay out code, speed slider, and graphs
	horiz_layout = new LinearLayoutComponent(2, 2, "horizontal_layout", "horizontal");	
	vert_layout = new Array(new LinearLayoutComponent(2, 5, "vert_layout_0", "vertical"), new LinearLayoutComponent(2, 2, "vert_layout_1", "vertical"));

	vert_layout[0].insertComponent(code.line_llc.group.getAttribute("id"), 0);
	vert_layout[0].insertComponent(action_panel.llc.group.getAttribute("id"), 1);
	vert_layout[0].insertComponent(speed_slider.slider.getAttribute("id"), 2);


        for(x in init_graphs){
            vert_layout[1].insertComponent(init_graphs[x].getAttribute("id"), x);
	}
	horiz_layout.insertComponent(vert_layout[0].group.getAttribute("id"), 0);
	horiz_layout.insertComponent(vert_layout[1].group.getAttribute("id"), 1);
	
	//offset to make everything visible
	horiz_layout.group.setAttribute("transform", "translate(" + x_offset + " " + y_offset + ")");
	code.highlight_group.setAttribute("transform","translate(" + x_offset + " " + y_offset + ")");

	the_evt.target.ownerDocument.documentElement.setAttribute("width", x_offset + horiz_layout.group.getBBox().x + horiz_layout.group.getBBox().width);
	the_evt.target.ownerDocument.documentElement.setAttribute("height", y_offset + horiz_layout.group.getBBox().y + horiz_layout.group.getBBox().height);
}


var animation = Array(%(animation)s
);

]]></script>
"""
head = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm">
<defs> 
    <marker id="Arrowhead" 
      viewBox="0 0 10 10" refX="0" refY="5" 
      markerUnits="strokeWidth" 
      markerWidth="4" markerHeight="3" 
      orient="auto"> 
      <path d="M 0 0 L 10 5 L 0 10 z" /> 
    </marker>    
    
    <linearGradient id="active_button_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="blue">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    
    <linearGradient id="inactive_button_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="blue" stop-opacity="0">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    
    
    
    <linearGradient id="slider_bar_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="skyblue" >
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    <linearGradient id="slider_thumb_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="#C0C0C0">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
</defs>
"""

footer = """
</svg>
"""

#Global constants for tokenEater
line_count = 1
keywordsList = [
          "del", "from", "lambda", "return",
          "and", "elif", "global", "not", "try",
          "break", "else", "if", "or", "while",
          "class", "except", "import", "pass",
          "continue", "finally", "in", "print",
          "def", "for", "is", "raise"]

operatorsList = ["+", "-", "*", "/", "^", "%", "=",
                 "+=", "-=", "*=", "/=", "^=", "%=",
                 ">", "<", "==", "!=", ">=", "<=",
                 "**", "<>", "|", "&", "<<", ">>",
                 "//", "~", "**="]

specialList = ["(", ",", ".", ")", "[", "]"]

begun_line = False
num_spaces = 0.0
SVG_Animation = None
prev = ""
indent_stack = [0]

def tokenEater(type, token, (srow, scol), (erow, ecol), line):
    global line_count
    global prev
    global begun_line
    global num_spaces
    global SVG_Animation
    global indent_stack

    print("'%s'" % token + " of " + str((srow,scol)) + " , " + str((erow, ecol)) + " - type: " + str(type) + "line: " + str(line) + "len=" + str(len(token)))
    if (type == 0): #EOF.  Reset globals
        line_count = 1
        num_spaces = 0.0
        indent_stack = [0]
        begun_line = False
        SVG_Animation = None
        prev = ""
    elif (type == 1): #Word.  Potential keyword.  Must check keywordsList
        if begun_line == False:
            begun_line = True
            SVG_Animation.write('<text id="%s" x="10" y="10" dx = "%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if token in keywordsList:
            if (prev in specialList and (prev != "]" and prev != ")")):
                SVG_Animation.write('<tspan font-weight="bold">%s</tspan>' % token)
            else:
                SVG_Animation.write('<tspan font-weight="bold"> %s</tspan>' % token)
        else:
            if (prev in specialList and (prev != "]" and prev != ")")):
                SVG_Animation.write(token)
            else:
                SVG_Animation.write(" " + token)
    elif (type == 4): #Newline on nonempty line
        SVG_Animation.write('</text>\n')
        begun_line = False
        line_count += 1
    elif (type == 5):  #Arbitrary number of tabs at beginning of line  tabs are 4 spaces long
        num_spaces = 0.0
        for x in token:
            if ord(x) == 9:
                num_spaces += 7.7
            elif ord(x) == 32:
                num_spaces += 1.0

        num_spaces = int(floor(num_spaces))
        indent_stack.append(num_spaces)
        #num_spaces = int(floor(len(token))/4)
    elif (type == 6):  #One backpedal
        indent_stack.pop()
    elif (type == 51): #Operators and punctuation
        if begun_line == False:
            begun_line = True
            SVG_Animation.write('<text id="%s" x="10" y="10" dx = "%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if token in operatorsList:
            if token == "<":
                token = "lessthan"
            elif token == "<<":
                token = "leftshift"
            elif token == "<=":
                token = "lessthanoreq"
            elif token == "<>":
                token = "!="
            SVG_Animation.write(' %s' % token)
        else:
            if prev in operatorsList:
                SVG_Animation.write(' %s' % token)
            else:
                SVG_Animation.write('%s' % token)
    elif (type == 53): #Comment
        x = 1+1  #For now, do nothing
    elif (type == 54): #Empty line with newline
        SVG_Animation.write('<text id="%s" x="10" y="10" dx = "%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal"></text>\n' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))
        line_begun = False
        line_count += 1
    else:
        if begun_line == False:
            begun_line = True
            SVG_Animation.write('<text id="%s" x="10" y="10" dx = "%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if (prev in specialList and (prev != "]" and prev != ")")):
            SVG_Animation.write(token)
        else:
            SVG_Animation.write(" " + token)
                
    
    prev = token
    


def cmd_as_javascript(cmd, idPrefix=''):
    """ Return a list of methodname, target and args """
    def quote(s, prefix=''):
        return "\"%s\"" % (prefix+str(s))
    
    if len(cmd.target) == 1:
        target = quote(cmd.target[0], idPrefix)
    else:
        target = quote(cmd.target, idPrefix)
        
    result = [cmd.time, cmd.method.__name__, target]
    for arg in cmd.args:
        result.append(quote(arg))
    return result
    

def collectAnimations(histories, prefixes):
    """ Given a list of animation histories (aka list of AnimationCommands)
        combine them, giving all targets of animation commands their history-
        specific prefix, sort them and return a list of JavaScripts arrays.
    """
    mergedCmds = [cmd_as_javascript(cmd, prefixes[0]) for cmd in histories[0]]
    for i, h in enumerate(histories[1:]):
        mergedCmds += [cmd_as_javascript(cmd, prefixes[i+1]) for cmd in h]
    mergedCmds = sorted(mergedCmds, key=lambda cmd: cmd[0])

    # Replace absolute times by duration
    currentTime = mergedCmds[0][0]
    for i, cmd in enumerate(mergedCmds):
        duration = max(1,int(round((cmd[0] - currentTime) * 1000, 0)))
        currentTime = cmd[0]
        mergedCmds[i][0] = str(duration)
    return ["Array(" + ", ".join(cmd) + ")" for cmd in mergedCmds]

def boundingBox(graphDisplay):
    bb = graphDisplay.canvas.bbox("all") # Bounding box of all elements on canvas
    # Give 10 pixels room to breathe
    x = max(bb[0] - 10,0)
    y = max(bb[1] - 10,0)
    width=bb[2] - bb[0] + 10
    height=bb[3] - bb[1] + 10
    return {'x':x,'y':y,'width':width,'height':height}


def WriteGraphAsSVG(graphDisplay, file, idPrefix=''):
    # Write Bubbles from weighted matching
    # XXX We make use of the fact that they have a bubble tag
    # XXX What to use as the bubble ID?
##    bubbles = graphDisplay.canvas.find_withtag("bubbles")
##    for b in bubbles:
##        col = graphDisplay.canvas.itemcget(b,"fill")
##        # Find center and convert to Embedding coordinates
##        coords = graphDisplay.canvas.coords(b)
##        x = 0.5 * (coords[2] - coords[0]) + coords[0]
##        y = 0.5 * (coords[3] - coords[1]) + coords[1]
##        r = 0.5 * (coords[2] - coords[0])
##        xe,ye = graphDisplay.CanvasToEmbedding(x,y)
##        re,dummy = graphDisplay.CanvasToEmbedding(r,0)
##        file.write('<circle cx="%s" cy="%s" r="%s" fill="%s" '\
##                   ' stroke-width="0" />\n' % (xe,ye,re,col))           


##    # Write Highlighted paths
##    # XXX What to use as the bubble ID?
##    for pathID, draw_path in graphDisplay.highlightedPath.items():
##        # XXX Need to check visibility? See HidePath
##        col = graphDisplay.canvas.itemcget(draw_path,"fill")
##        width = graphDisplay.canvas.itemcget(draw_path,"width")
##        points = ["%s,%s" % graphDisplay.VertexPositionAndRadius(v)[0:2] for v in pathID]
##        file.write('<polyline points="%s" stroke="%s" stroke-width="%s" '\
##                   'fill="None" />\n' % (" ".join(points),col,width))



    # Write Edges
    for v,w in graphDisplay.G.Edges():
        vx,vy,r = graphDisplay.VertexPositionAndRadius(v)
        wx,wy,r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)

        if graphDisplay.G.directed == 0:
            file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                       ' stroke-width="%s"/>\n' % (idPrefix+str((v,w)),vx,vy,wx,wy,col,width))
        else:
            # AAARGH. SVG has a retarded way of dealing with arrowheads 
            # It is a known bug in SVG 1.1 that the color of the arrowhead is not inherited
            # Will be fixed in SVG 1.2
            # See bug 995815 in inkscape bug tracker on SF
            # However, even 1.2 will keep the totally braindead way of sticking on the arrowhead
            # to the end! of the arrow. WTF
            # Workarounds:
            # Implement arrows as closed polylines including the arrow (7 vs. 2 coordinates)
            # Q> How to do curved edges with arrows? Loops? 
            x1,y1,x2,y2 = graphDisplay.directedDrawEdgePoints(graphDisplay.VertexPosition(v),
                                                              graphDisplay.VertexPosition(w),
                                                              0)
            x1e,y1e = graphDisplay.CanvasToEmbedding(x1,y1)
            x2e,y2e = graphDisplay.CanvasToEmbedding(x2,y2)


            if graphDisplay.G.QEdge(w,v): # Directed edges both ways
                file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                           ' stroke-width="%s"/>\n' % (idPrefix+str((v,w)),x1e,y1e,x2e,y2e,col,width))
            else: # Just one directed edge
                # XXX How to color arrowhead?
                l = sqrt((float(wx)-float(vx))**2 + (float(wy)-float(vy))**2)
                if (l < .001):
                    l = .001

                c = (l-2*graphDisplay.zVertexRadius)/l + .01
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))


                #dx = 0 #offset of wx to make room for arrow
                #dy = 0 #offset of wy
                cr = 0
                #Took out marker-end="url(#Arrowhead)" and added polyline
                #Shrink line to make room for arrow
                for z in graphDisplay.G.Vertices():
                    cx,cy,cr = graphDisplay.VertexPositionAndRadius(z)
                    if(cx == wx and cy == wy):
                        angle = atan2(int(float(wy))-int(float(vy)), int(float(wx))-int(float(vx)))
                        file.write('<line id="%s" x1="%s" y1="%s" x2="%f" y2="%f" stroke="%s"'\
                               ' stroke-width="%s" />\n' % (idPrefix+str((v,w)),vx,vy,tmpX,tmpY,
                                                            col,width))
                        break

                #Temporary settings for size of polyline arrowhead
                a_width = (1 + 1.5/(1*pow(log10(float(width)), 6)))
                if(a_width > 5.0):
                    a_width = 5.0
                a_width *= float(width) 
                p1 = (0,0)
                p2 = (0, a_width)
                p3 = (cr, a_width/2)
                angle = degrees(atan2(int(wy)-int(vy), int(wx)-int(vx)))
                c = (l-2*graphDisplay.zVertexRadius)/l
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                file.write('<polyline id="ea%s" points="%f %f %f %f %s %f" fill="%s" transform="translate(%f,%f)'\
                           ' rotate(%f %f %f)" />\n' % (idPrefix+str((v,w)), p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                                        col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))


        # Write Edge Annotations
        if graphDisplay.edgeAnnotation.QDefined((v,w)):
            da = graphDisplay.edgeAnnotation[(v,w)]
            x,y = graphDisplay.canvas.coords(graphDisplay.edgeAnnotation[(v,w)])
            xe,ye = graphDisplay.CanvasToEmbedding(x,y)
            text = graphDisplay.canvas.itemcget(graphDisplay.edgeAnnotation[(v,w)],"text") 
            size = r * 0.9
            offset = 0.33 * size
            col = 'black'
            if text != "":
                file.write('<text id="ea%s" x="%s" y="%s" text-anchor="center" '\
                           'fill="%s" font-family="Helvetica" '\
                           'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(xe),
                                                                               ye+offset,col,size,text))


    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)

        # Write Vertex
        col = graphDisplay.GetVertexColor(v)
        fw = graphDisplay.GetVertexFrameWidth(v)
        fwe,dummy = graphDisplay.CanvasToEmbedding(fw,0)
        stroke = graphDisplay.GetVertexFrameColor(v)

        #print x,y,r,col,fwe,stroke
        file.write('<circle id="%s" cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"'\
                   ' stroke-width="%s" />\n' % (idPrefix+str(v),x,y,r,col,stroke,fwe))

        # Write Vertex Label
        col = graphDisplay.canvas.itemcget(graphDisplay.drawLabel[v], "fill")
        size = r*1.0
        offset = 0.33 * size

        file.write('<text id="vl%s" x="%s" y="%s" text-anchor="middle" fill="%s" font-family="Helvetica" '\
                   'font-size="%s" font-style="normal" font-weight="bold" >%s</text>\n' % (idPrefix+str(v),x,
                                                                                           y+offset,col,size,
                                                                                           graphDisplay.G.GetLabeling(v)))

        # Write vertex annotation
        size = r*0.9
        text = graphDisplay.GetVertexAnnotation(v)
        col = 'black'
        if text != "":
            file.write('<text id="va%s" x="%s" y="%s" text-anchor="left" fill="%s" font-family="Helvetica" '\
                       'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(v),x+r+1,y+r+1,col,size,text))
    
        



def ExportSVG(fileName, algowin, algorithm, graphDisplay,
              secondaryGraphDisplay=None,
              secondaryGraphDisplayAnimationHistory=None,
              showAnimation=False):
    """ Export either the current graphs or the complete animation
        (showAnimation=True) to the file fileName
    """
    #print algowin.codeLineHistory
    global SVG_Animation
    if showAnimation:
        if secondaryGraphDisplayAnimationHistory:
            animation = collectAnimations([algorithm.animation_history.history,
                                           secondaryGraphDisplayAnimationHistory.history,
                                           algowin.codeLineHistory],
                                          ['g1_','g2_','l_'])
        else:
            animation = collectAnimations([algorithm.animation_history.history,
                                           algowin.codeLineHistory],
                                          ['g1_','l_'])
            

        # Reload the graph and execute prolog so we can save the initial state
        # to SVG
        algorithm.Start(prologOnly=True)
        
        file = open(fileName,'w')
        SVG_Animation = file
        # We need to change the coordinates and sizes of the SVG
        # to accomodate two graphs. How do we deal with various
        # browser window sizes???
        vars = {'x':0,'y':0,'width':1024,'height':768}

        # Merge animation commands from the graph windows and the algo window
        vars['animation'] = ",\n".join(animation)
       # print "vars", vars
       # print "animationhead", animationhead
        file.write(animationhead % vars)

        # Write out first graph as group and translate it
        bbg1 = boundingBox(graphDisplay)
        graph_type = ""
        if(graphDisplay.G.directed == 0):
                graph_type = "undirected"
        else:
                graph_type = "directed"
        file.write('<g id="g1" transform="translate(%d,%d)" type="%s">\n' % (200,0, graph_type))
        WriteGraphAsSVG(graphDisplay, file, idPrefix='g1_')    
        file.write('</g>\n')

        if secondaryGraphDisplay:
            # Write out second graph as group and translate it
            bbg2 = boundingBox(secondaryGraphDisplay)
            if(secondaryGraphDisplay.G.directed == 0):
                graph_type = "undirected"
            else:
                graph_type = "directed"
            file.write('<g id="g2" transform="translate(%d,%d)" type="%s">\n' % (200,bbg1['height'], graph_type))
            WriteGraphAsSVG(secondaryGraphDisplay, file, idPrefix='g2_')    
            file.write('</g>\n')

        algowin.CommitStop()
        # Write algorithm to SVG    
        source = algorithm.GetSource()
        #Call tokenEater
        tokenize.tokenize(StringIO.StringIO(source).readline, 
                              tokenEater)
        file.write(footer)
        file.close()
    else:
        pass