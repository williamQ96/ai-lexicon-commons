/* SPDX-License-Identifier: MIT; Copyright (c) 2026 William Qiu */
"use strict";

// Query and appearance stay within this tab; search never contacts a server.
const indexPath = new URL(document.body.dataset.indexUrl, location.href).pathname;
const storagePrefix = "plale-glossary:" + indexPath + ":";
function remember(key, value) {
  try { sessionStorage.setItem(storagePrefix + key, value); } catch { /* Storage is optional. */ }
}
function recall(key) {
  try { return sessionStorage.getItem(storagePrefix + key) || ""; } catch { return ""; }
}
const themeButton = document.getElementById("theme-toggle");
const preferredScheme = matchMedia("(prefers-color-scheme: dark)");
function applyTheme(theme) {
  if (theme) document.documentElement.dataset.theme = theme;
  else delete document.documentElement.dataset.theme;
  const dark = theme === "dark" || (!theme && preferredScheme.matches);
  themeButton.textContent = dark ? "Light" : "Dark";
  themeButton.setAttribute("aria-label", dark ? "Switch to light appearance" : "Switch to dark appearance");
}
if (themeButton) {
  applyTheme(recall("theme"));
  themeButton.hidden = false;
  themeButton.addEventListener("click", () => {
    const theme = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme && preferredScheme.matches) ? "light" : "dark";
    remember("theme", theme);
    applyTheme(theme);
  });
  preferredScheme.addEventListener("change", () => applyTheme(recall("theme")));
}
const searchInput = document.getElementById("search");
if (searchInput) {
  const items = [...document.querySelectorAll(".index-item")];
  const rows = [...document.querySelectorAll(".term-row")];
  const groups = [...document.querySelectorAll(".letter-group")];
  const count = document.getElementById("result-count");
  const empty = document.getElementById("no-results");
  const catalog = document.getElementById("term-catalog");
  const mobile = matchMedia("(max-width: 767px)");
  function updateSearch() {
    const tokens = searchInput.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const matches = item => tokens.every(token => item.dataset.search.includes(token));
    for (const item of [...items, ...rows]) item.hidden = !matches(item);
    for (const group of groups) group.hidden = [...group.querySelectorAll(".term-row")].every(row => row.hidden);
    const visible = items.filter(item => !item.hidden).length;
    count.textContent = tokens.length ? visible + " of " + items.length + " terms found" : items.length + " terms";
    empty.hidden = visible !== 0;
    for (const link of document.querySelectorAll(".alphabet a")) {
      link.hidden = document.getElementById(link.hash.slice(1)).hidden;
    }
    remember("query", searchInput.value);
    if (tokens.length) catalog.open = true;
  }
  function syncCatalog() { catalog.open = !mobile.matches || Boolean(searchInput.value.trim()); }
  searchInput.value = recall("query");
  updateSearch();
  syncCatalog();
  searchInput.addEventListener("input", updateSearch);
  document.getElementById("clear-search").addEventListener("click", () => {
    searchInput.value = "";
    updateSearch();
    searchInput.focus();
  });
  mobile.addEventListener("change", syncCatalog);
}
