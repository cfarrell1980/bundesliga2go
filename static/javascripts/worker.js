var xhr = new XMLHttpRequest();

function XHRrequest(url, type, params){
//   params == '#'? data = ' ' : data = params
  
  if(type == 'index') {
    params = '&md=' + params;
  } else{
    params = '#';
  }
  
  if(xhr) {    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(params);
    
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
  XHRrequest(data.url, data.get, data.params);
}, false);
