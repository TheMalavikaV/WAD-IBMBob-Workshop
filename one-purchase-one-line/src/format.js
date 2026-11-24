'use strict';

/** 79900 -> "Rs.799.00". Amounts are always integer paise (1 rupee = 100 paise). */
function formatPaise(paise) {
  const sign = paise < 0 ? '-' : '';
  const abs = Math.abs(paise);
  const rupees = Math.floor(abs / 100).toLocaleString('en-IN');
  const rest = String(abs % 100).padStart(2, '0');
  return `${sign}Rs.${rupees}.${rest}`;
}

/** "2026-11-03T19:02:11Z" -> "3 Nov 2026, 19:02 UTC" */
function formatTime(iso) {
  const d = new Date(iso);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const hh = String(d.getUTCHours()).padStart(2, '0');
  const mm = String(d.getUTCMinutes()).padStart(2, '0');
  return `${d.getUTCDate()} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()}, ${hh}:${mm} UTC`;
}

module.exports = { formatPaise, formatTime };
