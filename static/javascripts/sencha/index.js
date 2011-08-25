var App = new Ext.Application({
    name: 'TeamsApp',
    useLoadMask: true,

    launch: function () {
        Ext.dispatch({
            controller: TeamsApp.controllers.teamsController,
            action: 'index'
        });
    }
});
