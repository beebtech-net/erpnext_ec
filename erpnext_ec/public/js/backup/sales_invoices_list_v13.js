frappe.listview_settings['Sales Invoice'] = frappe.listview_settings['Sales Invoice'] || {};

const btApiServer = 'http://localhost:3003'; //

const Website = {
    loadingAnimation: `<div class="custom-animation" style="width: 25px;height: 25px;display: inline-block;"><svg version="1.1" id="L9" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 100 100" enable-background="new 0 0 0 0" xml:space="preserve">
    <path fill="#000" d="M73,50c0-12.7-10.3-23-23-23S27,37.3,27,50 M30.9,50c0-10.5,8.5-19.1,19.1-19.1S69.1,39.5,69.1,50">
      <animateTransform attributeName="transform" attributeType="XML" type="rotate" dur="1s" from="0 50 50" to="360 50 50" repeatCount="indefinite"></animateTransform>
  </path>
  </svg></div>`,
    CreateAlertItem(textInner) {
        return `<tr><td><span class="indicator-pill red ellipsis">
    		        <span class="ellipsis">${textInner}</span>
    			</span></td></tr>`;
    },
    GetDocumentResponses(doc, tip_doc, sitenamePar) {

        var url = `${btApiServer}/api/SriProcess/getresponses/${doc}?tip_doc=${tip_doc}&sitename=${sitenamePar}`;
        return new Promise(function (resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', url, true);
            //xhr.responseType = 'document';
            //xhr.onload = function () {
            xhr.onreadystatechange = function (oEvent) {
                /*
                var status = xhr.status;
                if (status == 200) {
                    resolve(xhr.response);
                } else {
                    reject(status);
                }
                */

                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        //console.log(xhr.responseText);
                        resolve(xhr.response);
                    }
                    else {
                        reject(xhr.status);
                    }
                }

            };
            /*
            xhr.onloadend = function() {
                if(xhr.status == 404) 
                {
                    throw new Error(url + ' replied 404');
                    //reject('Inválido');
                }
            }
            */
            xhr.send();
        });

    },
    ShowCustomMessage(title, indicator, contentMessage) {
        $('#xmlPreviewDocument').remove();

        var $div = $(`
            <div id="xmlPreviewDocument" class="modal fade" role="dialog" style="z-index: 3000;">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 class="modal-title">${title}</h4>
                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                        </div>
                        <div class="modal-body">
                        <p><code>${contentMessage}</code></p>
                        </div>
                        <div class="modal-footer">
                        </div>
                    </div>
                </div>
            </div>
        `).appendTo('body');


        $('#xmlPreviewDocument').modal('show');
        //frappe.confirm('First Name');

        /*frappe.msgprint({
                        title: __(title),
                        indicator: indicator,
                        message: __(contentMessage)
                    });  */
    },
    DownloadFromRaw(blobContent, fileNameForDownload) {
        var blob = new Blob([blobContent], { type: 'text/plain' });
        //var blob = blobContent;
        //var fileName = req.getResponseHeader("fileName") //if you have the fileName header available
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = fileNameForDownload;
        link.click();
        URL.revokeObjectURL(link.href);
    },
    ShowInfo(doc) {
        //doc String Parameter

        var btnProcess = $('div.dropdown[data-name="' + doc + '"]');
        //Oculta el botón
        $(btnProcess).hide();
        //Muestra animación de carga
        $(btnProcess).after(document.Website.loadingAnimation);

        setTimeout(
            async function () {
                var tip_doc = 'FAC';
                var document_responses_json = '';
                var document_responses = `<table class="table table-striped caption-top">
                <thead>
                    <tr>
                        <td>Fecha/Hora</td>
                        <td>Respuesta</td>
                        <td>-</td>
                        <td>-</td>
                    </tr>
                </thead>
                <tbody>
                `;
                var sitenameVar = frappe.boot.sitename;

                try {
                    document_responses_json = await document.Website.GetDocumentResponses(doc, tip_doc, sitenameVar);
                    document_responses_json = JSON.parse(document_responses_json);

                    for (let ij = 0; ij < document_responses_json.length; ij++) {
                        var xmldata_dec = document_responses_json[ij].xmldata.replace(/&apos;/g, "'")
                            .replace(/&quot;/g, '"')
                            .replace(/&gt;/g, '>')
                            .replace(/&lt;/g, '<')
                            .replace(/&amp;/g, '&');

                        var xmldata_enc = document_responses_json[ij].xmldata.replace(/&/g, '&amp;')
                            .replace(/</g, '&lt;')
                            .replace(/>/g, '&gt;')
                            .replace(/"/g, '&quot;')
                            .replace(/'/g, '&apos;')
                            .replace(/(\r\n|\n|\r)/gm, "");

                        var r_date = document_responses_json[ij].aud_ing_date;
                        var r_status = document_responses_json[ij].status;

                        var r_date_path = document_responses_json[ij].aud_ing_date.replace(/:/g, '');

                        document_responses += `<tr>
                            <td>${r_date}</td>
                            <td>${r_status}</td>
                            <td>
                            <button class="btn btn-xs" data-name="" title="Mostrar" onclick="document.Website.ShowCustomMessage('${r_status} - ${r_date}','green', '${xmldata_enc}');">
						        <svg class="icon icon-sm" style=""><use class="" href="#icon-view"></use></svg>
					        </button>
					        </td>
					        <td>
                            <button class="btn btn-xs" data-name="" title="Descargar" onclick="document.Website.DownloadFromRaw('${xmldata_enc}', '${tip_doc}-${r_status}-${r_date_path}-${doc}.xml');">
						        <svg class="icon icon-sm" style=""><use class="" href="#icon-file"></use></svg>
					        </button>
					        </td>
                        </tr>`;

                        //console.log(document_responses_json[ij].status);
                        //aud_ing_date
                        //doc_ref
                        //tip_doc
                        //xmldata
                    }

                    //console.log(document_responses_json);
                }
                catch (exp1) {
                    console.log('Error al obtener datos:' + exp1);
                }

                document_responses += `</tbody></table>`

                var url = `${btApiServer}/api/SriProcess/getdocument/${doc}?tip_doc=FAC&sitename=${sitenameVar}`;
                //console.log(url);

                var req = new XMLHttpRequest();
                req.open("POST", url, true);

                req.onreadystatechange = function (oEvent) {
                    //console.log(req.readyState);

                    if (req.readyState === 4) {
                        if (req.status === 200) {

                            //var btnProcess = $('.dropdown div[data-name="' + doc + '"]').parent().find('.btn-download-' + typeFile);
                            $(btnProcess).show();
                            $(btnProcess).parent().find('.custom-animation').remove();

                            var stringResponse = req.responseText;

                            try {
                                var jsonResponse = JSON.parse(stringResponse);
                            } catch (e) { }

                            //console.log(jsonResponse);

                            //jsonResponse.detalle

                            //${stringResponse}
                            var document_preview = `
                            <nav>
  <div class="nav nav-tabs" id="nav-tab" role="tablist">
    <button class="nav-link active" id="nav-home-tab" data-toggle="tab" data-target="#nav-home" type="button" role="tab" aria-controls="nav-home" aria-selected="true">Json Data</button>
    <button class="nav-link" id="nav-contact-tab" data-toggle="tab" data-target="#nav-contact" type="button" role="tab" aria-controls="nav-contact" aria-selected="false">Respuestas</button>
    <button class="nav-link" id="nav-profile-tab" data-toggle="tab" data-target="#nav-profile" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">Sri</button>    
  </div>
</nav>
<div class="tab-content" id="nav-tabContent">
  <div class="tab-pane fade show active" id="nav-home" role="tabpanel" aria-labelledby="nav-home-tab">
    <div style="overflow-y: auto;max-height: 380px;">
        <div id="wrapper-json"></div>
    </div>
  </div>
  <div class="tab-pane fade" id="nav-contact" role="tabpanel" aria-labelledby="nav-contact-tab">
    <div style="overflow-y: auto;max-height: 380px;">
        ${document_responses}
    </div>
  </div>
  <div class="tab-pane fade" id="nav-profile" role="tabpanel" aria-labelledby="nav-profile-tab">
    <div style="overflow-y: auto;max-height: 380px;">
        
    </div>
  </div>
</div>`;

                            //Medio segundo despues de mostrar el diálogo
                            setTimeout(
                                function () {
                                    var wrapper = document.getElementById("wrapper-json");
                                    var tree = jsonTree.create(jsonResponse, wrapper);

                                }
                                , 500);

                            // Create json-tree
                            //var tree = jsonTree.create(jsonResponse, wrapper);

                            // Expand all (or selected) child nodes of root (optional)
                            //tree.expand(function(node) {
                            //return node.childNodes.length < 2 || node.label === 'phoneNumbers';
                            //});

                            frappe.msgprint({
                                title: __('Datos del documento ' + doc),
                                indicator: 'green',
                                message: __(document_preview)
                            });


                            //bye bye!!
                            return;

                        } else {
                            console.log(req);
                            //console.log("Error", req.statusText);
                            console.log('1x');
                            frappe.show_alert({
                                message: __(`Error al procesar documento ${doc}:` + req.statusText + ":" + req.responseText),
                                indicator: 'red'
                            }, 5);
                        }

                        //console.log('Terminado proceso con el SRI!');
                        $(btnProcess).show();
                        $(btnProcess).parent().find('.custom-animation').remove();

                    }
                };
                req.send();

            }, 500);

    },
    SendEmail(doc) {
        let d = new frappe.ui.Dialog({
            title: 'Enviar email',
            fields: [
                {
                    label: 'Email',
                    fieldname: 'email_to',
                    fieldtype: 'Data'
                },
                {
                    label: 'Copia (cc)',
                    fieldname: 'email_cc',
                    fieldtype: 'Data'
                }
            ],
            primary_action_label: 'Enviar',
            primary_action(values) {
                console.log(doc);
                //console.log(values);
                //console.log(values.email_to);
                //frappe.utils.validate_type('ronald_chonillo@gmail.com', 'email');
                //show_alert with indicator
                var sitenameVar = frappe.boot.sitename;
                var url = `${btApiServer}/api/Tool/AddToEmailQuote/${doc}?tip_doc=FAC&sitename=${sitenameVar}&email_to=${values.email_to}`;
                var req = new XMLHttpRequest();
                req.open("POST", url, true);
                //req.responseType = "blob";
                /*
                req.loadend = function (event) {
                    console.log('Terminado');
                    $(btnProcess).show();
                    $(btnProcess).parent().find('.custom-animation').remove();
                };
                */
                req.onload = function (event) {

                    console.log('Terminado');
                    //$(btnProcess).show();
                    //$(btnProcess).parent().find('.custom-animation').remove();

                    frappe.show_alert({
                        message: __(`Documento ${doc} fue agregado a la cola de envío`),
                        indicator: 'green'
                    }, 3);

                };

                frappe.show_alert({
                    message: __(`Documento ${doc} se agregará la cola de envío`),
                    indicator: 'green'
                }, 2);

                req.send();


                d.hide();
            }
        });

        d.show();
    },
    DownloadFile(doc, typeFile, sitename) {
        //Cuando se usan botones individuales
        //var btnProcess = $('.list-actions button[data-name="' + doc + '"]').parent().find('.btn-download-' + typeFile);

        var btnProcess = $('div.dropdown[data-name="' + doc + '"]');
        //Oculta el botón
        $(btnProcess).hide();
        //Muestra animación de carga
        $(btnProcess).after(document.Website.loadingAnimation);
        //console.log(btnProcess);

        var url = `${btApiServer}/api/Download/${typeFile}/${doc}?tip_doc=FAC&sitename=${sitename}`;
        var req = new XMLHttpRequest();
        req.open("POST", url, true);
        req.responseType = "blob";
        /*
        req.loadend = function (event) {
            console.log('Terminado');
            $(btnProcess).show();
            $(btnProcess).parent().find('.custom-animation').remove();
        };
        */
        req.onload = function (event) {
            //console.log(req);
            var fileNameForDownload = doc + `.${typeFile}`;
            var disposition = req.getResponseHeader('Content-Disposition');
            //console.log(disposition);
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    fileNameForDownload = matches[1].replace(/['"]/g, '');
                }
            }

            var blob = req.response;
            //var fileName = req.getResponseHeader("fileName") //if you have the fileName header available
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = fileNameForDownload;
            link.click();

            //console.log('Terminado');
            $(btnProcess).show();
            $(btnProcess).parent().find('.custom-animation').remove();
        };

        req.send();
    },
    //$(document) .ready (function () {
    DownloadXml(doc) {
        var sitenameVar = frappe.boot.sitename;
        document.Website.DownloadFile(doc, 'xml', sitenameVar);
        /*
fetch(url)
  .then(resp => resp.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    // the filename you want
    a.download = 'todo-1.xml';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    //alert('your file has downloaded!'); // or you know, something with better UX...
  })
  .catch(() => alert('oh no!'));*/

    },

    DownloadPdf(doc) {
        var sitenameVar = frappe.boot.sitename;
        document.Website.DownloadFile(doc, 'pdf', sitenameVar);
        //console.log(doc);
    }
    //});
}

document.Website = Website;

function SetupCustomButtons(doc) {
    setTimeout(
        async function () {

            var buttonGroupExists = $('div.dropdown[data-name="' + doc.name + '"]');
            if (buttonGroupExists.length > 0) {
                //Evitamos que se renderice varias veces el botón de opciones
                return false;
            }

            //console.log(doc);
            //console.log(doc.name);
            var docApi = await frappe.db.get_doc('Sales Invoice', doc.name);
            //var docApi = frappe.get_doc('Sales Invoice', doc.name);
            //console.log(docApi);
            //console.log(this);
            //console.log(doc.name);
            //console.log('.list-actions button[data-name="'+ doc.name +'"]');
            //console.log($('.list-actions button[data-name="'+ doc.name +'"]').length);

            //Lograr que sea visible en mobile
            $('.list-actions').parent().removeClass('hidden-md');
            $('.list-actions').parent().removeClass('hidden-xs');
            $('.list-actions').parent().parent().removeClass('hidden-xs');
            //

            var actionButton = $('.list-actions > .btn-action[data-name="' + doc.name + '"]');

            $(actionButton).removeClass('btn-default');
            $(actionButton).addClass('btn-warning');

            $(actionButton).attr('endRender', 'true');

            $(actionButton).click(function (e) {
                e.preventDefault();
                SetupMainActionButton(doc);
            });

            //icon-attachment
            //icon-tool
            //icon-review
            //icon-printer
            //icon-arrow-right
            //#icon-reply
            //#icon-reply-all
            //console.log(docApi.numeroautorizacion);

            //console.log(docApi.sri_estado);
            var removeMainButton = false;

            if ((docApi.numeroautorizacion == "" || docApi.numeroautorizacion == "0") && docApi.sri_estado != 200)
            //if(true)
            {
				//Continúa la renderización del botón de envío
				// ya que no se ha autorizado
            }
            else {
                //Oculta el botón principal
                $(actionButton).addClass('d-none');

                // old icon version <svg class="icon icon-sm" style="">
                //<use class="" href="#icon-reply-all"></use>
                //</svg>
                //	new icon version <i class="fa fa-paper-plane"></i>
                //Se agrega el botón de envío
                $(actionButton).parent().append(`
                    <button class="btn btn-xs btn-default" data-name="` + doc.name + `" title="Enviar por email" onclick="event.stopPropagation(); document.Website.SendEmail('` + doc.name + `'); ">
    					<i class="fa fa-paper-plane"></i>
    				</button>
                `);

                removeMainButton = true;
            }

            /*
            $('.list-actions button[data-name="' + doc.name + '"]').parent().append(`
                <button class="btn btn-xs btn-default btn-download-xml" data-name="` + doc.name + `" title="Descargar Xml" onclick="event.stopPropagation(); document.Website.DownloadXml('` + doc.name + `'); ">
                    <svg class="icon icon-sm" style="">
                        <use class="" href="#icon-small-file"></use>
                    </svg>
                </button>
            `);

            $('.list-actions button[data-name="' + doc.name + '"]').parent().append(`
                <button class="btn btn-xs btn-default btn-download-pdf" data-name="` + doc.name + `" title="Descargar Pdf" onclick="event.stopPropagation(); document.Website.DownloadPdf('` + doc.name + `'); ">
                    <svg class="icon icon-sm" style="">
                        <use class="" href="#icon-printer"></use>
                    </svg>
                </button>
            `);
            */


            var buttonGroup = `<div class="dropdown show" data-name="` + doc.name + `" style="display: inline-block;position: unset !important;">
  <a class="btn btn-secondary dropdown-toggle btn-xs" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">    
  </a>
  <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
    <a class="dropdown-item" href="javascript:document.Website.DownloadXml('` + doc.name + `'); "><i class="fa fa-file-code-o" aria-hidden="true"></i> Xml ${doc.name}</a>
    <a class="dropdown-item" href="javascript:document.Website.DownloadPdf('` + doc.name + `'); "><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Pdf ${doc.name}</a>
    <a class="dropdown-item" href="javascript:document.Website.ShowInfo('` + doc.name + `'); "><i class="fa fa-info-circle" aria-hidden="true"></i> Ver información</a>
  </div>
</div>
`;

            var buttonGroupExists = $('div.dropdown[data-name="' + doc.name + '"]');
            if (buttonGroupExists.length > 0) {
                //Evitamos que se renderice varias veces el botón de opciones
                return false;
            }

            $(actionButton).parent().append(buttonGroup);

            //
            if (removeMainButton) {
                //Se elimina el botón principal
                $(actionButton).remove();
            }

        }, 1000);
}

function SetupMainActionButton(doc) {
    setTimeout(
        async function () {
            var sitenameVar = frappe.boot.sitename;
			var customer_email_id = '';
			
            var customerApi = await frappe.db.get_doc('Customer', doc.customer);
            //console.log(customerApi);

			var customerAddress = null;

			if(customerApi.customer_primary_address != null)
			{
				customerAddress = await frappe.db.get_doc('Address', customerApi.customer_primary_address);
				//console.log(customerAddress);
			}

            var paymentsApi = await frappe.db.get_list('Payment Request', { 'filters': { 'reference_name': doc.name } });
            //console.log(paymentsApi);
            var paymentsEntryApi = await frappe.db.get_list('Payment Entry Reference', { 'filters': { 'reference_name': doc.name } });
            //console.log(paymentsEntryApi);

            var docApi = frappe.get_doc('Sales Invoice', doc.name);
            var data_alert = '<table>';
            //console.log(docApi);
            var documentIsReady = true;

            if (paymentsApi.length == 0 && paymentsEntryApi.length == 0) {
                data_alert += document.Website.CreateAlertItem(`No se ha definido ni solicitud de pago ni entrada de pago`);
                documentIsReady = false;
            }

            //if(docApi.tax_id == "" || docApi.tax_id == "9999999999")
            //{
            //data_alert += `<span class="indicator-pill red ellipsis">
            //    <span class="ellipsis"> Cédula/Ruc del cliente es ${docApi.tax_id}</span>
            //</span>`;
            //}

            if (customerApi.tax_id == "" || customerApi.tax_id == "9999999999") {
                data_alert += document.Website.CreateAlertItem(`Cédula/Ruc del cliente es ${customerApi.tax_id}`);
            }
			
			if (customerAddress == null) {
                data_alert += document.Website.CreateAlertItem(`No se han definido datos de dirección del cliente`);
				documentIsReady = false;
            }
			
			
			if (customerAddress != null && (customerAddress.email_id == "" || customerAddress.email_id == null )) {
                data_alert += document.Website.CreateAlertItem(`No se ha definido Email del cliente`);
				documentIsReady = false;
            }
			
			if (customerAddress != null)
			{
				customer_email_id = customerAddress.email_id;
			}

            if (docApi.estab == null) {
                data_alert += document.Website.CreateAlertItem(`Establecimiento incorrecto (${docApi.estab})`);
                documentIsReady = false;
            }

            if (docApi.ptoemi == null) {
                data_alert += document.Website.CreateAlertItem(`Punto de emisión incorrecto (${docApi.ptoemi})`);
                documentIsReady = false;
            }

            data_alert += '</table>'

            //await frappe.db.get_doc('Customer', 'CONSUMIDOR FINAL')

            var document_preview = `
            <p>Confirmar para procesar el documento ${doc.name}</p>
            <table>
                <tr>
                    <td>Nombre cliente:</td>
                    <td>${doc.customer_name}</td>
                </tr>
                <tr>
                    <td>Tip.Doc. cliente:</td>
                    <td>${customerApi.typeidtax}</td>
                </tr>
                <tr>
                    <td>Cédula/RUC cliente:</td>
                    <td>${customerApi.tax_id}</td>
                </tr>
				<tr>
                    <td>Email cliente:</td>
                    <td>${customer_email_id}</td>
                </tr>
            </table>
            ` + data_alert +
                `<div class="warning-sri">Por favor, verifique que toda la información esté correctamente ingresada antes de enviarla al SRI y generar el documento electrónico.</div>`;


            if (documentIsReady) {

                frappe.warn('Enviar al SRI?',
                    document_preview,
                    () => {

                        frappe.show_alert({
                            message: __(`Documento ${doc.name} está siendo procesado en el SRI, por favor espere un momento. `),
                            indicator: 'green'
                        }, 7);

                        var btnProcess = $('.list-actions button[data-name="' + doc.name + '"]').parent().find('.btn-action');
                        //Oculta el botón
                        $(btnProcess).hide();
                        //Muestra animación de carga
                        $(btnProcess).after(document.Website.loadingAnimation);

                        // action to perform if Yes is selected
                        console.log('Enviando al SRI');
                        //console.log(doc);
                        var docApi = frappe.get_doc('Sales Invoice', doc.name);
                        //console.log(docApi);

                        //sitenameVar = sitenameVar + 'ddd';

                        var url = `${btApiServer}/api/SriProcess/sendmethod/${doc.name}?tip_doc=FAC&sitename=${sitenameVar}`;
                        //console.log(url);

                        var req = new XMLHttpRequest();
                        req.open("POST", url, true);

                        req.onreadystatechange = function (oEvent) {
                            //console.log(req.readyState);

                            if (req.readyState === 4) {
                                if (req.status === 200) {

                                    //console.log(req);
                                    //console.log(req.responseText)

                                    var stringResponse = req.responseText;
                                    stringResponse = stringResponse.replace(/(<([^>]+)>)/gi, '');
                                    //const jsonResponse = JSON.parse(req.responseText);
                                    const jsonResponse = JSON.parse(stringResponse);
                                    //console.log(jsonResponse);

                                    var newNumeroAutorizacion = jsonResponse.data.autorizaciones.autorizacion[0].numeroAutorizacion;

                                    // old icon version <use class="" href="#icon-reply-all"></use>
                                    //	new icon version <i class="fa fa-paper-plane"></i>
                                    $(btnProcess).parent().find('.custom-animation').remove();
                                    $(btnProcess).parent().append(`
                                <button class="btn btn-xs btn-default" data-name="` + doc.name + `" title="Enviar por email" onclick="event.stopPropagation(); document.Website.SendEmail('` + doc.name + `'); ">                					
                					<i class="fa fa-paper-plane"></i>                					
                				</button>
                            `);

                                    frappe.show_alert({
                                        message: __(`Documento ${doc.name} fue procesado en el SRI se obtuvo la clave de acceso: ` + newNumeroAutorizacion),
                                        indicator: 'green'
                                    }, 5);

                                    //bye bye!!
                                    return;

                                } else {
                                    console.log(req);
                                    //console.log("Error", req.statusText);
                                    console.log('1x');
                                    frappe.show_alert({
                                        message: __(`Error al procesar documento ${doc.name}:` + req.statusText + ":" + req.responseText),
                                        indicator: 'red'
                                    }, 5);
                                }

                                //console.log('Terminado proceso con el SRI!');
                                $(btnProcess).show();
                                $(btnProcess).parent().find('.custom-animation').remove();

                            }
                        };

                        req.onload = function (event) {
                            //console.log(req);
                            //var jsonResponse = req.response;

                            //console.log(jsonResponse);

                            //console.log('Terminado');
                            //$(btnProcess).show();
                            //$(btnProcess).parent().find('.custom-animation').remove();

                            //frappe.show_alert({
                            //       message:__(`Documento ${doc.name} fue procesado en el SRI`),
                            //       indicator:'green'
                            //  }, 5);
                        };

                        /*
                        function reqError() {
                            $(btnProcess).show();
                            $(btnProcess).parent().find('.custom-animation').remove();
                            
                            console.log(event);
                            
                            frappe.show_alert({
                                   message:__(`Error al procesar documento ${doc.name}`),
                                   indicator:'red'
                               }, 3);
                        };
                        
                       req.addEventListener("error", reqError);
                       */

                        req.send();

                    },
                    'Confirmar proceso de envío al SRI'
                );
            }
            else {
                frappe.msgprint({
                    title: __('Factura con datos faltantes'),
                    indicator: 'red',
                    message: __(document_preview)
                });
            }


        }, 100);
}

function PrepareDocument(doc_name)
{
	setTimeout(
        async function ()
		{
			var docApi = frappe.get_doc('Sales Invoice', doc_name);	
			
			//console.log(docApi);
			
			var sitenameVar = frappe.boot.sitename;			
			var customerApi = await frappe.db.get_doc('Customer', docApi.customer);

			var customerAddress = null;

			if(customerApi.customer_primary_address != null)
			{
				customerAddress = await frappe.db.get_doc('Address', customerApi.customer_primary_address);
				//console.log(customerAddress);
			}

			
			var paymentsItems = null;
			var paymentsEntryApi = null;
			var paymentsEntryRefApi = await frappe.db.get_list('Payment Entry Reference', { 'fields': '["*"]', 'filters': { 'reference_name': docApi.name } });			
			//console.log(paymentsEntryRefApi);
			
			if(paymentsEntryRefApi!=null && paymentsEntryRefApi.length > 0)
			{
				//console.log(paymentsEntryRefApi[0].parent);
				var paymentsEntryApi = await frappe.db.get_list('Payment Entry', { 'fields': '["*"]', 'filters': { 'name': paymentsEntryRefApi[0].parent } });
				//console.log(paymentsEntryApi);
			}
			
			//Existe pago
			if(paymentsEntryApi!=null && paymentsEntryApi.length > 0)
			{
				console.log('Pago existente...');
				for (const paymentEntryItem of paymentsEntryApi) 
				{
					var modeOfPaymentApi = await frappe.db.get_doc('Mode of Payment', paymentEntryItem.mode_of_payment );				
					//console.log(paymentRequestItem);
					//console.log(modeOfPaymentApi);
					paymentEntryItem.formapago = modeOfPaymentApi.formapago;
					paymentEntryItem.plazo = 0;
					paymentEntryItem.Total = paymentEntryItem.paid_amount;
					paymentEntryItem.UnidadTiempo = "dias";
				}
				
				paymentsItems = paymentsEntryApi;				
			}
			else
			{
				//Sino existe pago se evaluan los requerimientos de pago
				var paymentRequestsApi = await frappe.db.get_list('Payment Request', { 'fields': '["*"]',  'filters': { 'reference_name': docApi.name } });
				console.log('Pago no existente...');
				//console.log(paymentRequestsApi);
				for (const paymentRequestItem of paymentRequestsApi) 
				{
					var modeOfPaymentApi = await frappe.db.get_doc('Mode of Payment', paymentRequestItem.mode_of_payment );				
					//console.log(paymentRequestItem);
					//console.log(modeOfPaymentApi);
					paymentRequestItem.formapago = modeOfPaymentApi.formapago;
					paymentRequestItem.plazo = 0;
					paymentRequestItem.Total = paymentRequestItem.grand_total;
					paymentRequestItem.UnidadTiempo = "dias";
				}
				
				paymentsItems = paymentRequestsApi;
			}
			
			//console.log(paymentsItems);
			
			//var modeOfPaymentApi = await frappe.db.get_list('Mode of Payment', { 'fields': '["*"]',  
			//	'filters': { 'mode_of_payment': 'Transferencia Bancaria' } });
			
			//console.log(modeOfPaymentApi);
  			//paymentRequestsApi.forEach((element) => 
			//{				
			//});
			var DireccionMatriz = '';
			var dirEstablecimiento = '';
			var direccionComprador = '';
			var emailComprador = '';
			
			var companyApi = await frappe.db.get_doc('Company', docApi.company);
			
			if(docApi.company_address != undefined)
			{			
				var companyAddressApi = await frappe.db.get_doc('Address', docApi.company_address);
				if(companyAddressApi.address_line1 == null)
					companyAddressApi.address_line1 = '';
				
				if(companyAddressApi.address_line2 == null)
					companyAddressApi.address_line2 = '';
				
				DireccionMatriz = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
				dirEstablecimiento = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
			}
			else
			{
				var dinLinkApi = await frappe.db.get_list('Dynamic Link', { 'fields': '["*"]','filters': { 'link_doctype': 'Company', 'parenttype':'Address' , 'link_name': docApi.company } });
				var companyAddressApi = await frappe.db.get_doc('Address', dinLinkApi[0].parent);
				
				if(companyAddressApi.address_line1 == null)
					companyAddressApi.address_line1 = '';
				
				if(companyAddressApi.address_line2 == null)
					companyAddressApi.address_line2 = '';
				
				DireccionMatriz = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
				dirEstablecimiento = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
				
			}
			
			if(docApi.customer_address != undefined)
			{
				var customerAddressApi = await frappe.db.get_doc('Address', docApi.customer_address);
				direccionComprador = customerAddressApi.address_title;
				emailComprador = customerAddressApi.email_id;
			}
			else
			{
				var dinLinkApiC = await frappe.db.get_list('Dynamic Link', { 'fields': '["*"]','filters': { 'link_doctype': 'Customer', 'parenttype':'Address' , 'link_name': docApi.customer } });
				var customerAddressApi = await frappe.db.get_doc('Address', dinLinkApiC[0].parent);
				direccionComprador = customerAddressApi.address_title;
				emailComprador = customerAddressApi.email_id;
			}
			
			docApi.DireccionMatriz = DireccionMatriz;
			docApi.dirEstablecimiento = dirEstablecimiento;
			docApi.direccionComprador = direccionComprador;
			docApi.emailComprador = direccionComprador;
				
			var commentsApi = await frappe.db.get_list('Comment', { 'fields': '["*"]','filters': { 'reference_name': docApi.name } });
			
			docApi.company_name = companyApi.company_name;
			docApi.nombreComercial = companyApi.nombrecomercial;
			docApi.agenteRetencion = companyApi.agenteretencion;
			docApi.contribuyenteEspecial = companyApi.contribuyenteespecial;
			docApi.obligadoContabilidad = companyApi.obligadocontabilidad;
			docApi.contribuyenteRimpe = companyApi.contribuyenterimpe;			
			docApi.paymentsItems = paymentsItems;
			
			
			
			const typeidtax = customerApi.typeidtax.split(' ');
			docApi.tipoIdentificacionComprador = typeidtax[0];
			//console.log(customerApi);
			
			if(docApi.taxes!=null && docApi.taxes.length > 0)
			{
				console.log('Taxes existente...');
				for (const taxItem of docApi.taxes) 
				{
					var accountApi = await frappe.db.get_doc('Account', taxItem.account_head );				
					//console.log(accountApi);
					
					taxItem.sricode = accountApi.sricode;
					taxItem.codigoPorcentaje = accountApi.codigoporcentaje;
					
				}
				
				paymentsItems = paymentsEntryApi;				
			}
			
			var strComment = BuildComment(commentsApi);
			
			infoAdicionalData = "";
            infoAdicionalData = [{
									"nombre":"email",
									"valor": customerAddressApi.email_id 
								 },
								 {
									"nombre":"tel.",
									"valor": customerAddressApi.phone
								 },
								 {
									"nombre":"Doc. Ref.",
									"valor":docApi.name
								 },
								 {
									"nombre":"Coment.",
									"valor":strComment
								 }
								];
								
			docApi.infoAdicional = infoAdicionalData;
			//console.log(infoAdicionalData);
			
			
			console.log(docApi);
			console.log(JSON.stringify(docApi));
			//console.log(companyAddressApi);
			//console.log(customerAddressApi);			
			//console.log(companyApi);
			//console.log(paymentRequestsApi);
			
			
		var url = `${btApiServer}/api/Download/xmlfromjson/?tip_doc=FAC&sitename=`;
        var req = new XMLHttpRequest();
        req.open("POST", url, true);
        req.responseType = "blob";
        /*
        req.loadend = function (event) {
            console.log('Terminado');
            $(btnProcess).show();
            $(btnProcess).parent().find('.custom-animation').remove();
        };
        */
        req.onload = function (event) {
            //console.log(req);
            var fileNameForDownload = doc + `.${typeFile}`;
            var disposition = req.getResponseHeader('Content-Disposition');
            //console.log(disposition);
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    fileNameForDownload = matches[1].replace(/['"]/g, '');
                }
            }

            var blob = req.response;
            //var fileName = req.getResponseHeader("fileName") //if you have the fileName header available
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = fileNameForDownload;
            link.click();

            //console.log('Terminado');
            $(btnProcess).show();
            $(btnProcess).parent().find('.custom-animation').remove();
        };

        //req.send(JSON.stringify(docApi));
			
			
			
			
		}, 100);
}

function BuildComment(comments)
{
	var strComment = '';
	for (const comment of comments) 
	{
		//console.log(comment);
		strComment = comment.content;
		console.log(comment);
		strComment = stripHTML(strComment);
		strComment = normalizeString(strComment);
		break;
	}
	
	if(strComment == '')
	{
		
	}
	
	return strComment;
}

function stripHTML(input) {
    return input.replace(/<[^>]*>/g, '');
}

function normalizeString(strSource) {
    let strResult = strSource.trim();
    try {
        strResult = strResult.normalize('NFD').replace(/[^a-zA-Z0-9 ]+/g, '');
    } catch (e) {
        console.error('Error: NormalizeString');
        console.error('Data: ' + strSource);
        // Aquí puedes manejar el error según tus necesidades en JavaScript
    }
    return strResult;
}

frappe.listview_settings['Sales Invoice'].button = {
    show(doc) {

        //return doc.status != 'Paid';
        if (doc.status == 'Cancelled' || doc.status == 'Draft') {
            return false;
        }

        SetupCustomButtons(doc);
        return true;
    },
    get_label() {
        //old return __('<svg class="icon icon-sm" style=""><use class="" href="#icon-mark-as-read"></use></svg>');
        return __('<i class="fa fa-play"></i>');
    },
    get_description(doc) {
        return __('Enviar al SRI')
    },
    action(doc) {
        var actionButton = $('.list-actions > .btn-action[data-name="' + doc.name + '"]');
        //console.log($(actionButton).attr('endRender'));

        if ($(actionButton).attr('endRender') != 'true') {
            frappe.show_alert({
                message: __(`${doc.name} aún se está configurando, espere un momento por favor.`),
                indicator: 'red'
            }, 3);
        }
        //SetupMainActionButton(doc);
    }
}
