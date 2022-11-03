import { applyTheme } from "./colorTheme";
import { clipboardListener } from "./clipboardEventListener";
import { getKeywords } from "./hover-highlight-element.js";

(() => {
  applyTheme();
  clipboardListener();
  getKeywords();
})();
