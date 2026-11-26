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

  // Default and custom dimensions
  const DEFAULT_WIDTH = 420;
  const DEFAULT_HEIGHT = 620;
  let customWidth = DEFAULT_WIDTH;
  let customHeight = DEFAULT_HEIGHT;
  let isMaximized = false;

  // Create Chat Window Card
  const chatCard = document.createElement("div");
  chatCard.id = "dsce-widget-card";
  chatCard.style.display = "none";
  chatCard.style.flexDirection = "column";
  chatCard.style.position = "absolute";
  chatCard.style.bottom = "68px";
  chatCard.style.right = "0";
  chatCard.style.width = `${DEFAULT_WIDTH}px`;
  chatCard.style.maxWidth = "calc(100vw - 32px)";
  chatCard.style.height = `${DEFAULT_HEIGHT}px`;
  chatCard.style.maxHeight = "calc(100vh - 96px)";
  chatCard.style.borderRadius = "16px";
  chatCard.style.overflow = "hidden";
  chatCard.style.boxShadow = "0 18px 45px rgba(15, 23, 42, 0.22), 0 0 0 1px rgba(226, 232, 240, 0.85)";
  chatCard.style.backgroundColor = "#ffffff";
  chatCard.style.transition = "width 0.2s ease, height 0.2s ease, transform 0.2s ease";

  // Drag-to-Resize Handle at top-left corner
  const resizeHandle = document.createElement("div");
  resizeHandle.id = "dsce-widget-resize-handle";
  resizeHandle.title = "Drag to adjust chatbot size";
  resizeHandle.style.position = "absolute";
  resizeHandle.style.top = "2px";
  resizeHandle.style.left = "2px";
  resizeHandle.style.width = "22px";
  resizeHandle.style.height = "22px";
  resizeHandle.style.cursor = "nwse-resize";
  resizeHandle.style.zIndex = "1000";
  resizeHandle.style.display = "flex";
  resizeHandle.style.alignItems = "center";
  resizeHandle.style.justifyContent = "center";
  resizeHandle.style.borderRadius = "4px";
  resizeHandle.innerHTML = `<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="rgba(255,255,255,0.75)" stroke-width="2"><path d="M1 11L11 1M1 6L6 1M1 1L1 1"/></svg>`;
  chatCard.appendChild(resizeHandle);

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
      #dsce-widget-resize-handle {
        display: none !important;
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

  // Interactive Drag-to-Resize Logic
  let isDraggingResize = false;
  let startX = 0, startY = 0, startWidth = 0, startHeight = 0;

  resizeHandle.addEventListener("mousedown", (e) => {
    if (isMaximized) return;
    isDraggingResize = true;
    startX = e.clientX;
    startY = e.clientY;
    startWidth = chatCard.offsetWidth;
    startHeight = chatCard.offsetHeight;
    iframe.style.pointerEvents = "none";
    document.body.style.userSelect = "none";
    document.body.style.cursor = "nwse-resize";
    e.preventDefault();
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDraggingResize) return;
    // Card is anchored at bottom-right, so dragging left increases width, dragging up increases height
    const deltaX = startX - e.clientX;
    const deltaY = startY - e.clientY;

    const minW = 360;
    const maxW = Math.min(1000, window.innerWidth - 32);
    const minH = 460;
    const maxH = Math.min(900, window.innerHeight - 90);

    const newW = Math.min(Math.max(minW, startWidth + deltaX), maxW);
    const newH = Math.min(Math.max(minH, startHeight + deltaY), maxH);

    customWidth = newW;
    customHeight = newH;
    chatCard.style.width = `${newW}px`;
    chatCard.style.height = `${newH}px`;
  });

  document.addEventListener("mouseup", () => {
    if (isDraggingResize) {
      isDraggingResize = false;
      iframe.style.pointerEvents = "auto";
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    }
  });

  // Size Preset Setter
  function setCardSize(w, h) {
    if (isMaximized) isMaximized = false;
    customWidth = Math.min(w, window.innerWidth - 32);
    customHeight = Math.min(h, window.innerHeight - 90);
    chatCard.style.width = `${customWidth}px`;
    chatCard.style.height = `${customHeight}px`;
    chatCard.style.maxWidth = "calc(100vw - 32px)";
    chatCard.style.maxHeight = "calc(100vh - 96px)";
    resizeHandle.style.display = "flex";
    notifyIframeState();
  }

  // Maximize / Restore Toggle
  function toggleMaximize() {
    isMaximized = !isMaximized;
    if (isMaximized) {
      chatCard.style.width = "min(960px, calc(100vw - 32px))";
      chatCard.style.height = "calc(100vh - 90px)";
      chatCard.style.maxWidth = "calc(100vw - 32px)";
      chatCard.style.maxHeight = "calc(100vh - 90px)";
      resizeHandle.style.display = "none";
    } else {
      chatCard.style.width = `${customWidth}px`;
      chatCard.style.height = `${customHeight}px`;
      chatCard.style.maxWidth = "calc(100vw - 32px)";
      chatCard.style.maxHeight = "calc(100vh - 96px)";
      resizeHandle.style.display = "flex";
    }
    notifyIframeState();
  }

  function notifyIframeState() {
    try {
      iframe.contentWindow.postMessage({
        type: "DSCE_MAXIMIZE_STATE",
        isMaximized: isMaximized
      }, "*");
    } catch (e) {}
  }

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

  // Cross-frame message handler from iframe inside the widget
  window.addEventListener("message", (e) => {
    if (!e.data || !e.data.type) return;
    if (e.data.type === "DSCE_TOGGLE_MAXIMIZE") {
      toggleMaximize();
    } else if (e.data.type === "DSCE_MINIMIZE") {
      closeWidget();
    } else if (e.data.type === "DSCE_SET_SIZE") {
      if (e.data.size === "S") setCardSize(380, 520);
      else if (e.data.size === "M") setCardSize(440, 620);
      else if (e.data.size === "L") setCardSize(640, 720);
    }
  });

  // Global helper for opening the assistant from any link or button on the website
  window.openDsceAssistant = function (query = null) {
    openWidget(query);
  };

  container.appendChild(chatCard);
  container.appendChild(callout);
  container.appendChild(btn);
  document.body.appendChild(container);
})();
