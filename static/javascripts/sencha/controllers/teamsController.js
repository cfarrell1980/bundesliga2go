Ext.regController('TeamsController',{

    'index': function (options) {
        console.log("Team Controller action index");

        if (!TeamsApp.views.mainView) {
            TeamsApp.views.mainView = new TeamsApp.views.MainView();
        }

        TeamsApp.views.mainView.setActiveItem(
            TeamsApp.views.teamsListView
        );
    },
    
   'new': function (options) {
      console.log("New clicked")
      var now = new Date();
      var teamId = now.getTime();
      
      var team = Ext.ModelMgr.create({ id: teamId, team1name: '', team1score: '', team1shortcut: '', team2name: '', team2score: '', team2shortcut: '' },
          'TeamModel'
      );

      TeamsApp.views.teamEditorView.load(team);
      
      TeamsApp.views.mainView.setActiveItem(
          TeamsApp.views.teamEditorView,
          { type: 'slide', direction: 'left' }
      );
    },
    
    'edit': function (options) {

    },

    'save': function (options) {

      var currentTeam = TeamsApp.views.teamEditorView.getRecord();

      TeamsApp.views.teamEditorView.updateRecord(currentTeam);

      var errors = currentTeam.validate();
      if (!errors.isValid()) {
          Ext.Msg.alert('Wait!', errors.getByField('title')[0].message, Ext.emptyFn);
          return;
      }

      if (null == TeamsApp.stores.teamsStore.findRecord('id', currentTeam.data.id)) {
          TeamsApp.stores.teamsStore.add(currentTeam);
      }

      TeamsApp.stores.teamsStore.sync();

//      TeamsApp.stores.teamsStore.sort([{ property: 'date', direction: 'DESC'}]);

      TeamsApp.views.teamsListView.refreshList();

      TeamsApp.views.mainView.setActiveItem(
          TeamsApp.views.teamsListView,
          { type: 'slide', direction: 'right' }
      );
    },

    'delete': function (options) {

    },

    'canceledit': function (options) {

    }
});

TeamsApp.controllers.teamsController = Ext.ControllerManager.get('TeamsController');

