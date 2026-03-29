const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() || '';
const browserOrigin = window.location.origin;
const isLikelyViteDevServer =
    /^(http:\/\/127\.0\.0\.1:517[0-9]|http:\/\/localhost:517[0-9]|http:\/\/127\.0\.0\.1:4173|http:\/\/localhost:4173)$/.test(
        browserOrigin
    );

// In dev, use empty string so requests go through Vite proxy (relative URLs)
// In production, use the configured base URL or the browser origin
const resolvedBaseUrl = configuredBaseUrl
    ? configuredBaseUrl
    : isLikelyViteDevServer
      ? ''
      : browserOrigin;

export const apiConfig = {
    baseUrl: resolvedBaseUrl,
    videosBaseUrl: `${resolvedBaseUrl}/api/v1/videos`,
};
