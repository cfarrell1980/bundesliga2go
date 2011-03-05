var xhr = new XMLHttpRequest();

function XHRrequest(url, params){
  params == '#'? data = ' ' : data = params
  
  if(xhr) {    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(data);
    
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
	if (xhr.status == 200) {
	  postMessage(xhr.responseText);
	} else {
	  postMessage("Invocation Errors Occured");
	}
      } else {
	postMessage("wait");
      }
    }
  }
}

self.addEventListener('message', function(e) {
  var data = e.data;
  XHRrequest(data.url, data.params);
}, false);
