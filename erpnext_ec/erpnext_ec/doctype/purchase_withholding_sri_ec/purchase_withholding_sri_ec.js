//Prepare in list mode
SetListSriButtons('Purchase Withholding Sri Ec');

//Prepare in form mode
frappe.ui.form.on('Purchase Withholding Sri Ec', 
{
    setup: async function(frm) 
    {
        

        //console.log(cur_frm);

        /*******************************/
        /* FILTRO PARA CAMPO */
        /*
        cur_frm.set_query("codigoRetencion", function() {
            return {
                filters: 
                {
                    "FieldNameFromLinkedDocument": true
                }
            }
        });
        */

        /*******************************/
        /* FILTRO PARA CAMPO DE GRID */
        
        //frm.fields_dict.pos_search_fields.grid.update_docfield_property('field', 'options', fields);

        //cur_frm.fields_dict['taxes'].grid.update_docfield_property("codigoRetencion", "search_fields","sricode, account_name");
        //console.log(cur_frm.fields_dict['taxes'].grid);
        //cur_frm.refresh_field('taxes');

        //cur_frm.fields_dict['taxes'].grid.get_field("codigoRetencion").search_fields = "sricode, account_name";        
        
        //cur_frm funciona por defecto [!]
        cur_frm.fields_dict['taxes'].grid.get_field("codigoRetencion").get_query = function(doc, cdt, cdn) 
        {
            return {
                filters: {
                "is_withhold_account": true
                }
            }
        }

        var def_company = frappe.defaults.get_user_default("Company");
            
        var companySri = await GetFullCompanySri(def_company);
        console.log('GetFullCompanySri');
        console.log(companySri);

        frm.set_value('nombreComercial',  companySri.nombrecomercial);
        frm.set_value('ruc',  companySri.tax_id);                
        frm.set_value('obligadoContabilidad',  companySri.obligadocontabilidad);        
        frm.set_value('dirMatriz',  companySri.dirMatriz);
        //frm.refresh_field('nombreComercial');
        //frm.refresh_field('dirMatriz');
        
    },
	refresh(frm) {
		// your code here
		console.log('Refreshhhh!!!');

        //Botones de formulario
        SetFormSriButtons(frm);
	},
    purchase_withholding_supplier: function(frm)
	{
        console.log(frm);
        //var tipoIdentificacionSujetoRetenido = frm.get_value('tipoIdentificacionSujetoRetenido');
        var purchase_withholding_supplier = frm.doc.purchase_withholding_supplier;
        console.log(purchase_withholding_supplier);

        //if(tipoIdentificacionSujetoRetenido == undefined)
        //    return;

        frm.set_value('tipoIdentificacionSujetoRetenido',  '');
        frm.set_value('razonSocialSujetoRetenido',  '');
        frm.set_value('identificacionSujetoRetenido',  '');
        frm.refresh_field('tipoIdentificacionSujetoRetenido');

		frappe.db.get_list('Supplier', { 'fields': '["*"]', 'filters': { 'name': purchase_withholding_supplier } }).then(docs => {
			console.log(docs);
			
			if(docs.length > 0)
			{
                console.log(docs[0].typeidtax);

                frm.set_value('tipoIdentificacionSujetoRetenido',  docs[0].typeidtax);
                frm.set_value('razonSocialSujetoRetenido',  docs[0].supplier_name);
                frm.refresh_field('tipoIdentificacionSujetoRetenido');
                frm.set_value('identificacionSujetoRetenido',  docs[0].tax_id);
			}
		});
	},
	estab: function(frm)
	{
	    console.log('estab event!!!');
	},
	taxes_add(frm, cdt, cdn) 
	{ // "links" is the name of the table field in ToDo, "_add" is the event
        // frm: current ToDo form
        // cdt: child DocType 'Dynamic Link'
        // cdn: child docname (something like 'a6dfk76')
        // cdt and cdn are useful for identifying which row triggered this event

        frappe.msgprint('A row has been added to the links table 🎉 ');
    },
    
})

frappe.ui.form.on("Purchase Taxes and Charges Ec", "codDocSustentoLink", function(frm, cdt, cdn) {     
     
     //console.log(frm);
     //console.log(cdt);
     //console.log(cdn);

     //console.log(locals);
     
    let item = locals[cdt][cdn]; 

    console.log(item.codDocSustentoLink);

    //let articleId = Math.round(+new Date()/1000);
    
    //item.article_id = articleId;
    //item.codDocSustento = articleId;
    
    //let tax = frappe.get_doc(cdt, cdn);    
    //console.log(tax);

    //let type_document_sri = frappe.get_doc('Sri Type Doc', item.codDocSustentoLink);
    //console.log(type_document_sri);    
    
    setTimeout(
        async function () 
        {
            var type_document_sri = await frappe.db.get_doc('Sri Type Doc', item.codDocSustentoLink);
            console.log(type_document_sri);

            item.codDocSustento = type_document_sri.document_type;
            frm.refresh_field('taxes');
        }
        , 500);
});

frappe.ui.form.on("Purchase Taxes and Charges Ec", "numDocSustentoLink", function(frm, cdt, cdn) {         
    let item = locals[cdt][cdn];
    console.log(item);
    //console.log(item.numDocSustentoLink.numeroAutorizacion);

    frappe.db.get_list('Purchase Invoice', { 'fields': '["*"]', 'filters': { 'name': item.numDocSustentoLink } }).then(docs => {
        console.log(docs);

        item.numDocSustento = '';
        item.numDocSustento = '';
        item.fechaEmisionDocSustento = '';
        frm.refresh_field('taxes');

        if(docs.length > 0)
        {

            /*
            frappe.db.set_value('Purchase Invoice', item.numDocSustentoLink, 'numeroautorizacion', '4567890654327890211')
            .then(r => {
                let doc = r.message;
                console.log(doc);
            });

            frappe.db.set_value('Purchase Invoice', item.numDocSustentoLink, 'docidsri', '0101000000008')
            .then(r => {
                let doc = r.message;
                console.log(doc);
            });

            frappe.db.set_value('Purchase Invoice', item.numDocSustentoLink, 'fechaautorizacion', '2024-01-01 00:01:01')
            .then(r => {
                let doc = r.message;
                console.log(doc);
            });
            */
            
            console.log(docs[0].numeroautorizacion);

            if(docs[0].numeroautorizacion != undefined && docs[0].numeroautorizacion != null && docs[0].numeroautorizacion != '')
            {
                //item.numDocSustento = docs[0].numeroautorizacion;
                item.numDocSustento = docs[0].docidsri; //docidsri --> cambiarlo a numDoc
                item.fechaEmisionDocSustento = docs[0].fechaautorizacion;
                frm.refresh_field('taxes');
            }
            else
            {
                var document_preview = `
                    <p>Confirmar para procesar el documento ${item.numDocSustentoLink}</p>
                    <table>
                        <tr>
                            <td>Nombre proveedor:</td>
                            <td>${docs[0].supplier_name}</td>
                        </tr>
                        <tr>
                    </table>`;

                frappe.msgprint({
                    title: __('Factura de compra no tiene datos del SRI'),
                    indicator: 'red',
                    message: __(document_preview)
                });
            }
        }
        else
        {
            var document_preview = `
                    <p>Documento inexistente ${item.numDocSustentoLink}.</p>
                    <table>
                        <tr>
                            <td>Asegurese de que el documento exista antes de crear un comprobante de retención.</td>                            
                        </tr>
                        <tr>
                    </table>`;

            frappe.msgprint({
                title: __('Factura no encontrada'),
                indicator: 'red',
                message: __(document_preview)
            });
        }

    });

    setTimeout(
        async function ()
        {
            //console.log(item.numDocSustentoLink);

            //Busca las factura de venta para obtener los datos y llenarlos automáticamente
            
            //frappe.db.get_doc('Purchase Invoice', item.numDocSustentoLink).then(doc => {
            //    console.log(doc)
            //});           
                

            /*
            var document_sri = await frappe.db.get_doc('Purchase Invoice', item.numDocSustentoLink);
            console.log(document_sri);

            item.numDocSustento = document_sri.numeroAutorizacion;
            item.numDocSustento = document_sri.docidsri; //docidsri --> cambiarlo a numDoc
            item.fechaEmisionDocSustento = document_sri.fechaautorizacion;
            frm.refresh_field('taxes');
            */
        }
        , 500);    
    
    //frm.refresh_field('taxes');
});



frappe.ui.form.on("Purchase Taxes and Charges Ec", "codigoRetencion", function(frm, cdt, cdn) {         
    let item = locals[cdt][cdn];
    console.log(item);
    //console.log(item.numDocSustentoLink.numeroAutorizacion);

    frappe.db.get_list('Account', { 'fields': '["*"]', 'filters': { 'name': item.codigoRetencion } }).then(docs => {
        console.log(docs);

        item.porcentajeRetener = '0';       
        frm.refresh_field('taxes');

        if(docs.length > 0)
        {   
            console.log(docs[0].codigoretencion);

            if(docs[0].codigoretencion != undefined && docs[0].codigoretencion != null && docs[0].codigoretencion != '')
            {                
                item.porcentajeRetener = docs[0].tax_rate;
                frm.refresh_field('taxes');
            }
            else
            {
                var document_preview = `
                    <p>Cuenta contable incorrecta</p>
                    <table>
                        <tr>
                            <td>Nombre proveedor:</td>                            
                        </tr>
                        <tr>
                    </table>`;

                frappe.msgprint({
                    title: __('Factura de compra no tiene datos del SRI'),
                    indicator: 'red',
                    message: __(document_preview)
                });
            }
        }
        else
        {
            var document_preview = `
                    <p>Documento inexistente ${item.codigoRetencion}.</p>
                    <table>
                        <tr>
                            <td>Asegurese de que el documento exista antes de crear un comprobante de retención.</td>                            
                        </tr>
                        <tr>
                    </table>`;

            frappe.msgprint({
                title: __('Factura no encontrada'),
                indicator: 'red',
                message: __(document_preview)
            });
        }
    });
});