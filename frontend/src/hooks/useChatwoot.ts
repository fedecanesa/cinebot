import { useEffect } from 'react';

export function useChatwoot() {
  useEffect(() => {
    const baseUrl = import.meta.env.VITE_CHATWOOT_BASE_URL;
    const websiteToken = import.meta.env.VITE_CHATWOOT_WEBSITE_TOKEN;

    // Si no está configurado, salir silenciosamente
    if (!baseUrl || !websiteToken || websiteToken === 'YOUR_WEBSITE_TOKEN_HERE') {
      console.warn('Chatwoot not configured. Please set VITE_CHATWOOT_BASE_URL and VITE_CHATWOOT_WEBSITE_TOKEN');
      return;
    }

    // Configurar Chatwoot
    (window as any).chatwootSettings = {
      position: 'right',
      hideMessageBubble: false,
      showPopoutButton: true,
    };

    // Cargar el script de Chatwoot
    const script = document.createElement('script');
    script.src = `${baseUrl}/packs/js/sdk.js`;
    script.async = true;
    script.onload = () => {
      // Inicializar Chatwoot después de que el script cargue
      if ((window as any).chatwootSDK) {
        (window as any).chatwootSDK.run({
          websiteToken: websiteToken,
          baseUrl: baseUrl,
        });
      }
    };
    script.onerror = () => {
      console.error('Failed to load Chatwoot script');
    };

    document.head.appendChild(script);

    return () => {
      // Limpiar el script cuando el componente se desmonte
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);
}
