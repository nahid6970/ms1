function skipAd() {
  const skipButton = document.querySelector('button.ytp-skip-ad-button.ytp-ad-component--clickable');
  if (skipButton) {
    skipButton.click();
  }
}

setInterval(skipAd, 1000); // Check for the ad button every second
