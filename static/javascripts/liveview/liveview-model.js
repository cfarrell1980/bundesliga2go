var URL = "http://paddy.suse.de:8080/active?tester=2011-08-06-16-00"

var match = new function() {
  this.find = function(id) {
    var match, matches;
    
    if(id == "all") {
      console.log("**** MODEL FIND ALL ****");
      //return sessionStorage.getItem('matches');
      return JSON.parse(sessionStorage.getItem('matches'));
      
    } else {
//      console.log("**** MODEL: FIND BY ID " + id +" ****");

      sessionStorage.getItem('match' + id) == null? match = "undefined" : match = sessionStorage.getItem('match' + id);
//      return JSON.parse(match);
      return match;
    }
  };
    
  this.save = function(object) {
    console.log("**** MODEL: SAVE ****");
    
    if(typeof(object) == "object") {
      console.log("MODEL: SAVE MATCHES IN SESSION STORAGE " + typeof(object));
      sessionStorage.setItem('matches', JSON.stringify(object));
      return true;
      
    } else {
      console.error("Unknown type ");
      console.log(typeof(object))
    }
    
  };
}


