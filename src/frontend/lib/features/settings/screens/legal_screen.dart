import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/constants/app_constants.dart';
import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 법적 문서 화면 (이용약관 / 개인정보 처리방침).
///
/// [type] 파라미터로 표시할 문서 종류를 결정한다.
class LegalScreen extends StatelessWidget {
  /// [LegalScreen] 생성자.
  ///
  /// [type] — 'terms' (이용약관) 또는 'privacy' (개인정보 처리방침).
  const LegalScreen({super.key, required this.type});

  /// 법적 문서 유형.
  final String type;

  @override
  Widget build(BuildContext context) {
    final isTerms = type == 'terms';
    final title = isTerms ? '이용약관' : '개인정보 처리방침';
    final content = isTerms ? _termsContent : _privacyContent;

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        centerTitle: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${AppConstants.appName} $title',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              '시행일: 2026년 1월 1일',
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textSecondary,
              ),
            ),
            const Divider(height: 32),
            Text(
              content,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textPrimary,
                height: 1.8,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 이용약관 MVP 플레이스홀더.
const String _termsContent = '''
제1조 (목적)
본 약관은 약먹어(이하 "서비스")가 제공하는 약물 상호작용 정보 서비스의 이용 조건 및 절차에 관한 사항을 규정함을 목적으로 합니다.

제2조 (서비스의 내용)
1. 서비스는 의약품 및 영양제 간 상호작용 정보를 제공합니다.
2. 본 서비스는 의학적 진단이나 치료를 대체하지 않으며, 참고 목적으로만 사용해야 합니다.
3. 실제 복약에 대한 결정은 반드시 의사 또는 약사와 상의하시기 바랍니다.

제3조 (면책조항)
1. 서비스에서 제공하는 정보는 공공 데이터에 기반한 참고 정보입니다.
2. 서비스 이용으로 발생하는 모든 결과에 대해 서비스 제공자는 책임을 지지 않습니다.
3. 긴급한 의료 상황 시에는 즉시 의료 전문가에게 연락하시기 바랍니다.

제4조 (개인정보)
1. 서비스는 회원가입을 요구하지 않으며, 최소한의 디바이스 정보만 사용합니다.
2. 복약 정보는 사용자 기기에 우선 저장되며, 서버 전송을 최소화합니다.

제5조 (광고)
1. 서비스는 광고를 포함하며, 광고 수익으로 운영됩니다.
2. 광고 내용은 서비스 제공자의 의견을 반영하지 않습니다.

(MVP 버전 — 정식 출시 시 법률 검토 후 업데이트 예정)
''';

/// 개인정보 처리방침 MVP 플레이스홀더.
const String _privacyContent = '''
1. 수집하는 개인정보 항목
- 디바이스 식별자 (UUID): 복약함 데이터 연동 목적

2. 개인정보의 수집 및 이용 목적
- 사용자 디바이스별 복약함 데이터 관리
- 서비스 이용 통계 분석

3. 개인정보의 보유 및 이용 기간
- 서비스 이용 기간 동안 보유하며, 1년간 미이용 시 자동 삭제됩니다.

4. 건강정보 보호
- 복약 정보는 민감정보로 분류되며, 개인정보보호법에 따라 보호됩니다.
- 복약 정보는 사용자 기기에 우선 저장되며, 서버 전송을 최소화합니다.
- 서버에 저장되는 데이터는 암호화하여 보관합니다.

5. 개인정보의 제3자 제공
- 원칙적으로 사용자의 개인정보를 제3자에게 제공하지 않습니다.

6. 광고 관련
- 서비스 내 광고는 Google AdMob을 통해 제공됩니다.
- 광고 식별자(ADID/IDFA)는 Google 광고 정책에 따라 처리됩니다.

7. 정보주체의 권리
- 사용자는 언제든지 복약함 데이터를 삭제할 수 있습니다.
- 앱 삭제 시 기기에 저장된 모든 데이터가 삭제됩니다.

(MVP 버전 — 정식 출시 시 법률 검토 후 업데이트 예정)
''';
