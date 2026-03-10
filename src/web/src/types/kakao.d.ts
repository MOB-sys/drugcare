interface Window {
  Kakao?: {
    isInitialized(): boolean;
    init(appKey: string): void;
    Share: {
      sendDefault(params: Record<string, unknown>): void;
    };
  };
}
