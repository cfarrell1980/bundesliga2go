TeamsApp.views.TeamEditorView = Ext.extend(Ext.form.FormPanel, {

    initComponent: function () {

        this.backButton = new Ext.Button({
            text: 'Home',
            ui: 'back',
            handler: this.backButtonTap,
            scope: this
        });

        this.saveButton = new Ext.Button({
            text: 'Save',
            ui: 'action',
            handler: this.saveButtonTap,
            scope: this
        });

        this.trashButton = new Ext.Button({
            iconCls: 'trash',
            iconMask: true,
            handler: this.trashButtonTap,
            scope: this
        });

        this.topToolbar = new Ext.Toolbar({
            title: 'Edit Team',
            items: [
                this.backButton,
                { xtype: 'spacer' },
                this.saveButton
            ]
        });

        this.bottomToolbar = new Ext.Toolbar({
            dock: 'bottom',
            items: [
                { xtype: 'spacer' },
                this.trashButton
            ]
        });

        this.dockedItems = [this.topToolbar, this.bottomToolbar];

        TeamsApp.views.TeamEditorView.superclass.initComponent.call(this);
    },

    backButtonTap: function () {
        Ext.dispatch({
            controller: TeamsApp.controllers.teamsController,
            action: 'canceledit'
        });
    },

    saveButtonTap: function () {
        Ext.dispatch({
            controller: TeamsApp.controllers.teamsController,
            action: 'save'
        });
    },

    trashButtonTap: function () {
        Ext.dispatch({
            controller: TeamsApp.controllers.teamsController,
            action: 'delete'
        });
    },

    items: [{
        xtype: 'textfield',
        name: 'teamID',
        label: 'ID',
        required: false
    }, 
    
    {
        xtype: 'textfield',
        name: 'teamName',
        label: 'Name',
        required: false
    },
    
    {
        xtype: 'textfield',
        name: 'teamIconUrl',
        label: 'URL'
    }]
});
