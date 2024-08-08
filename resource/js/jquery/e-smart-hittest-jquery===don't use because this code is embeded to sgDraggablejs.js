/*	
 *	jQuery hitTest plugin
 *	Demo and documentation:
 *	http://e-smartdev.com/#!jsPluginList/hittestJQuery
 *	
 *	Copyright (c) 2012 Damien Corzani
 *	http://e-smartdev.com/
 *
 *	Dual licensed under the MIT and GPL licenses.
 *	http://en.wikipedia.org/wiki/MIT_License
 *	http://en.wikipedia.org/wiki/GNU_General_Public_License
 */
(function( $ ){

 /**
  * get the visible rect containing the jquery element
  * return a rectangle object => ({x,y,width,height}) properties 
  */
  
  
  
  $.fn.getRect = function() {
  	var offset = this.offset();
  	if(!offset)
  		return null;
	var formX = offset.left;
	var formY = offset.top; 
    return new Rectangle(formX, formY, this.outerWidth(), this.outerHeight());
  };
  
  /*
  $.fn.getRect = function() {
	  var cp = this.calculatePosition();
    return new Rectangle(cp.left, cp.top, this.outerWidth(), this.outerHeight());
  };
  
  $.fn.calculatePosition = function (){
	return {
		left: calculatePosition(this[0], "offsetLeft"),
		top: calculatePosition(this[0], "offsetTop")
	};
  }
  
  function calculatePosition (objElement, strOffset){
	var iOffset = 0;
	if (objElement.offsetParent){
		do{
			iOffset += objElement[strOffset];
			objElement = objElement.offsetParent;
		} while (objElement);
	}
	return iOffset;
  }
  */
  
  /**
  * test if a jquery element hittest with a given coodinate
  * @param {Object} options = {'x': Xcoordinate to test
  * 						   'y': Ycoordinate to test
  * 						   'transparency' : manage images and canvas elements transparency
  * 						  } 
  */
  $.fn.hitTestPoint = function(options) {
  	 // Create some defaults, extending them with any options that were provided
    var settings = $.extend( {
      'x' : 0,
      'y' : 0,
      'transparency' : false,
	  'scaleX' : 1,
	  'scaleY' : 1
    }, options);
    
	var chk = false;
	this.each(function(i,e){
		if(chk) return;
		var objectRect = $(this).getRect();
		//console.log(objectRect);
		applyRectScale(objectRect, settings.scaleX, settings.scaleY);
		/*
		console.log(this.getBoundingClientRect());
		console.log(objectRect);
		console.log(settings.x, settings.y);
		*/
		var rectHitTest = objectRect.rectContainsPoint(settings.x, settings.y);
		
		var elementTarget = this;//[0];
	
		// if we don't whant to check the transparency we return just the rectangle test'
		if(!settings.transparency || (!($(elementTarget).is("img")) && !($(elementTarget).is("canvas")))){
			chk = rectHitTest?$(this):false;//rectHitTest;
			return;
		}
		// if the object rectangle don't hitTest return false
		if(!rectHitTest)
			return;
	
		var canvas = getCanvasFromElement(elementTarget);
		if (canvas == null){ // the browser is not compatible with canvas element 
			chk = $(this);
			return;
		}
		
		var ctx = canvas.getContext('2d');  
		var imageData = ctx.getImageData(settings.x - objectRect.x, settings.y - objectRect.y, 1, 1);
		
		chk = (imageData.data[3] != 0) ? $(this) : false;
		return; 
	});
	
	return chk;
  };
  
  /**
  * test if a jquery element hittest with a given coodinate
  * @param {Object} options = {'object': object to hittest width
  * 						   'transparency' : manage images and canvas elements transparency
  * 						  } 
  */
  $.fn.hitTestObject = function(options) {
  	 // Create some defaults, extending them with any options that were provided
    var settings = $.extend( {
      'selector' : null,
      'transparency' : false,
	  'scaleX' : 1,
	  'scaleY' : 1
    }, options);
    
   if(settings.selector == null) // si the object to test is not set
   	return false;
    
	var $object = $(settings.selector);
	if($object.length == 0) return false;
	
	//this.each(function(i,e){
	var i,j,k;
	var klen = this.length;
	var $this, ilen,
		objectRect,
		objectToTestRect,
		rectsInstersects,
		objectCanvas,
		objectToTestCanvas,
		ctxObject,
		ctxObjectToTest,
		intersectionRect,
		objectImageData,
		objectToTestImageData,
		objectPix,
		objectToTestPix,
		nbPixels,
		chk, $target;
		
	for(k=0; k<klen; k++){
		$this = this.eq(k);
		objectRect = $this.getRect();
		applyRectScale(objectRect, settings.scaleX, settings.scaleY);
		ilen = $object.length;
		chk = false;
		//console.log($this);
		console.log($object.length);	
		for(i=0; i<ilen; i++){
			$target = $object.eq(i);
			objectToTestRect = $target.getRect();
			applyRectScale(objectToTestRect, settings.scaleX, settings.scaleY);
			rectsInstersects = objectRect.intersects(objectToTestRect);
	
			// if we don't whant to check the transparency we return just the rectangle test'
			if(!settings.transparency || (!($this.is("img")) && !($this.is("canvas")))){
				//return rectsInstersects;
				if(rectsInstersects){
					chk = true;
					break;
				}
				else continue;
			}
			// if the object rectangle don't hitTest return false
			if(!rectsInstersects){
				continue;
				//break;//return false;
			}
			
			objectCanvas = getCanvasFromElement(this);
			objectToTestCanvas = getCanvasFromElement($object[i]);
		
			if (objectCanvas == null || objectToTestCanvas == null){ // the browser is not compatible with canvas element 
				//return true;
				chk = true;
				break;
			}
				
			ctxObject = objectCanvas.getContext('2d');  
			ctxObjectToTest = objectToTestCanvas.getContext('2d');  
			
			intersectionRect = objectRect.intersection(objectToTestRect);
			
			if(!intersectionRect){ // should not append
				//return true;
				chk = true;
				break;
			}
			
			// get the intersectionRect bitmap of the 2 objects to test  
			objectImageData = ctxObject.getImageData(intersectionRect.x - objectRect.x, intersectionRect.y - objectRect.y, intersectionRect.width>0 ?intersectionRect.width :1 , intersectionRect.height>0 ?intersectionRect.height :1 );
			objectToTestImageData = ctxObjectToTest.getImageData(intersectionRect.x - objectToTestRect.x, intersectionRect.y - objectToTestRect.y, intersectionRect.width>0 ?intersectionRect.width :1 , intersectionRect.height>0 ?intersectionRect.height :1 );
			
			objectPix = objectImageData.data;
			objectToTestPix = objectToTestImageData.data;
		
			nbPixels = objectImageData.width*objectImageData.height*4;
			// if one pixel is not transparent in both object : collision append
			for (j=0; j<nbPixels;j+=4){
				if(objectPix[j+3] != 0 && objectToTestPix[j+3] != 0){
					//return true;
					chk = true;
					break;
				}
			}
			if(chk) break;
		}
		if(chk) return $target;
	}
	
    
	return false;
  };
  
  function applyRectScale(rect, sx, sy){
	  //console.log(rect.width);
		rect.width *= sx;
		//console.log(rect.width, sx);
		rect.height *= sy;
	}
  
  
  /**
   * return a canvas of an image or a canvas element
   * if the given element is not a canvas or an image return null  
   */
  function getCanvasFromElement(jqElement){
  	
  	var isImg = $(jqElement).is("img");
  	
  	if(!isImg && !($(jqElement).is("canvas")))
  		return null;
  	
  	var canvas = isImg ? document.createElement('canvas') : jqElement;
  	
    if (!canvas.getContext) // the browser is not compatible with canvas element 
    	return null;
	
	var ctx;
	if(isImg){
	    canvas.setAttribute('width', $(jqElement).outerWidth());
	    canvas.setAttribute('height', $(jqElement).outerHeight());
	    ctx = canvas.getContext('2d');  
	    ctx.drawImage(jqElement, 0, 0, $(jqElement).outerWidth(), $(jqElement).outerHeight());
	}
	return canvas;
  }
  
})( jQuery );

/**
 * Rectangle Class
 */
function Rectangle(x, y, width, height) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    /*
     * return rectangle informations into a string
     */
    this.toString = function() {
	    return '(x=' + this.x + ', y=' + this.y + ', width=' + this.width +', height=' +this.height+')';
	  };
	/*
	 * check if a given point is contain into the rectangle
	 */  
    this.rectContainsPoint = function (pointX, pointY){
		return (pointX>=this.x && pointX<=this.x+this.width && pointY>=this.y && pointY<=this.y+this.height);	
	}
	/*
	 * check if a rectangle intersect with another ome
	 */
	this.intersects = function(rect){
		return (this.x <= rect.x + rect.width && rect.x <= this.x + this.width && this.y <=rect.y + rect.height && rect.y <= this.y + this.height);
	}
	/*
	 * return the intersection of two rectangle as a rectangle
	 * return null if there is not intersection
	 */
	this.intersection = function(rect){
		  var highestX = Math.max(this.x, rect.x);
		  var lowestX = Math.min(this.x + this.width, rect.x + rect.width);
		
		  if (highestX <= lowestX) {
		    var highestY = Math.max(this.y, rect.y);
		    var lowestY = Math.min(this.y + this.height, rect.y + rect.height);
		
		    if (highestY <= lowestY) {
		      return new Rectangle(highestX, highestY, lowestX - highestX, lowestY - highestY);
		    }
		  }
		  return null;
	}
}