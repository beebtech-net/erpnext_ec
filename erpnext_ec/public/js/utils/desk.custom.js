function getCookie(cname) {
  let name = cname + "=";
  let ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function showEvalSriSettings(changeStatus)
{
  frappe.call({
    method: "erpnext_ec.utilities.tools.validate_sri_settings",
    args: 
    {
      success: function(r) {},
      always: function(r) {},
    },
    callback: function(r)
    {
      console.log(r);
      if(r == null || r == undefined)
        return;
      
      if(r.message == null || r.message == undefined)
        return;

      //if(r.message.SettingsAreReady)
      //{
        //console.log('Configuracion Lista!!');
        //return;
      //}
      //else
      //{
        //console.log('Configuracion No esta Lista!!');
      //}

      var data_header = '';
      var data_alert = '';
      var SettingsAreReady = true;

      for(ig=0; ig < r.message.groups.length; ig++)
      {
        data_header += '<table>';

        if(r.message.groups[ig].SettingsAreReady == false && SettingsAreReady)
        {
          SettingsAreReady = false;
        }

        for(i=0; i < r.message.groups[ig].header.length; i++)
          {                  
            data_header += `<tr>
                      <td>${r.message.groups[ig].header[i].description}:</td>
                      <td>${r.message.groups[ig].header[i].value}</td>
                  </tr>`;
          }
          
          for(i=0; i < r.message.groups[ig].alerts.length; i++)
            {				
              data_header += document.Website.CreateAlertItem(r.message.groups[ig].alerts[i].description);
            }

        data_header += '</table>';
        data_header += '<div class="dropdown-divider"></div>';
        //data_alert += '<table>';
  
        //for(i=0; i < r.message.groups[ig].alerts.length; i++)
        //{				
          //data_alert += document.Website.CreateAlertItem(r.message.groups[ig].alerts[i].description);
        //}
        //data_alert += '</table>';              
      }

      //console.log(data_alert);

      var document_preview = `
            <p>Se requiere revisión</p>` + 
      data_header +
      data_alert +
                `<div class="warning-sri">
                  Por favor, corrija su configuración antes de generar documentos electrónicos.
                </div>`;
      
    if(!SettingsAreReady)
    {
      frappe.msgprint({
        title: __('Configuración incompatible con el SRI'),
        indicator: 'red',
        message: __(document_preview)
      });
    }
      
      if(changeStatus)
      {
        //Se actualiza la cookie a "not"
        frappe.call({
          method: "erpnext_ec.utilities.tools.set_cookie",
          args: 
          {
            cookie_name:'login_boot',
            cookie_value:'not',
            success: function(r) {},
            always: function(r) {},
          },
          callback: function(r)
          {
            //console.log(r);
          },
          error: function(r) {
            //console.log(r);
          },
        });
      }

    },
    error: function(r) {
      console.log(r);
    },
  });
}

function evalSriSettings()
{  
  var login_boot = getCookie('login_boot');

  if(login_boot=='yes')
  {
    showEvalSriSettings(true);
    //console.log('Mensaje de configuracion');        
  }
}

setTimeout(
    async function () {
        /*
        var buttonGroup = `<div class="dropdown show" style="display: inline-block;">
  <a class="btn btn-secondary dropdown-toggle btn-xs" href="#" role="button" id="dropdownMenuTopNavBar" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
  ${frappe.boot.sysdefaults.company }
  </a>
  <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuTopNavBar">
    <a class="dropdown-item" href="javascript:document.Website.DownloadXml(''); "><i class="fa fa-file-code-o" aria-hidden="true"></i> Xml </a>
    <a class="dropdown-item" href="javascript:document.Website.DownloadPdf(''); "><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Pdf </a>
    <a class="dropdown-item" href="javascript:document.Website.ShowInfo(''); "><i class="fa fa-info-circle" aria-hidden="true"></i> Ver información</a>
  </div>
</div>
`;
*/
/*
      var buttonGroup = `<div class="dropdown show" style="display: inline-block;">
        <a class="btn-secondary dropdown-toggle btn-xs" href="#" role="button" id="dropdownMenuTopNavBar" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <div class="" style="max-width: 100px;display: inline-block;text-overflow: ellipsis;overflow-x: hidden;overflow-y: hidden;">
        ${frappe.boot.sysdefaults.company}
        </div>
        </a>  
      </div>
      `;
*/

//$('.form-inline.fill-width.justify-content-end').after(buttonGroup);

      var buttonGroup = `<li class="nav-item dropdown dropdown-mobile show">
        <button class="btn-reset nav-link text-muted ellipsis" 
        data-toggle="" aria-haspopup="true" 
        aria-expanded="true" title="" 
        data-original-title="Compania" style="max-width: 120px;"
        onclick="showEvalSriSettings(false)">
        <span class="ellipsis">${frappe.boot.sysdefaults.company}</span>
        </button>
        </li>`;

      $('li.nav-item.dropdown.dropdown-notifications').before(buttonGroup);        
      
      evalSriSettings();
      
}, 2000);
