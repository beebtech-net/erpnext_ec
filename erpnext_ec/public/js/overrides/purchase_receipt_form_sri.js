var doctype_customized = "Purchase Receipt";

frappe.ui.form.on(doctype_customized, {
	refresh(frm)
    {
        if (frm.doc.status == 'Draft')
        {
            //Fields for custom settings
            frm.set_query('ptoemi', function() {
                return {
                    filters: {
                        'sri_establishment_lnk': frm.doc.estab
                    }
                };
            });
        }

        if (frm.doc.status == 'Cancelled' || frm.doc.status == 'Draft')
        {
            return false;
        }
        
        SetFormSriButtons(frm, doctype_customized);      
        //console.log(frm);
        //console.log(frm.doctype_customized);
    },
    estab: function(frm)
	{
        //frm.set_value('ptoemi',  '');
        //frm.refresh_field('ptoemi');
	},
})
