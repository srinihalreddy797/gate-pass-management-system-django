(() => {
  const isModifiedClick = (event) =>
    event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0;

  const shouldSkipLink = (link) => {
    if (!link) return true;
    if (link.hasAttribute("download")) return true;
    if (link.hasAttribute("target") && link.getAttribute("target") !== "_self") return true;
    if (link.closest("[data-no-transition]")) return true;

    const href = link.getAttribute("href");
    if (!href) return true;
    if (
      href.startsWith("#") ||
      href.startsWith("mailto:") ||
      href.startsWith("tel:") ||
      href.startsWith("javascript:")
    ) {
      return true;
    }

    let url;
    try {
      url = new URL(href, window.location.href);
    } catch {
      return true;
    }

    if (url.origin !== window.location.origin) return true;
    if (url.pathname === window.location.pathname && url.hash) return true;

    return false;
  };

  const fadeInOnLoad = () => {
    document.body.classList.add("is-transitioning-in");
    window.requestAnimationFrame(() => {
      document.body.classList.remove("is-transitioning-in");
    });
  };

  const navigateWithTransition = (url) => {
    const go = () => {
      window.location.href = url;
    };

    if (document.startViewTransition) {
      document.body.classList.add("is-transitioning-out");
      const transition = document.startViewTransition(() => {
        go();
      });

      transition.finished.finally(() => {
        document.body.classList.remove("is-transitioning-out");
      });

      return;
    }

    document.body.classList.add("is-transitioning");
    window.setTimeout(go, 220);
  };

  document.addEventListener("click", (event) => {
    if (isModifiedClick(event)) return;

    const link = event.target.closest("a");
    if (!link || shouldSkipLink(link)) return;

    const href = link.getAttribute("href");
    const url = new URL(href, window.location.href);
    if (url.href === window.location.href) return;

    event.preventDefault();
    navigateWithTransition(url.href);
  });

  window.addEventListener("pageshow", fadeInOnLoad);
})();
