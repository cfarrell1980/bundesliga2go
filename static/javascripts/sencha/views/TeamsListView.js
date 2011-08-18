TeamsApp.views.TeamsListView = Ext.extend(Ext.Panel, {

    teamsStore: Ext.emptyFn,
    teamsList: Ext.emptyFn,

    layout: 'fit',

    initComponent: function () {

        this.newButton = new Ext.Button({
            text: 'New',
            ui: 'action',
            handler: this.onNewTeam,
            scope: this
        });

        this.topToolbar = new Ext.Toolbar({
            title: 'TEAMS',
            items: [
                { xtype: 'spacer' },
                this.newButton
            ]
        });

        this.dockedItems = [this.topToolbar];

        this.teamsList = new Ext.List({
            store: this.teamsStore,
            grouped: false,
            emptyText: 'No teams cached',
            // onItemDisclosure: true,
            itemTpl: "<div><img src='{teamIconUrl}' /> {teamName}</div>"
        });

        this.teamsList.on('disclose', function (record, index, evt) {
            this.onEditTeam(record, index);
        }, this),

        this.items = [this.teamsList];

        TeamsApp.views.TeamsListView.superclass.initComponent.call(this);
    },

    onNewTeam: function () {
        console.log("New clicked!")
        Ext.dispatch({
            controller: TeamsApp.controllers.teamsController,
            action: 'new'
        });
    },

//    onEditTeam: function (record, index) {
//        Ext.dispatch({
//            controller: TeamsApp.controllers.teamsController,
//            action: 'edit'//,
//            //note: record
//        });
//    },

    refreshList: function () {
        console.log("Refresh teams list");
        this.teamsList.refresh();
    }
});



