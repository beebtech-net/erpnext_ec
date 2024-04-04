
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
        <button class="btn-reset nav-link text-muted ellipsis" data-toggle="" aria-haspopup="true" aria-expanded="true" title="" data-original-title="Compania" style="max-width: 120px;">
        <span class="ellipsis">${frappe.boot.sysdefaults.company}</span>
        </button>
        </li>`;

      $('li.nav-item.dropdown.dropdown-notifications').before(buttonGroup);        

}, 2000);
