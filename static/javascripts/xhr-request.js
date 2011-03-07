function XHRRequest(type, url, params) {
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
          switch(type) {
            case 'index':
              console.info('Type is: ' + type + ' before save!');
              saveIndex(xhr.responseText, data);
              break;
            case 'teams':
//               console.info('Type is: ' + type + ' before save!');
              index(xhr.responseText, params);
              break;
            default:
              console.error('Unknown type: ' + type);
          }
        } else {
          return "Invocation Errors Occured";
        }
      } else {
        return xhr.readyState;
      }
    }
  }
}