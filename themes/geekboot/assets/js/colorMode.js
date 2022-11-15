/*!
 * Dark Mode Switch v1.0.1 (https://github.com/coliff/dark-mode-switch)
 * Copyright 2021 C.Oliff
 * Licensed under MIT (https://github.com/coliff/dark-mode-switch/blob/main/LICENSE)
 */

(() => {
    var darkSwitch = document.getElementById("darkSwitch");
    window.addEventListener("load", function () {
      if (darkSwitch) {
          initTheme();
          darkSwitch.addEventListener("change", function () {
            resetTheme();
          });
      }
    });
})();
/**
 * Summary: function that adds or removes the attribute 'color-theme' depending if
 * the switch is 'on' or 'off'.
 *
 * Description: initTheme is a function that uses localStorage from JavaScript DOM,
 * to store the value of the HTML switch. If the switch was already switched to
 * 'on' it will set an HTML attribute to the body named: 'color-theme' to a 'dark'
 * value. If it is the first time opening the page, or if the switch was off the
 * 'color-theme' attribute will not be set.
 * @return {void}
 */
function initTheme() {
  var darkThemeSelected =
    localStorage.getItem("darkSwitch") !== null &&
    localStorage.getItem("darkSwitch") === "dark";
  darkSwitch.checked = darkThemeSelected;
  darkThemeSelected
    ? document.documentElement.setAttribute("color-theme", "dark")
    : document.documentElement.removeAttribute("color-theme");
}

/**
 * Summary: resetTheme checks if the switch is 'on' or 'off' and if it is toggled
 * on it will set the HTML attribute 'color-theme' to dark so the dark-theme CSS is
 * applied.
 * @return {void}
 */
function resetTheme() {
  if (darkSwitch.checked) {
    document.documentElement.setAttribute("color-theme", "dark");
    localStorage.setItem("darkSwitch", "dark");
  } else {
    document.documentElement.removeAttribute("color-theme", "light");
    localStorage.removeItem("darkSwitch");
  }
}