importScripts('/static/javascripts/functions.js');

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
// 	  saveData(JSON.parse(xhr.responseText));
// 	  postMessage("finished");
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
  switch (data.get) {
    case 'teams':
      var url = 'http://paddy.suse.de:8080/getTeams'
      var url = '/patch_updates/show_summary?background=true';
      XHRrequest(url, data.params);
      break;
    case 'data':
      var url = 'http://paddy.suse.de:8080/getData'
      XHRrequest(url, data.params);
      break;
    case 'updates':
      var url = 'http://paddy.suse.de:8080/getUpdatesByTstamp'
      XHRrequest(url, data.params);
      break;
    default:
      self.postMessage('Unknown command: ' + data.msg);
  };
}, false);
