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
  chatCard.style.width = "420px";
  chatCard.style.maxWidth = "calc(100vw - 32px)";
  chatCard.style.height = "620px";
  chatCard.style.maxHeight = "calc(100vh - 96px)";
  chatCard.style.borderRadius = "16px";
  chatCard.style.overflow = "hidden";
  chatCard.style.boxShadow = "0 18px 45px rgba(15, 23, 42, 0.22), 0 0 0 1px rgba(226, 232, 240, 0.85)";
  chatCard.style.backgroundColor = "#ffffff";
  chatCard.style.transition = "all 0.22s cubic-bezier(0.16, 1, 0.3, 1)";

  // Responsive styling for small mobile screens
  const responsiveStyle = document.createElement("style");
  responsiveStyle.textContent = `
    @media (max-width: 480px) {
      #dsce-widget-container {
        bottom: 16px !important;
        right: 16px !important;
      }
      #dsce-widget-card {
        position: fixed !important;
        bottom: 80px !important;
        right: 12px !important;
        left: 12px !important;
        width: auto !important;
        max-width: none !important;
        height: calc(100vh - 96px) !important;
        max-height: none !important;
        border-radius: 14px !important;
      }
    }
  `;
  document.head.appendChild(responsiveStyle);

  // Iframe loading the chat interface in compact embedded mode
  const iframe = document.createElement("iframe");
  iframe.id = "dsce-widget-iframe";
  iframe.src = `${scriptOrigin}/chat?embed=true`;
  iframe.style.width = "100%";
  iframe.style.height = "100%";
  iframe.style.border = "none";
  iframe.title = "DSCE Campus Assistant";

  chatCard.appendChild(iframe);

  // Callout Prompt Bubble
  const callout = document.createElement("div");
  callout.id = "dsce-widget-callout";
  callout.style.position = "absolute";
  callout.style.bottom = "12px";
  callout.style.right = "68px";
  callout.style.background = "#ffffff";
  callout.style.color = "#0f172a";
  callout.style.padding = "8px 14px";
  callout.style.borderRadius = "20px";
  callout.style.fontSize = "13px";
  callout.style.fontWeight = "600";
  callout.style.whiteSpace = "nowrap";
  callout.style.boxShadow = "0 8px 24px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(226, 232, 240, 0.8)";
  callout.style.cursor = "pointer";
  callout.style.display = "flex";
  callout.style.alignItems = "center";
  callout.style.gap = "6px";
  callout.style.transition = "all 0.25s ease";
  callout.innerHTML = `<span>💬</span> <span>Ask DSCE AI: 2026-27 Fees & Hostels</span>`;

  callout.onclick = () => {
    openWidget();
  };

  // Toggle Functionality
  let isOpen = false;
  function openWidget(queryToAsk = null) {
    isOpen = true;
    chatCard.style.display = "flex";
    callout.style.display = "none";
    btn.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;
    
    if (queryToAsk) {
      setTimeout(() => {
        try {
          iframe.contentWindow.postMessage({
            type: "DSCE_ASK_QUESTION",
            query: queryToAsk
          }, "*");
        } catch (e) {}
      }, 350);
    }
  }

  function closeWidget() {
    isOpen = false;
    chatCard.style.display = "none";
    btn.innerHTML = `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
  }

  btn.onclick = () => {
    if (isOpen) {
      closeWidget();
    } else {
      openWidget();
    }
  };

  // Global helper for opening the assistant from any link or button on the website
  window.openDsceAssistant = function (query = null) {
    openWidget(query);
  };

  container.appendChild(chatCard);
  container.appendChild(callout);
  container.appendChild(btn);
  document.body.appendChild(container);
})();
