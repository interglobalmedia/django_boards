import {
  scrollTopButton,
  scrollFunction,
  backToTop,
} from './scroll-top.js'
import { copyButton } from './copy-button.js'

// When the user scrolls down 20px from the top of the document, show the button. This must come first.
window.onscroll = function () {
  scrollFunction()
}

// When the user clicks on the button, scroll to the top of the document. This must come after window.onscroll, otherwise it will not work.
scrollTopButton.addEventListener("pointerdown", backToTop)

// inits
const copyButtonInit = copyButton()