var url = "http://paddy.suse.de:8080/w"
var invocation = new XMLHttpRequest();
var params = "matchday=1&league=bl1&season=2010";

function callOtherDomain(){
  if(invocation) {    
    invocation.open('POST', url, true);
    invocation.setRequestHeader('Content-Type', 'application/json');
    invocation.onreadystatechange = updateUI;
    invocation.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    invocation.send(params);
  }
}

function updateUI(evtXHR) {
  if (invocation.readyState == 4) {
    if (invocation.status == 200) {
      postMessage("finished");
      postMessage(invocation.responseText);
    } else {
      postMessage("Invocation Errors Occured");
    }
  } else {
    postMessage(invocation.readyState);
  }
}

onmessage = function(event) {
  var data = event.data;
  if(data == "start") {
    callOtherDomain();    
  } else {
    postMessage("ERROR");
  }
}

function sleep(milliseconds) {
  var start = new Date().getTime();
  
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}


