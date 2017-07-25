/*
 *  To use the library, call:
 *  	 XHRequest.createRequest(config)
 *
 * 		where config is an object that can contain or override any parameters desired
 * 		config object parameters include:
 * 			success - a function that defines how a successful response should be handled
 * 			failure - a function that defines how an error response should be handled
 * 			method  - usually "GET" or "POST", defaults to get
 * 			url     - no default is supplied, you should supply one
 * 			asynch  - set to true, usually don't need to override this
 * 			params  - a query string to be sent to the server
 * 		    readyStatePickOffValue - default is 4, but change to 3 if desired.  will call success for all values at or higher than that value
 * 			successStatusCodes - array of http status codes to be considered successful.  0 &  200 are defaults.  Use [-1] for any values to be successful
 *
 * 		a typical call may look like the following:		XHRequest.createRequest({url: "myURL", success: mySuccessFunction});
 */
var XHRequest = {

	// any of these values can be overridden and tailored to your choosing
	xhrConfig : {     success: function(xhr){alert(xhr.responseText);},
	                  failure: function(xhr, xhrConfig, error){alert(error.message);},
					  method: "GET",
					  url: null,
					  asynch: true,
					  params: null,
					  readyStatePickOffValue : 4,
					  successStatusCodes : [0, 200]
	},

	createRequest : function(xhrConfig) {

		for(oneProp in this.xhrConfig) 							// copies default properties
			if(typeof xhrConfig[oneProp] == "undefined")        // from this.xhrConfig into the
				xhrConfig[oneProp] = this.xhrConfig[oneProp];   // user's xhrConfig if not provided


		buildXHR = function() {
			if(typeof XMLHttpRequest != "undefined")
				return new XMLHttpRequest();
			else if (window.ActiveXObject) {
				var xhr = new ActiveXObject("Msxml2.XMLHTTP");
				if (!xhr)
					xhr = new ActiveXObject("Microsoft.XMLHTTP");
				return xhr;
			}
		}

		processXHR = function(xhr) {
			if (xhr == null)
				return;

			xhr.onreadystatechange = function() {
				if(xhr.readyState >= xhrConfig.readyStatePickOffValue) {
					if (xhrConfig.successStatusCodes[0] === -1) {			// a -1 means all http codes are conidered successful
						xhrConfig.success(xhr, xhrConfig);
						return;
					}
					else {
						for(httpCode in xhrConfig.successStatusCodes) {
							if (xhr.status == xhrConfig.successStatusCodes[httpCode]) {
								xhrConfig.success(xhr, xhrConfig);
								return;
							}
						}
						// ???? Should call failure. Added by Nikhil 7/31/2007
						alert ("AJAX failure: " + xhr.status);
					}
				}
			};

			var queryString = "";
			if(xhrConfig.params && xhrConfig.params.constructor == Object) { // if params is an object, convert it to a queryString

				for(var prop in xhrConfig.params) {
					var oneProp = "";

					if (notFirst) oneProp += "&";

					var notFirst = true;

					oneProp += encodeURI(prop);
					oneProp += "=";
					oneProp += encodeURI(xhrConfig.params[prop]);

					queryString += oneProp;
				}
			}
			else if (xhrConfig.params && xhrConfig.params.constructor == String)
				queryString = xhrConfig.params;  // params was provided as a string


			if (xhrConfig.method && xhrConfig.method.toUpperCase() == "GET") {

				var urlWithParams = xhrConfig.url;
				if (queryString.length > 0)
					urlWithParams += ("?" + queryString);

				xhr.open(xhrConfig.method, urlWithParams, xhrConfig.asynch);
				xhr.send(null);
			}
			else {
				xhr.open(xhrConfig.method, xhrConfig.url, xhrConfig.asynch);
				xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
				xhr.send(queryString);
			}
		}

		try {
			var xhr = buildXHR();
			processXHR(xhr);
		}
		catch(error) {
			xhrConfig.failure(xhr, xhrConfig, new Error("Error: " + error.name + "\n" + "Message: " +error.message));
		}

		return xhr;
	}
}
