//Prepare in list mode
//NO USAR AQUI
//SetListSriButtons('Purchase Withholding Sri Ec');

function refreshPurchaseInvoicesFilter()
{    
    var purchase_withholding_supplier = cur_frm.doc.purchase_withholding_supplier;
    if(purchase_withholding_supplier.length == 0)
    {
        purchase_withholding_supplier = '--------';
    }

    //cur_frm.fields_dict['taxes'].grid.update_docfield_property(
    //    "numDocSustentoLink","value", "");
    
    for(i=0;i<cur_frm.fields_dict['taxes'].grid.grid_rows.length;i++)
    {        
        cur_frm.fields_dict['taxes'].grid.get_grid_row(i).doc.numDocSustentoLink='';

        cur_frm.fields_dict['taxes'].grid.get_grid_row(i).doc.baseImponible=0;
        cur_frm.fields_dict['taxes'].grid.get_grid_row(i).doc.porcentajeRetener=0;
        cur_frm.fields_dict['taxes'].grid.get_grid_row(i).doc.valorRetenido=0;

        cur_frm.fields_dict['taxes'].grid.get_grid_row(i).refresh();
    }

    cur_frm.fields_dict['taxes'].grid.update_docfield_property(
        "numDocSustentoLink","filters", {
            "supplier": purchase_withholding_supplier
            }); 
}

function setPurchaseInvoicesFilter()
{
    console.log('SHOW');
    
    //console.log(cur_frm.fields_dict);

    var purchase_withholding_supplier = cur_frm.doc.purchase_withholding_supplier;
    if(purchase_withholding_supplier.length == 0)
    {
        purchase_withholding_supplier = '44566%^78iu';
    }

    console.log(purchase_withholding_supplier);

    cur_frm.fields_dict['taxes'].grid.get_field("numDocSustentoLink").get_query = function(doc, cdt, cdn) 
        {
            return {
                filters: {
                "supplier": purchase_withholding_supplier
                }
            }
        }
}

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

        setPurchaseInvoicesFilter();
        
        if(frm.doc.status == 'Draft')
        {
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
        }
        
    },
	refresh(frm) {
        //console.log(frm);
		// your code here
		console.log('Refreshhhh!!!');

        //Botones de formulario
        SetFormSriButtons(frm, 'Purchase Withholding Sri Ec');
	},
    purchase_withholding_supplier: function(frm)
	{
        console.log('purchase_withholding_supplier');
        //return false;

        //console.log(frm);
        //var tipoIdentificacionSujetoRetenido = frm.get_value('tipoIdentificacionSujetoRetenido');
        var purchase_withholding_supplier = frm.doc.purchase_withholding_supplier;
        //console.log(purchase_withholding_supplier);

        //if(tipoIdentificacionSujetoRetenido == undefined)
        //    return;

        frm.set_value('tipoIdentificacionSujetoRetenido',  '');
        frm.set_value('razonSocialSujetoRetenido',  '');
        frm.set_value('identificacionSujetoRetenido',  '');
        frm.refresh_field('tipoIdentificacionSujetoRetenido');

		frappe.db.get_list('Supplier', { 'fields': '["*"]', 'filters': { 'name': purchase_withholding_supplier } }).then(docs => {
			//console.log(docs);
			
			if(docs.length > 0)
			{
                //console.log(docs[0].typeidtax);

                frm.set_value('tipoIdentificacionSujetoRetenido',  docs[0].typeidtax);
                frm.set_value('razonSocialSujetoRetenido',  docs[0].supplier_name);
                frm.refresh_field('tipoIdentificacionSujetoRetenido');
                frm.set_value('identificacionSujetoRetenido',  docs[0].tax_id);
			}
		});

        //setPurchaseInvoicesFilter();
        refreshPurchaseInvoicesFilter();
	},
	estab: function(frm)
	{
	    console.log('estab event!!!');
	},
    onload: function(frm) 
    {
        setTimeout(
            async function () 
            {
                $(cur_frm.fields_dict.periodoFiscal.$input).monthpicker({
                    changeYear:true,
                    defaultDate: null
                });
                    
                $(cur_frm.fields_dict.periodoFiscal.$input).val(moment().format('MM/YYYY'));

                // var user_setings = {"updated_on":"Fri+May+24+2024+15:36:47+GMT-0500","GridView":{"Purchase+Taxes+and+Charges+Ec":[{"fieldname":"codDocSustentoLink","columns":1},{"fieldname":"numDocSustentoLink","columns":1},{"fieldname":"fechaEmisionDocSustento","columns":1},{"fieldname":"codigoRetencion","columns":1},{"fieldname":"baseImponible","columns":2},{"fieldname":"porcentajeRetener","columns":2},{"fieldname":"valorRetenido","columns":2}]}};

                // frappe.call({
				// 	method: "frappe.model.utils.user_settings.save",
				// 	args: 
				// 	{
				// 		doctype:"Purchase Withholding Sri Ec",
				// 		user_settings: user_setings,                        
				// 		freeze: true,
				// 		freeze_message: "Procesando documento, espere un momento.",
				// 		success: function(r) {},
				// 		always: function(r) {},
				// 	},
				// 	callback: function(r)
				// 	{
				// 		console.log(r);
				// 	},
				// 	error: function(r) {
				// 		console.log(r);
				// 	},
				// });


            }
            , 500);

        // Agregar un controlador de eventos al campo de mes y año
        //frm.fields_dict.periodoFiscal.$input.on('focus', function() {
            // Abre un selector de fecha personalizado con solo mes y año
        //    frappe.datetime.monthpicker(this);
        //});

        //cur_frm.fields_dict.periodoFiscal.$input.on('focus', function() {
            // Abre un selector de fecha personalizado con solo mes y año
        //    frappe.datetime.monthpicker(this);
        //});

        //$(cur_frm.fields_dict.periodoFiscal.$input).monthpicker({changeYear:true, minDate: "-3 M", maxDate: "+2 Y" });
        
        /*
        cur_frm.fields_dict.periodoFiscal.$input.datepicker({ 
            changeMonth: true,
            changeYear: true,            
            showButtonPanel: false,
            todayButton: false,
            dateFormat: 'mm/yyyy',
            language: "en",
            autoClose: true,
            showMonthAfterYear: true,
            showOtherMonths: true,
	        selectOtherMonths: true,
            onChangeMonthYear: function(year, month) {
                // Aquí puedes ejecutar tu código cuando se cambia el mes o el año
                console.log("Se ha seleccionado un nuevo mes o año:", month, year);
            },
            onSelect: () => {
				//this.$input.trigger("change");
                console.log('onSelect');
			},
            onShow: () => {
				console.log('onShow');
			}            
        });
        */
       /*
        $(cur_frm.fields_dict.periodoFiscal.$input).find('[data-action="month"]').click(() => {
			this.datepicker.selectDate(this.get_now_date());
		});
        */
        //cur_frm.fields_dict.anio_fiscal.$input.datepicker({ 
        //    changeMonth: true,
        //    changeYear: true,            
        //    showButtonPanel: false,
        //    todayButton: false,
        //   dateFormat: 'dd-mm-yyyy',
        //});

        //$(cur_frm.fields_dict.periodoFiscal.$input).datepicker("widget").find(".ui-datepicker-current").hide();
        //$(cur_frm.fields_dict.periodoFiscal).find('.datepicker--buttons').attr('style','display: none;');
        //$(cur_frm.fields_dict.periodoFiscal.$input).find('.datepicker--days').attr('style','display: none;');
    },
    periodoFiscal: function(frm)
    {
        //console.log(frm);
        //var dte = frm.doc.sdate;
        //var mySubString = dte.split('-');
        //var arr = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        //var mnth = mySubString[1] - 1;
        //frm.set_value("periodoFiscal",arr[mnth] + "/"+ mySubString[0])
    },
	taxes_add(frm, cdt, cdn) 
	{ // "links" is the name of the table field in ToDo, "_add" is the event
        // frm: current ToDo form
        // cdt: child DocType 'Dynamic Link'
        // cdn: child docname (something like 'a6dfk76')
        // cdt and cdn are useful for identifying which row triggered this event

        //frappe.msgprint('A row has been added to the links table 🎉 ');
        frappe.show_alert({            
            message: __('A row has been added to the links table 🎉 '),
            indicator: 'red'
        }, 5);
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
            
            console.log("numeroautorizacion");
            console.log(docs[0].numeroautorizacion);

            if(docs[0].numeroautorizacion != undefined && 
                docs[0].numeroautorizacion != null && 
                docs[0].numeroautorizacion != '' &&
                docs[0].numeroautorizacion != '0')
            {
                //item.numDocSustento = docs[0].numeroautorizacion;
                item.numDocSustento = docs[0].docidsri; //docidsri --> cambiarlo a numDoc
                item.fechaEmisionDocSustento = docs[0].fechaautorizacion;
                
                //item.baseImponible = docs[0].base_grand_total; //base_total
                
                item.totalFactura = docs[0].base_grand_total; //base_total

                //TODO: Asignación temporal, para calcular total_iva_factura
                // se debe recorrer todos los items de factura
                // y buscar cuales son los que tienen código 2
                // lo que implica realizar otra busqueda en la 
                // tabla cuentas contables
                var total_iva_factura = docs[0].total_taxes_and_charges;
                
                item.totalIvaFactura = total_iva_factura;

                //ComputeBaseImponible(frm, item, doc[0]);

                ComputeValorRetenido(frm, item);

                //item.porcentajeRetener =
                //item.valorRetenido =                

                frm.refresh_field('taxes');
            }
            else
            {                
                var document_preview = `
                    <div class="fill-width flex title-section">                        
                        <h4 class="modal-title">Factura sin datos del SRI</h4>
                    </div>
                    <p>Verifique documento ${item.numDocSustentoLink}</p>                    
                        <div>
                            <span>Nombre proveedor:</span>
                            <span>${docs[0].supplier_name}</span>
                        </div>`;

                //frappe.msgprint({
                //    title: __('Factura de compra no tiene datos del SRI'),
                //    indicator: 'red',
                //    message: __(document_preview)
                //});
                frappe.show_alert({
                    title: __('Factura no encontradada'),
                    message: __(document_preview),
                    indicator: 'red'
                }, 5);

                item.numDocSustentoLink = '';

                item.baseImponible = 0;
                item.totalFactura = 0;
                item.totalIvaFactura = 0;
                item.valorRetenido = 0;
                frm.refresh_field('taxes');
            }
        }
        else
        {
            var document_preview = `
                    <div class="fill-width flex title-section">                        
                        <h4 class="modal-title">Factura no encontrada</h4>
                    </div>
                    <p>Documento inexistente ${item.numDocSustentoLink}.</p>
                    <table>
                        <tr>
                            <td>Asegurese de que el documento exista antes de crear un comprobante de retención.</td>                            
                        </tr>
                        <tr>
                    </table>`;

            //frappe.msgprint({
            //    title: __('Factura no encontrada'),
            //    indicator: 'red',
            //    message: __(document_preview)
            //});

            frappe.show_alert({
                title: __('Factura no encontradada'),
                message: __(document_preview),
                indicator: 'red'
            }, 5);

            item.baseImponible = 0;
            //porcentajeRetener
            item.totalFactura = 0;
            item.totalIvaFactura = 0;
            item.valorRetenido = 0;
            frm.refresh_field('taxes');

            return;
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
                
                console.log(docs[0].tax_rate);

                console.log(docs[0].withholding_tax_base);

                if(docs[0].withholding_tax_base == "Total de Factura")
                {
                    item.baseImponible = item.totalFactura;
                }

                if(docs[0].withholding_tax_base == "Iva")
                {                    
                    item.baseImponible = item.totalIvaFactura;
                }
                
                if(docs[0].withholding_tax_base == "Valor Fijo")
                {
                    item.baseImponible = docs[0].baseimponiblefijaretencion;
                    console.log('baseimponiblefijaretencion');
                }
                //item.valorRetenido = docs[0].tax_rate * item.baseImponible;
                ComputeValorRetenido(frm, item);
                frm.refresh_field('taxes');
            }
            else
            {
                var document_preview = `
                    <p>Código de retención incorrecto</p>
                    <table>
                        <tr>
                            <td>Nombre proveedor:</td>                            
                        </tr>
                        <tr>
                    </table>`;

                //frappe.msgprint({
                //    title: __('Factura de compra no tiene datos del SRI'),
                //    indicator: 'red',
                //    message: __(document_preview)
                //});

                frappe.show_alert({
                    title: __('----------------'),
                    message: __(document_preview),
                    indicator: 'red'
                }, 5);
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

            //frappe.msgprint({
            //    title: __('Factura no encontrada'),
            //    indicator: 'red',
            //    message: __(document_preview)
            //});

            frappe.show_alert({
                title: __('----------------'),
                message: __(document_preview),
                indicator: 'red'
            }, 5);
        }
    });
});

function ComputeValorRetenido(frm, item)
{
    //item.porcentajeRetener = docs[0].tax_rate;
    //item.valorRetenido = docs[0].tax_rate * item.baseImponible;
    item.valorRetenido = (item.porcentajeRetener * item.baseImponible)/100;
    frm.refresh_field('taxes');
}