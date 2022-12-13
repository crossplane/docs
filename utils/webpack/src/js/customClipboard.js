// Customize clipboard.js
import * as ClipboardJS from 'clipboard';

// Most of the following is directly from the Bootstrap Website.
// https://github.com/twbs/bootstrap/blob/main/site/assets/js/code-examples.js
const btnHtml = [
  '<div class="bd-code-snippet">',
  '   <div class="bd-clipboard">',
  '      <button type="button" class="btn-clipboard">',
  '        <svg class="bi" role="img" title="Copy" aria-label="Copy"><use xlink:href="#clipboard"/></svg>',
  '      </button>',
  '   </div>',
  '</div>'
].join('')

// wrap programmatically code blocks and add copy btn.
document.querySelectorAll('.highlight')
  .forEach(element => {
    if (!element.closest('.bd-example-snippet')) { // Ignore examples made be shortcode
      element.insertAdjacentHTML('beforebegin', btnHtml)
      element.previousElementSibling.append(element)
    }
  })

const clipboard = new ClipboardJS('.btn-clipboard', {
  target: trigger => trigger.closest('.bd-code-snippet').querySelector('.highlight'),
  text: function(trigger) { return getText(trigger.closest('.bd-code-snippet').querySelector('.highlight')) }
})

clipboard.on('success', event => {
  const iconFirstChild = event.trigger.querySelector('.bi').firstElementChild
  const namespace = 'http://www.w3.org/1999/xlink'
  const originalXhref = iconFirstChild.getAttributeNS(namespace, 'href')
  const originalTitle = event.trigger.title

  event.clearSelection()
  iconFirstChild.setAttributeNS(namespace, 'href', originalXhref.replace('clipboard', 'check2'))

  setTimeout(() => {
    iconFirstChild.setAttributeNS(namespace, 'href', originalXhref)
    event.trigger.title = originalTitle
  }, 2000)
})

clipboard.on('error', event => {
  const modifierKey = /mac/i.test(navigator.userAgent) ? '\u2318' : 'Ctrl-'
  const fallbackMsg = `Press ${modifierKey}C to copy`
})

// Get the lines from the code box based on the optional `copy-lines` attribute.
// Defaults to copying all lines.
function getText(highlightDiv){

  // Find the code lines inside the code table
  var codeLines = highlightDiv.getElementsByClassName("line")
  var codeText = []

  for (var i = 0; i < codeLines.length; i++){
    codeText.push(codeLines[i].innerText)
  }

    // default is only copy line 1
    var startLines = 1
    var endLines = codeText.length

    // did they set the "copy-lines" value in the code box to identify what to copy?
    if("copy-lines" in highlightDiv.attributes){

      var copyVal = highlightDiv.attributes["copy-lines"].value

      // if it's a single digit then start == end
      if(copyVal.length === 1){
        startLines = parseInt(copyVal, 10)
        endLines = parseInt(copyVal, 10)
      }
      // If the default copy is 1 instead of all, the following is required.
      // else if(copyVal.localeCompare("all") === 0){
      //     endLines = codeContent.length
      // }
      else {
        // look for a value like 1-10. Split on the dash.
        var startendLines = copyVal.split("-")
        startLines = parseInt(startendLines[0], 10)
        endLines = parseInt(startendLines[1], 10)
      }

      if(startLines <= 0 || isNaN(startLines)) {
        startLines = 1
      }
      if(endLines <= 0 || endLines > codeText.length - 1 || isNaN(endLines)){
        endLines = codeText.length
      }

    }

    return codeText.slice((startLines - 1), endLines).join('')

  }