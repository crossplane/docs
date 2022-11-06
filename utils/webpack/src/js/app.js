import { clipboardListener } from "./clipboardEventListener";
import { getKeywords } from "./hover-highlight-element.js";

(() => {
  clipboardListener();
  getKeywords();
})();
