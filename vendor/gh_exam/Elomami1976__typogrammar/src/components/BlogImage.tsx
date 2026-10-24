import React, { useState } from 'react';

interface BlogImageProps {
  slug: string;
  fallbackUrl?: string;
  alt: string;
  className?: string;
  loading?: 'lazy' | 'eager';
  /** Hint for above-the-fold LCP images. Use 'high' for the hero. */
  fetchPriority?: 'high' | 'low' | 'auto';
  /** Intrinsic dimensions reserve layout space to prevent CLS. Defaults to a 1200x630 cover ratio. */
  width?: number;
  height?: number;
}

/**
 * BlogImage Component
 * Automatically tries to load local images from /images/blog/{slug}.{ext}
 * Falls back to external URL if provided, or shows placeholder
 * 
 * Supported formats: .jpg, .jpeg, .png, .webp
 */
const BlogImage: React.FC<BlogImageProps> = ({ 
  slug, 
  fallbackUrl, 
  alt, 
  className = '', 
  loading = 'lazy',
  fetchPriority = 'auto',
  width = 1200,
  height = 630,
}) => {
  const [imageSrc, setImageSrc] = useState<string>(`/images/blog/${slug}.jpg`);
  const [hasError, setHasError] = useState(false);

  const handleImageError = () => {
    if (!hasError) {
      // First error: try .png
      if (imageSrc.endsWith('.jpg')) {
        setImageSrc(`/images/blog/${slug}.png`);
        return;
      }
      
      // Second error: try .webp
      if (imageSrc.endsWith('.png')) {
        setImageSrc(`/images/blog/${slug}.webp`);
        return;
      }
      
      // Third error: try .jpeg
      if (imageSrc.endsWith('.webp')) {
        setImageSrc(`/images/blog/${slug}.jpeg`);
        return;
      }
      
      // Final fallback: use external URL or show nothing
      if (fallbackUrl) {
        setImageSrc(fallbackUrl);
      } else {
        setHasError(true);
      }
    }
  };

  // Don't render if all attempts failed and no fallback
  if (hasError && !fallbackUrl) {
    return null;
  }

  // Serve a smaller WebP sibling when the source is a local raster image.
  // Every /images raster has a generated .webp (see scripts/optimize-images.cjs);
  // browsers that lack WebP support (or a missing file) fall back to <img>.
  const isLocalRaster = /^\/images\/.*\.(jpe?g|png)$/i.test(imageSrc);
  const webpSrc = isLocalRaster ? imageSrc.replace(/\.(jpe?g|png)$/i, '.webp') : null;

  return (
    <picture className="contents">
      {webpSrc && <source srcSet={webpSrc} type="image/webp" />}
      <img
        src={imageSrc}
        alt={alt}
        className={className}
        loading={loading}
        fetchPriority={fetchPriority}
        width={width}
        height={height}
        decoding="async"
        onError={handleImageError}
      />
    </picture>
  );
};

export default BlogImage;
