
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

const btApiServer = 'http://localhost:3003'; //

const Website = {
    loadingAnimation: `<div class="custom-animation" style="width: 25px;height: 25px;display: inline-block;"><svg version="1.1" id="L9" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 100 100" enable-background="new 0 0 0 0" xml:space="preserve">
    <path fill="#000" d="M73,50c0-12.7-10.3-23-23-23S27,37.3,27,50 M30.9,50c0-10.5,8.5-19.1,19.1-19.1S69.1,39.5,69.1,50">
      <animateTransform attributeName="transform" attributeType="XML" type="rotate" dur="1s" from="0 50 50" to="360 50 50" repeatCount="indefinite"></animateTransform>
  </path>
  </svg></div>`,
    CreateHtmlItem(textInner, color) {
    return `<tr><td><span class="indicator-pill ${color} ellipsis">
                <span class="ellipsis">${textInner}</span>
            </span></td></tr>`;
    },
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
    DownloadFile(doc, typeFile, siteName, doctype_erpnext)
    {
        typeDocSri = '-';

        if(doctype_erpnext == 'Sales Invoice')
            typeDocSri = 'FAC';

        if(doctype_erpnext == 'Delivery Note')
            typeDocSri = 'GRS';

        if(doctype_erpnext == 'Purchase Withholding Sri Ec')
            typeDocSri = 'CRE';
        
        console.log(typeDocSri);
        console.log(typeFile);
        console.log(siteName);

        var btnProcess = $('div.dropdown[data-name="' + doc + '"]');
        //Oculta el botón
        $(btnProcess).hide();
        //Muestra animación de carga
        $(btnProcess).after(document.Website.loadingAnimation);

        frappe.call({
            method: "erpnext_ec.utilities.sri_ws.get_doc",
            args: {
                doc_name: doc,
                typeDocSri: typeDocSri,
                typeFile: typeFile,
                siteName: siteName
                //freeze: true,
                //freeze_message: "Procesando documento, espere un momento.",                
            },
            success: function(r) {
                console.log('success');
                console.log(r);
            },                
            always: function(r) {
                //console.log("siempre!!");
                $(btnProcess).show();
                $(btnProcess).parent().find('.custom-animation').remove();
            },
            error: function(r) {

                console.log('error');
                console.log(r);

                frappe.show_alert({
                    //message: __(`Error al procesar documento ${doc}:` + req.statusText + ":" + req.responseText),
                    message: __(`Error al procesar descarga del documento ${doc}:`),
                    indicator: 'red'
                }, 5);
            },
            callback: function(r) 
            {
                //console.log(r.message);
                
                var fileNameForDownload = doc + `.${typeFile}`;

                if(r != undefined && r.message != undefined && r.message != "")
                {   
                    //Se convierte el resultado en Blob
                    var blob = new Blob([r.message], {
                        type: 'text/plain'
                    });
                    
                    //var blob = r.message;
                    //var fileName = req.getResponseHeader("fileName") //if you have the fileName header available
                    var link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = fileNameForDownload; //doc+".xml";
                    link.click();

                    frappe.show_alert({                        
                        message: __(`Documento XML ${doc} descargado.`),
                        indicator: 'green'
                    }, 5);
                }
                else
                {
                    //console.log(req);
                        //console.log("Error", req.statusText);
                    //console.log('1x');
                    frappe.show_alert({
                        //message: __(`Error al procesar documento ${doc}:` + req.statusText + ":" + req.responseText),
                        message: __(`Error al procesar descarga del documento ${doc}:`),
                        indicator: 'red'
                    }, 5);
                    
                    //$(btnProcess).show();
                    //$(btnProcess).parent().find('.custom-animation').remove();
                }

                $(btnProcess).show();
                $(btnProcess).parent().find('.custom-animation').remove();
            }
        });
    },    
    DownloadXml(doc) {
        //console.log(doc);
        var doctype_erpnext = '';
        var properties_view = Object.getOwnPropertyNames(frappe.views.list_view);
        if(properties_view.length > 0)
        {
            //Lista
            doctype_erpnext = properties_view[0];
            console.log(properties_view[0]);
        }
        else
        {
            //Form
            doctype_erpnext = cur_frm.doctype;
        }         

        var sitenameVar = frappe.boot.sitename;
        document.Website.DownloadFile(doc, 'xml', sitenameVar, doctype_erpnext);
    },
    DownloadPdf(doc) {
        var doctype_erpnext = '';
        var properties_view = Object.getOwnPropertyNames(frappe.views.list_view);
        if(properties_view.length > 0)
        {
            //Lista
            doctype_erpnext = properties_view[0];
            console.log(properties_view[0]);
        }
        else
        {
            //Form
            doctype_erpnext = cur_frm.doctype;
        }  

        var sitenameVar = frappe.boot.sitename;
        document.Website.DownloadFile(doc, 'pdf', sitenameVar, doctype_erpnext);
        //console.log(doc);
    }    
}

document.Website = Website;