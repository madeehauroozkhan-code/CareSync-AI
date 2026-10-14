import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import "leaflet/dist/leaflet.css";
 
// FIX: browsers automatically remember and restore scroll position across
// reloads for the same page. That's what was causing the dashboard to
// "start halfway down" after a refresh -- the browser was restoring the
// scroll position from before the reload, which looked broken because the
// page content had also changed in the meantime (new cases loaded in above
// where you were scrolled to). Disabling this makes every reload start
// cleanly at the top, which is what you want for a live dashboard.
if ("scrollRestoration" in window.history) {
  window.history.scrollRestoration = "manual";
}
window.scrollTo(0, 0);
 
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
