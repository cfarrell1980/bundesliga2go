/* *** NOTICE *** */
// GET TEAMS FROM JSON
// type: 'ajax',
// url: 'app/models/data_from_instagram_api.json'

/* *** LOCAL STORAGE *** */
// Ext.regStore('TeamsStore', {
//     model: 'TeamModel',
//     proxy: {
//         type: 'localstorage',
//         id: 'team-app-store'
//     }
// });


//##############################

// Ext.regStore('TeamsStore', {
//        id: 'store_tp',
//        model: 'TeamModel',
//        autoLoad: true,
//        proxy: {
//           type: 'ajax',
//            url: 'http://foxhall.de:8081/jsonc',
//            reader: {
//                type: 'json',
//                root: 'data'
//            }
//        }
//    });
// 
// TeamsApp.stores.teamsStore = Ext.StoreMgr.get('TeamsStore');


//#############################



// Ext.regModel("User", {
// fields: [ 
// {name: "firstname", type: "string"},
// {name: "lastname", type: "string"},
// {name: "language", type: "string"},
// {name: "id", type: "int"},
// ],
// 
// });
// 
// The local store: 
// 
var localUser = new Ext.data.Store({
	model: 'TeamModel',
	proxy: {
		type: 'localstorage',
		id : 'teams_storage',
		proxy: {
			idProperty: 'id'
		}
	}
});

// 
// And getting the json data and syncing with the local store:
// 
Ext.Ajax.request({
 	url: 'http://foxhall.de:8081/jsonc',
	success: function(response, opts) {
		var dataInfo = Ext.decode(response.responseText);
		console.log(response.responseText)
	
		var userData = dataInfo.data;
		var userSession = localUser.getAt(0);
		
		if (!userSession) {
			localUser.add(userData)
		} else {
			userSession.set(userData)
		}
		localUser.sync();
	}
});

TeamsApp.stores.teamsStore = localUser.load();