import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface CachedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallback?: React.ReactNode;
}

export function CachedImage({ src, alt, className, fallback, ...props }: CachedImageProps) {
  const [status, setStatus] = useState<'loading' | 'loaded' | 'error'>('loading');

  useEffect(() => {
    setStatus('loading');
    if (!src) {
      setStatus('error');
      return;
    }

    const img = new Image();
    img.src = src;
    img.onload = () => setStatus('loaded');
    img.onerror = () => setStatus('error');
  }, [src]);

  if (status === 'error') {
    return fallback ? <>{fallback}</> : null;
  }

  return (
    <div className={cn("relative overflow-hidden", className)}>
      {status === 'loading' && (
        <div className="absolute inset-0 bg-white/5 animate-pulse" />
      )}
      <img
        src={src}
        alt={alt}
        className={cn(
          "w-full h-full object-contain transition-opacity duration-300",
          status === 'loaded' ? 'opacity-100' : 'opacity-0'
        )}
        {...props}
      />
    </div>
  );
}
