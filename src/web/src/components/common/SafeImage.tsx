"use client";

import { useState } from "react";
import Image, { type ImageProps } from "next/image";

interface SafeImageProps extends Omit<ImageProps, "onError"> {
  fallback?: React.ReactNode;
}

/** 이미지 로드 실패 시 fallback을 보여주는 래퍼. */
export function SafeImage({ fallback, alt, ...props }: SafeImageProps) {
  const [error, setError] = useState(false);

  if (error) {
    return fallback ? <>{fallback}</> : null;
  }

  return (
    <Image
      alt={alt}
      {...props}
      onError={() => setError(true)}
    />
  );
}
