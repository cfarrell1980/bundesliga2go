function XHRRequest(url, params) {
  var xhr = new XMLHttpRequest();
  params == '#'? data = ' ' : data = params
  
  if(xhr) {    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(data);
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
	if (xhr.status == 200) {
	  saveData(JSON.parse(xhr.responseText));
	} else {
	  return "Invocation Errors Occured";
	}
      } else {
	return xhr.readyState;
      }
    }
  }
}