frappe.listview_settings['Sri Type Doc'] = {
    breadcrumb: 'Sri Type Doc',
    title: 'Titulo Custom',
    /*
    filters: [
        {
            fieldname: 'id',
            fieldtype:'Select',
            options: 'Company 1\nCompany 2',
            label: 'Company',
            //on_change: handle_company_change()
        }
    ],
    */
    //get_tree_nodes: 'path.to.whitelisted_method.get_children',
    //add_tree_node: 'path.to.whitelisted_method.handle_add_account',
    // fields for a new node
    fields: [
        {
            fieldtype: 'Data', fieldname: 'account_name',
            label: 'New Account Name', reqd: true
        },
        {
            fieldtype: 'Link', fieldname: 'account_currency',
            label: 'Currency', options: 'Currency'
        },
        {
            fieldtype: 'Check', fieldname: 'is_group', label: 'Is Group'
        }
    ],
    // ignore fields even if mandatory
    //ignore_fields: ['parent_account'],
    // to add custom buttons under 3-dot menu group
    menu_items: [
        {
            label: 'New Company',
            action: function() { frappe.new_doc('Sri Type Doc', true) },
            //condition: 'frappe.boot.user.can_create.indexOf(''Company'') !== -1'
        }
    ],
    onload: function(treeview) {
        // triggered when tree view is instanciated
        //frappe.throw('Iniciada la cosa');
        console.log("onload from list");
    },
    post_render: function(treeview) {
        // triggered when tree is instanciated
        //frappe.throw('Iniciada la cosa');
        console.log("post_render from list");
    },
    onrender: function(node) {
        // triggered when a node is instanciated
    },
    on_get_node: function(nodes) {
        // triggered when `get_tree_nodes` returns nodes
    },
    // enable custom buttons beside each node
    extend_toolbar: true,
    // custom buttons to be displayed beside each node
    toolbar: [
        {
            label: 'Add Child',
            condition: function(node) {},
            click: function() {},
            btnClass: 'hidden-xs'
        }
    ]
}