/**
 * DSCE Campus Assistant - Embeddable Floating Chat Widget
 * Usage:
 *   <script src="https://your-domain.com/static/widget.js"></script>
 */

(function () {
  // Determine base URL from current script tag
  let scriptOrigin = window.location.origin;
  const currentScript = document.currentScript;
  if (currentScript && currentScript.src) {
    try {
      const url = new URL(currentScript.src);
      scriptOrigin = url.origin;
    } catch (e) {}
  }

  // Prevent multiple injections
  if (document.getElementById("dsce-widget-container")) return;

  // Create Container
  const container = document.createElement("div");
  container.id = "dsce-widget-container";
  container.style.position = "fixed";
  container.style.bottom = "24px";
  container.style.right = "24px";
  container.style.zIndex = "999999";
  container.style.fontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

  // Create Floating Action Button
  const btn = document.createElement("button");
  btn.id = "dsce-widget-btn";
  btn.setAttribute("aria-label", "Open DSCE Campus Assistant");
  btn.style.width = "56px";
  btn.style.height = "56px";
  btn.style.borderRadius = "28px";
  btn.style.backgroundColor = "#0284c7";
  btn.style.backgroundImage = "linear-gradient(135deg, #0284c7, #0369a1)";
  btn.style.color = "#ffffff";
  btn.style.border = "none";
  btn.style.boxShadow = "0 8px 24px rgba(2, 132, 199, 0.4)";
  btn.style.cursor = "pointer";
  btn.style.display = "flex";
  btn.style.alignItems = "center";
  btn.style.justifyContent = "center";
  btn.style.fontSize = "22px";
  btn.style.transition = "all 0.25s cubic-bezier(0.16, 1, 0.3, 1)";
  btn.innerHTML = `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;

  btn.onmouseenter = () => {
    btn.style.transform = "scale(1.08)";
    btn.style.boxShadow = "0 10px 28px rgba(2, 132, 199, 0.5)";
  };
  btn.onmouseleave = () => {
    btn.style.transform = "scale(1)";
    btn.style.boxShadow = "0 8px 24px rgba(2, 132, 199, 0.4)";
  };

  // Create Chat Window Card
  const chatCard = document.createElement("div");
  chatCard.id = "dsce-widget-card";
  chatCard.style.display = "none";
  chatCard.style.flexDirection = "column";
  chatCard.style.position = "absolute";
  chatCard.style.bottom = "68px";
  chatCard.style.right = "0";
  chatCard.style.width = "400px";
  chatCard.style.maxWidth = "calc(100vw - 48px)";
  chatCard.style.height = "580px";
  chatCard.style.maxHeight = "calc(100vh - 120px)";
  chatCard.style.borderRadius = "16px";
  chatCard.style.overflow = "hidden";
  chatCard.style.boxShadow = "0 16px 40px rgba(15, 23, 42, 0.2), 0 0 0 1px rgba(226, 232, 240, 0.8)";
  chatCard.style.backgroundColor = "#ffffff";
  chatCard.style.transition = "opacity 0.2s ease, transform 0.2s ease";

  // Iframe loading the chat interface in compact embedded mode
  const iframe = document.createElement("iframe");
  iframe.src = `${scriptOrigin}/?embed=true`;
  iframe.style.width = "100%";
  iframe.style.height = "100%";
  iframe.style.border = "none";
  iframe.title = "DSCE Campus Assistant";

  chatCard.appendChild(iframe);

  // Toggle Functionality
  let isOpen = false;
  btn.onclick = () => {
    isOpen = !isOpen;
    if (isOpen) {
      chatCard.style.display = "flex";
      btn.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;
    } else {
      chatCard.style.display = "none";
      btn.innerHTML = `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
    }
  };

  container.appendChild(chatCard);
  container.appendChild(btn);
  document.body.appendChild(container);
})();
