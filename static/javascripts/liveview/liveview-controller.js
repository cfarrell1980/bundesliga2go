
  
function index() {
  console.log("**** CONTROLLER: INDEX ****");
  
  matches = match.find('all');
  if( matches == "undefined" || matches == null) {
//    XHRRequest(URL, 'index', false);
    CORS(URL);
  } else {
    renderIndex(matches, true);
  }
  
}

function save(matches) {
  console.log("**** CONTROLLER: SAVE ****");
  
  if(match.save(matches)) {
    console.info("MATCHES SUCCESSFULLY SAVED!");
  } else {
    console.error("ERROR OCUURED!");
  }
}



