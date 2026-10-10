// SPDX-License-Identifier: MIT; Copyright (c) 2026 William Qiu
"use strict";
const searchInput = document.getElementById("search");
const rows = Array.from(document.querySelectorAll(".term-row"));
const groups = Array.from(document.querySelectorAll(".letter-group"));
const count = document.getElementById("result-count");
const empty = document.getElementById("no-results");
function updateSearch() {
  const tokens = searchInput.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const row of rows) {
    row.hidden = !tokens.every(token => row.dataset.search.includes(token));
    if (!row.hidden) visible++;
  }
  for (const group of groups) {
    group.hidden = !Array.from(group.querySelectorAll(".term-row")).some(row => !row.hidden);
  }
  count.textContent = visible + (visible === 1 ? " term" : " terms") + (tokens.length ? " found" : "");
  empty.hidden = visible !== 0;
}
searchInput.addEventListener("input", updateSearch);
document.getElementById("clear-search").addEventListener("click", () => {
  searchInput.value = "";
  updateSearch();
  searchInput.focus();
});
