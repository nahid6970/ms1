Number.prototype.pad = function(n) {
  for (var r = this.toString(); r.length < n; r = 0 + r);
  return r;
};

function updateClock() {
  var now = new Date();
  var sec = now.getSeconds(),
    min = now.getMinutes(),
    hou = now.getHours(),
    mo = now.getMonth(),
    dy = now.getDate(),
    yr = now.getFullYear();
  var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var tags = ["mon", "d", "y", "h", "m", "s"], // Removed "mi" from tags
    corr = [months[mo], dy, yr, (hou % 12 || 12).pad(2), min.pad(2), sec.pad(2)]; // Adjusted hours to 12-hour format, removed milliseconds
  for (var i = 0; i < tags.length; i++)
    document.getElementById(tags[i]).firstChild.nodeValue = corr[i];
  
  // Add AM/PM
  document.getElementById("ampm").firstChild.nodeValue = hou >= 12 ? "PM" : "AM";
}

function initClock() {
  updateClock();
  window.setInterval("updateClock()", 1);
}
