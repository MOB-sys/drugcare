interface Window {
  gtag(command: "js", date: Date): void;
  gtag(command: "config", id: string, params?: Record<string, unknown>): void;
  gtag(command: "event", action: string, params?: Record<string, unknown>): void;
  gtag(command: "set", params: Record<string, unknown>): void;
}
