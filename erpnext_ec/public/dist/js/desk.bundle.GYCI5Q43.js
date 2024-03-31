(() => {
  // ../erpnext_ec/erpnext_ec/public/js/utils/desk.bundle.js
  console.log("SIPIS!");
  setTimeout(
    async function() {
      var buttonGroup = `<div class="dropdown show" style="display: inline-block;">
  <a class="btn btn-secondary dropdown-toggle btn-xs" href="#" role="button" id="dropdownMenuTopNavBar" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
  </a>
  <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuTopNavBar">
    <a class="dropdown-item" href="javascript:document.Website.DownloadXml(''); "><i class="fa fa-file-code-o" aria-hidden="true"></i> Xml </a>
    <a class="dropdown-item" href="javascript:document.Website.DownloadPdf(''); "><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Pdf </a>
    <a class="dropdown-item" href="javascript:document.Website.ShowInfo(''); "><i class="fa fa-info-circle" aria-hidden="true"></i> Ver informaci\xF3n</a>
  </div>
</div>
`;
      $(".form-inline.fill-width.justify-content-end").after(buttonGroup);
    },
    2e3
  );
  console.log("YAPIS!");
})();
//# sourceMappingURL=desk.bundle.GYCI5Q43.js.map
