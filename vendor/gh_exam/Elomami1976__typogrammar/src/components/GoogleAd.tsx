import React, { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

type Props = {
  adSlot: string
  style?: React.CSSProperties
  format?: string
  layout?: string
  fullWidthResponsive?: boolean
  adTest?: 'on' | 'off'
  // Reserve space to prevent CLS. Defaults to 90px (banner). Use 250 for
  // mid-content rectangles so Google's CLS audit doesn't penalise the page.
  minHeight?: number
}

const GoogleAd: React.FC<Props> = ({
  adSlot,
  style,
  format = 'auto',
  layout,
  fullWidthResponsive = true,
  adTest,
  minHeight = 90,
}) => {
  const adRef = useRef<HTMLModElement>(null)
  const location = useLocation()

  useEffect(() => {
    const timer = setTimeout(() => {
      if (adRef.current) {
        try {
          const hasAdStatus = adRef.current.getAttribute('data-ad-status')
          const hasAdLoaded = adRef.current.getAttribute('data-adsbygoogle-status')

          if (!hasAdStatus && !hasAdLoaded) {
            ;(window as any).adsbygoogle = (window as any).adsbygoogle || []
            ;(window as any).adsbygoogle.push({})
          }
        } catch (e) {
          // Silently handle AdSense errors
        }
      }
    }, 6500)

    return () => clearTimeout(timer)
  }, [location.pathname])

  const attrs: any = {
    className: 'adsbygoogle',
    style: style || (layout === 'in-article' ? { display: 'block', textAlign: 'center' } : format === 'auto' ? { display: 'block' } : undefined),
    'data-ad-client': 'ca-pub-4709657806016589',
    'data-ad-slot': adSlot,
  }
  if (layout) attrs['data-ad-layout'] = layout
  if (format) attrs['data-ad-format'] = format
  if (!layout && fullWidthResponsive) attrs['data-full-width-responsive'] = 'true'
  if (adTest) attrs['data-adtest'] = adTest

  return (
    // Reserved slot prevents layout shift (CLS) while the ad loads.
    // min-height keeps space even before the AdSense iframe is injected.
    <div style={{ minHeight: `${minHeight}px`, width: '100%' }}>
      <ins ref={adRef} {...attrs} key={`${adSlot}-${location.pathname}`} />
    </div>
  )
}

export default GoogleAd
