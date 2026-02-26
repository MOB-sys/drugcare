export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-8 mt-auto">
      <div className="max-w-5xl mx-auto px-4 text-center text-xs text-gray-400 space-y-4">
        {/* 앱 다운로드 */}
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-500">앱으로 더 편리하게</p>
          <div className="flex justify-center gap-4">
            <a
              href="https://apps.apple.com/app/yakmeogeo"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              App Store
            </a>
            <a
              href="https://play.google.com/store/apps/details?id=com.yakmeogeo.app"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              Google Play
            </a>
          </div>
        </div>

        <p>
          약먹어는 의학적 진단이나 치료를 제공하지 않습니다.
          <br />
          제공되는 정보는 참고용이며, 반드시 의사 또는 약사와 상담하세요.
        </p>
        <p>&copy; {new Date().getFullYear()} 약먹어. All rights reserved.</p>
      </div>
    </footer>
  );
}
