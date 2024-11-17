const url = document.location.href;

export const copyButton = new Clipboard('.copy-button', {
  text: function () {
    return url
  }
})
