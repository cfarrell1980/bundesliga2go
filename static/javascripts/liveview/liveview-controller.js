// INITIAL SYNC
function index() {
  console.log("**** CONTROLLER: INDEX ****");
  
  if(navigator.onLine) {
    matches = match.find('all');
    if( matches == "undefined" || matches == null) {
  //    XHRRequest(URL, 'index', false);
      CORS(URL);
    } else {
      renderIndex(matches, true);
    }
  
  } else {
    jQuery('#matches').html("SORRY YOU ARE OFFLINE !!!");
  }
  
}

// SAVE VALUES IN SESSION STORAGE AFTER INDEX IS RENDERED
function save(matches) {
  console.log("**** CONTROLLER: SAVE ****");
  
  if(match.save(matches)) {
    console.info("MATCHES SUCCESSFULLY SAVED!");
  } else {
    console.error("ERROR OCUURED!");
  }
}

// GET LIVE UPDATE FROM SERVER
function update() {
  console.log("get updates");
  CORS(URL);
}



