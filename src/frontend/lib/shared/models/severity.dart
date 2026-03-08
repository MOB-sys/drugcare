import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';

/// 상호작용 심각도 등급.
enum Severity {
  /// 위험 — 병용 금기.
  danger,

  /// 경고 — 주의 필요.
  warning,

  /// 주의 — 가벼운 상호작용.
  caution,

  /// 참고 — 정보 제공.
  info;

  /// 심각도에 해당하는 메인 색상.
  Color get color {
    switch (this) {
      case Severity.danger:
        return AppColors.danger;
      case Severity.warning:
        return AppColors.warning;
      case Severity.caution:
        return AppColors.caution;
      case Severity.info:
        return AppColors.info;
    }
  }

  /// 심각도에 해당하는 배경 색상.
  Color get backgroundColor {
    switch (this) {
      case Severity.danger:
        return AppColors.dangerBg;
      case Severity.warning:
        return AppColors.warningBg;
      case Severity.caution:
        return AppColors.cautionBg;
      case Severity.info:
        return AppColors.infoBg;
    }
  }

  /// 심각도에 해당하는 아이콘.
  IconData get icon {
    switch (this) {
      case Severity.danger:
        return Icons.dangerous;
      case Severity.warning:
        return Icons.warning;
      case Severity.caution:
        return Icons.info_outline;
      case Severity.info:
        return Icons.lightbulb_outline;
    }
  }

  /// 심각도 한국어 라벨.
  String get label {
    switch (this) {
      case Severity.danger:
        return '위험';
      case Severity.warning:
        return '경고';
      case Severity.caution:
        return '주의';
      case Severity.info:
        return '참고';
    }
  }

  /// JSON 문자열로 변환한다.
  String toJson() => name;

  /// JSON 문자열에서 [Severity]를 생성한다.
  static Severity fromJson(String value) {
    return Severity.values.firstWhere(
      (e) => e.name == value,
      orElse: () => throw ArgumentError('Unknown Severity: $value'),
    );
  }
}
