function launchInputSizeLimitAlert() {
  var text = "Input files are limited to " + guiInputSizeLimit.toFixed(1) + " MB."
  showErrorDialog("Problem", text)
}

function showErrorDialog(title, text, callback) {
  getErrorDialogTitleEl().textContent = title
  getErrorDialogTextEl().textContent = text
  var dialog = getErrorDialog()
  if (! callback) {
    callback = hideErrorDialog
  }
  dialog.addEventListener("click", function(evt) {
    callback(evt)
  })
  show(getErrorDialog())
}

function hideErrorDialog() {
  hide(getErrorDialog())
}

function showOkDialog(title, text) {
  getOkDialogTitleEl().textContent = title
  getOkDialogTextEl().textContent = text
  show(getOkDialog())
}

