TeamsApp.views.MainView = Ext.extend(Ext.Panel, {

    fullscreen: true,
    layout: 'card',
    cardSwitchAnimation: 'slide',

    initComponent: function () {

        Ext.apply(TeamsApp.views, {
            teamsListView: new TeamsApp.views.TeamsListView({ teamsStore: TeamsApp.stores.teamsStore }),
            teamEditorView: new TeamsApp.views.TeamEditorView()
        });

        this.items = [
            TeamsApp.views.teamsListView,
//            TeamsApp.views.teamsListView,
            TeamsApp.views.teamEditorView
        ]

        TeamsApp.views.MainView.superclass.initComponent.call(this);

        this.on('render', function () {
            console.log("Load TeamStore")
            TeamsApp.stores.teamsStore.load();
        });
    }
});

