"use client";

import { useState, useCallback, useRef, useEffect } from "react";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

let toastCounter = 0;

export interface UseToastReturn {
  toasts: Toast[];
  addToast: (message: string, type?: ToastType) => void;
  removeToast: (id: string) => void;
}

export function useToast(): UseToastReturn {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timerMap = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  /** Clean up all timers on unmount. */
  useEffect(() => {
    const timers = timerMap.current;
    return () => {
      timers.forEach((timer) => clearTimeout(timer));
      timers.clear();
    };
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timerMap.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timerMap.current.delete(id);
    }
  }, []);

  const addToast = useCallback(
    (message: string, type: ToastType = "info") => {
      const id = `toast-${++toastCounter}`;
      setToasts((prev) => [...prev.slice(-4), { id, message, type }]);

      const timer = setTimeout(() => {
        timerMap.current.delete(id);
        removeToast(id);
      }, 3500);
      timerMap.current.set(id, timer);
    },
    [removeToast],
  );

  return { toasts, addToast, removeToast };
}
