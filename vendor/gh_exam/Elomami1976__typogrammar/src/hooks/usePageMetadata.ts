import { useEffect } from 'react';

interface PageMetadata {
  title?: string;
  description?: string;
  canonical?: string;
  robots?: string;
  ogTitle?: string;
  ogDescription?: string;
  ogUrl?: string;
  ogImage?: string;
  ogType?: string;
  twitterCard?: string;
  twitterTitle?: string;
  twitterDescription?: string;
  twitterImage?: string;
}

const SITE_URL = 'https://typogrammar.com';
const DEFAULT_OG_IMAGE = 'https://typogrammar.com/og-default.png';
const DESCRIPTION_SELECTOR = 'meta[name="description"]';
const ROBOTS_SELECTOR = 'meta[name="robots"]';
const CANONICAL_SELECTOR = 'link[rel="canonical"]';
const MAX_DESCRIPTION_LENGTH = 160;

const truncateDescription = (text: string): string => {
  const trimmed = text.trim().replace(/\s+/g, ' ');
  if (trimmed.length <= MAX_DESCRIPTION_LENGTH) return trimmed;
  const cut = trimmed.slice(0, MAX_DESCRIPTION_LENGTH - 1);
  const lastSpace = cut.lastIndexOf(' ');
  const base = lastSpace > 100 ? cut.slice(0, lastSpace) : cut;
  return base.replace(/[\s,;:.\-]+$/, '') + '…';
};

const normalizeCanonicalPath = (path: string): string => {
  let cleanPath = path.split('?')[0].split('#')[0];
  if (cleanPath === '/') return cleanPath;
  if (!cleanPath.endsWith('/')) {
    cleanPath = cleanPath + '/';
  }
  return cleanPath;
};

const normalizeCanonicalUrl = (rawUrl: string): string => {
  try {
    const u = new URL(rawUrl);
    u.search = '';
    u.hash = '';
    if (u.pathname !== '/' && !u.pathname.endsWith('/')) {
      u.pathname = u.pathname + '/';
    }
    return u.toString();
  } catch {
    const noQuery = rawUrl.split('?')[0].split('#')[0];
    if (noQuery.endsWith('/')) return noQuery;
    return noQuery + '/';
  }
};

const getMetaContent = (selector: string, isProperty = false): string | undefined => {
  const el = document.querySelector<HTMLMetaElement>(
    isProperty ? `meta[property="${selector}"]` : `meta[name="${selector}"]`
  );
  return el?.getAttribute('content') ?? undefined;
};

const setMetaTag = (property: string, content: string, isProperty = false) => {
  const selector = isProperty ? `meta[property="${property}"]` : `meta[name="${property}"]`;
  let meta = document.querySelector<HTMLMetaElement>(selector);
  if (!meta) {
    meta = document.createElement('meta');
    if (isProperty) {
      meta.setAttribute('property', property);
    } else {
      meta.setAttribute('name', property);
    }
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
  return meta;
};

const restoreMetaTag = (property: string, previous: string | undefined, isProperty = false) => {
  const selector = isProperty ? `meta[property="${property}"]` : `meta[name="${property}"]`;
  const meta = document.querySelector<HTMLMetaElement>(selector);
  if (!meta) return;
  if (previous !== undefined) {
    meta.setAttribute('content', previous);
  } else {
    document.head.removeChild(meta);
  }
};

export default function usePageMetadata({
  title,
  description,
  canonical,
  robots,
  ogTitle,
  ogDescription,
  ogUrl,
  ogImage,
  ogType,
  twitterCard,
  twitterTitle,
  twitterDescription,
  twitterImage
}: PageMetadata) {
  useEffect(() => {
    // Snapshot previous values so cleanup can restore them
    const previousTitle = document.title;
    const previousDescription = getMetaContent(DESCRIPTION_SELECTOR.replace('meta[name="', '').replace('"]', ''));
    const previousRobots = getMetaContent('robots');
    const canonicalEl = document.querySelector<HTMLLinkElement>(CANONICAL_SELECTOR);
    const previousCanonical = canonicalEl?.getAttribute('href') ?? undefined;
    const previousOgTitle = getMetaContent('og:title', true);
    const previousOgDescription = getMetaContent('og:description', true);
    const previousOgImage = getMetaContent('og:image', true);
    const previousOgType = getMetaContent('og:type', true);
    const previousOgUrl = getMetaContent('og:url', true);
    const previousTwitterCard = getMetaContent('twitter:card');
    const previousTwitterTitle = getMetaContent('twitter:title');
    const previousTwitterDescription = getMetaContent('twitter:description');
    const previousTwitterImage = getMetaContent('twitter:image');

    // --- title ---
    if (title) document.title = title;

    // --- description ---
    if (description) {
      let meta = document.querySelector<HTMLMetaElement>(DESCRIPTION_SELECTOR);
      if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute('name', 'description');
        document.head.appendChild(meta);
      }
      meta.setAttribute('content', truncateDescription(description));
    }

    // --- canonical (always set) ---
    const normalizedPath = normalizeCanonicalPath(window.location.pathname);
    const canonicalUrl = canonical
      ? normalizeCanonicalUrl(canonical)
      : `${SITE_URL}${normalizedPath}`;
    let link = canonicalEl;
    if (!link) {
      link = document.createElement('link');
      link.setAttribute('rel', 'canonical');
      document.head.appendChild(link);
    }
    link.setAttribute('href', canonicalUrl);

    // --- robots ---
    const robotsContent = robots || 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1';
    let robotsMeta = document.querySelector<HTMLMetaElement>(ROBOTS_SELECTOR);
    if (!robotsMeta) {
      robotsMeta = document.createElement('meta');
      robotsMeta.setAttribute('name', 'robots');
      document.head.appendChild(robotsMeta);
    }
    robotsMeta.setAttribute('content', robotsContent);

    // --- Open Graph: derive from title/description when not explicitly provided ---
    const effectiveOgTitle = ogTitle || title;
    const effectiveOgDescription = ogDescription || description;
    const effectiveOgImage = ogImage || DEFAULT_OG_IMAGE;
    const effectiveOgType = ogType || 'website';
    const effectiveOgUrl = ogUrl ? normalizeCanonicalUrl(ogUrl) : canonicalUrl;

    if (effectiveOgTitle) setMetaTag('og:title', effectiveOgTitle, true);
    if (effectiveOgDescription) setMetaTag('og:description', truncateDescription(effectiveOgDescription), true);
    setMetaTag('og:url', effectiveOgUrl, true);
    setMetaTag('og:image', effectiveOgImage, true);
    setMetaTag('og:type', effectiveOgType, true);

    // --- Twitter Card: derive from OG/title/description when not explicitly provided ---
    const effectiveTwitterCard = twitterCard || 'summary_large_image';
    const effectiveTwitterTitle = twitterTitle || effectiveOgTitle;
    const effectiveTwitterDescription = twitterDescription || effectiveOgDescription;
    const effectiveTwitterImage = twitterImage || effectiveOgImage;

    setMetaTag('twitter:card', effectiveTwitterCard);
    if (effectiveTwitterTitle) setMetaTag('twitter:title', effectiveTwitterTitle);
    if (effectiveTwitterDescription) setMetaTag('twitter:description', truncateDescription(effectiveTwitterDescription));
    setMetaTag('twitter:image', effectiveTwitterImage);

    return () => {
      if (title) document.title = previousTitle;

      if (description) {
        const meta = document.querySelector<HTMLMetaElement>(DESCRIPTION_SELECTOR);
        if (meta) {
          if (previousDescription !== undefined) {
            meta.setAttribute('content', previousDescription);
          } else {
            document.head.removeChild(meta);
          }
        }
      }

      // Restore canonical
      const linkEl = document.querySelector<HTMLLinkElement>(CANONICAL_SELECTOR);
      if (linkEl && previousCanonical !== undefined) {
        linkEl.setAttribute('href', previousCanonical);
      }

      if (robots) {
        const meta = document.querySelector<HTMLMetaElement>(ROBOTS_SELECTOR);
        if (meta) {
          if (previousRobots !== undefined) {
            meta.setAttribute('content', previousRobots);
          } else {
            document.head.removeChild(meta);
          }
        }
      }

      // Restore OG tags
      if (effectiveOgTitle) restoreMetaTag('og:title', previousOgTitle, true);
      if (effectiveOgDescription) restoreMetaTag('og:description', previousOgDescription, true);
      restoreMetaTag('og:url', previousOgUrl, true);
      restoreMetaTag('og:image', previousOgImage, true);
      restoreMetaTag('og:type', previousOgType, true);

      // Restore Twitter tags
      restoreMetaTag('twitter:card', previousTwitterCard);
      if (effectiveTwitterTitle) restoreMetaTag('twitter:title', previousTwitterTitle);
      if (effectiveTwitterDescription) restoreMetaTag('twitter:description', previousTwitterDescription);
      restoreMetaTag('twitter:image', previousTwitterImage);
    };
  }, [title, description, canonical, robots, ogTitle, ogDescription, ogUrl, ogImage, ogType, twitterCard, twitterTitle, twitterDescription, twitterImage]);
}
