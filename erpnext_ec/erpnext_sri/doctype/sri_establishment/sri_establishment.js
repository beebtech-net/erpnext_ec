frappe.ui.form.on('Sri Establishment', {
    refresh: function(frm) {
        if(frm.doc.__unsaved == 1)
        {            
            let route = frappe.get_prev_route();

            if (route && route.length > 1 && route[1] === 'Company') 
            {
                let company = route[2]; 
                
                frm.set_value('company_link',  company).then(response=>
                {

                });
            }
            else
            {
                //No viene desde compañia
            }
        }
    }
});
