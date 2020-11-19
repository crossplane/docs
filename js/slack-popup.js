(function () {
  function setDismissed() {
    window.localStorage.setItem('dismissedSlackPopup', 'true');
  }

  function checkDismissed() {
    return window.localStorage.getItem('dismissedSlackPopup') === 'true';
  }

  function handleEscapeKey(e) {
    if (e.key === 'Escape') {
      hidePopup();
    }
  }

  function hidePopup() {
    document.removeEventListener('keydown', handleEscapeKey);
  
    // IE fix
    document.querySelector('.slack-popup-container').innerHTML = '';
  
    if (document.querySelector('.slack-popup-container') !== null) {
      document.querySelector('.slack-popup-container').remove();
    }

    if (document.querySelector('.modal-overlay') !== null) {
      document.querySelector('.modal-overlay').remove();
    }
  }

  function showPopup() {
    if (document.querySelector('.modal-overlay') === null) {
      var overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.onclick = function () {
        hidePopup();
      };
      document.querySelector('body').appendChild(overlay);
    }

    if (document.querySelector('.slack-popup-container') === null) {
      var popup = document.createElement('div');
      popup.role = 'dialog';
      popup.tabIndex = '-1';
      popup.className = 'slack-popup-container';

      var popupHeader = document.createElement('div');
      popupHeader.className = 'slack-popup-header';

      var truckImage = document.createElement('img');
      truckImage.alt = 'Crossplane truck';
      truckImage.className = 'slack-popup-truck';
      truckImage.src = '/images/crossplane-truck.svg';

      popupHeader.appendChild(truckImage);
      popup.appendChild(popupHeader);

      var popupBody = document.createElement('div');
      popupBody.className = 'slack-popup-body';

      var slackLogo = document.createElement('img');
      slackLogo.src = '/images/slack-logo.svg';

      var headerText = document.createElement('h2');
      headerText.innerText = 'Get answers quick on our Slack channel';

      var bodyText = document.createElement('p');
      bodyText.innerText =
        'Hi there! Did you know we have an official Slack Channel? It’s the easiest way to get help and when you join you will be directly connected with our vibrant community.';

      var btnWrap = document.createElement('div');
      btnWrap.className = 'slack-popup-btn-wrapper';

      var ctaBtn = document.createElement('a');
      ctaBtn.classList.add('slack-popup-button', 'slack-popup-cta');
      ctaBtn.href = 'https://slack.crossplane.io/?utm_campaign=Slack%20Membership&utm_source=Crossplane%20Website%20Popup&utm_medium=popup&utm_content=popup';
      ctaBtn.innerHTML = '<img src="/images/slack-white.svg" /><span>Join Crossplane Slack</span>';

      var dismissBtn = document.createElement('a');
      dismissBtn.classList.add('slack-popup-button', 'slack-popup-dismiss');
      dismissBtn.innerText = 'I’m not interested in joining';
      dismissBtn.onclick = function () {
        hidePopup();
      };

      btnWrap.appendChild(ctaBtn);
      btnWrap.appendChild(dismissBtn);

      var popupStyles = document.createElement('style');
      popupStyles.innerHTML =
        '.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background-color:rgba(23,43,77,.45);z-index:100}.slack-popup-container{position:fixed;z-index:110;width:500px;height:600px;left:50%;top:50%;background:#fff;border-radius:10px;transform:translate(-50%,-50%);box-shadow:rgba(80,90,114,.7) 0 2px 5px 0;outline:0;color:#183d54}.slack-popup-container .slack-popup-header{height:147px;background-color:#183d54;position:relative;border-radius: 10px 10px 0 0;}.slack-popup-container .slack-popup-truck{width:231px;height:212px;position:absolute;top:-50px;left:50%;margin-left:-115.5px}.slack-popup-container .slack-popup-body{padding:40px}.slack-popup-container .slack-popup-body>img{width:138px;height:36px}.slack-popup-container .slack-popup-body{text-align:center}.slack-popup-container .slack-popup-body h2{line-height:40px;margin-top:20px;font-weight:900}.slack-popup-container .slack-popup-body p{font-size:16px;line-height:30px}.slack-popup-container .slack-popup-btn-wrapper .slack-popup-button{display:block;width:300px;cursor:pointer;border-radius:20px;padding:10px 0;text-decoration:none}.slack-popup-container .slack-popup-btn-wrapper .slack-popup-cta{background:#3bbdc4;color:#fff;margin:0 auto 10px auto}.slack-popup-container .slack-popup-btn-wrapper .slack-popup-cta img{height:20px;width:20px;margin-right:15px;vertical-align:text-top}.slack-popup-container .slack-popup-btn-wrapper .slack-popup-dismiss{color:#929394;border:1px solid #dcdcde;margin:0 auto} @media (max-width:48em){.slack-popup-container{width:320px!important;height:390px!important}.slack-popup-container .slack-popup-header{height:70px!important}.slack-popup-container .slack-popup-header .slack-popup-truck{width:115px;height:106px;top:-25px;margin-left:-52.5px}.slack-popup-container .slack-popup-body{padding:20px}.slack-popup-container .slack-popup-body>img{width:80px!important;height:auto!important}.slack-popup-container .slack-popup-body h2{line-height:20px!important;margin-top:10px!important;font-size:20px}.slack-popup-container .slack-popup-body p{font-size:12px!important;line-height:21px!important}.slack-popup-container .slack-popup-body .slack-popup-btn-wrapper .slack-popup-button{width:220px;font-size:12px}.slack-popup-container .slack-popup-btn-wrapper .slack-popup-cta img{height:12px;width:12px;margin-right:10px}}';

      popupBody.appendChild(slackLogo);
      popupBody.appendChild(headerText);
      popupBody.appendChild(bodyText);
      popupBody.appendChild(btnWrap);
      popupBody.appendChild(popupStyles);
      popup.appendChild(popupBody);

      document.querySelector('body').appendChild(popup);

      document.addEventListener('keydown', handleEscapeKey);
    }
  }

  setTimeout(function () {
    if (!checkDismissed()) {
      showPopup();
      setDismissed();
    }
  }, 30000);
})();
